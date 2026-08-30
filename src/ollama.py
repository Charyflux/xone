"""Ollama wrapper for X-ONE"""
import httpx
import logging
from typing import AsyncGenerator, Optional
from pathlib import Path

log = logging.getLogger("xone.ollama")


class OllamaClient:
    """Wrapper for Ollama API"""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=timeout, verify=False)
        self.timeout = timeout

    async def health_check(self) -> bool:
        """Check if Ollama is online"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            log.error(f"Ollama health check failed: {e}")
            return False

    async def list_models(self) -> list[str]:
        """List all available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            log.error(f"Failed to list models: {e}")
            return []

    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        num_predict: int = 512,
        system_prompt: Optional[str] = None
    ) -> str:
        """Get single response from model (non-streaming)"""
        full_response = ""
        async for chunk in self.stream(
            model=model,
            messages=messages,
            temperature=temperature,
            num_predict=num_predict,
            system_prompt=system_prompt
        ):
            full_response += chunk
        return full_response

    async def stream(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        num_predict: int = 512,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response from model (token by token)"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = __import__('json').loads(line)
                            if 'message' in data and 'content' in data['message']:
                                yield data['message']['content']
                        except Exception as e:
                            log.error(f"Error parsing response: {e}")
                            continue

        except Exception as e:
            log.error(f"Stream failed: {e}")
            raise

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        num_predict: int = 512,
        system_prompt: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """Generate text using legacy /api/generate endpoint"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature,
                    "num_predict": num_predict,
                }
            }

            if system_prompt:
                payload["system"] = system_prompt

            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = __import__('json').loads(line)
                            if 'response' in data:
                                yield data['response']
                        except Exception:
                            continue

        except Exception as e:
            log.error(f"Generate failed: {e}")
            raise

    async def pull_model(self, model_name: str) -> bool:
        """Pull (download) a model"""
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        try:
                            data = __import__('json').loads(line)
                            status = data.get('status', '')
                            if 'success' in status.lower():
                                log.info(f"Model {model_name} pulled successfully")
                                return True
                        except Exception:
                            continue
            return False
        except Exception as e:
            log.error(f"Failed to pull model: {e}")
            return False

    async def show_model_info(self, model: str) -> Optional[dict]:
        """Get model information"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": model}
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            log.error(f"Failed to get model info: {e}")
            return None

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


def load_system_prompt(prompt_type: str = "base") -> str:
    """Load system prompt from config files"""
    try:
        prompt_file = Path("config/system_prompts") / f"{prompt_type}.txt"
        if prompt_file.exists():
            return prompt_file.read_text()
        log.warning(f"Prompt file not found: {prompt_file}")
        return ""
    except Exception as e:
        log.error(f"Failed to load prompt: {e}")
        return ""


def load_specialized_prompt(vuln_type: str) -> str:
    """Load specialized prompt for vulnerability type"""
    vuln_map = {
        "XSS": "xss",
        "SQL Injection": "sqli",
        "SSRF": "ssrf",
        "SQLi": "sqli",
    }

    prompt_name = vuln_map.get(vuln_type, "base")
    return load_system_prompt(prompt_name)

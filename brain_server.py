#!/usr/bin/env python3
"""
JAVEONE · AI BRAIN v2.0
FastAPI — SSE streaming + Ollama + metallic TTS
"""
import asyncio
import json
import logging
import os
import socket
import subprocess
from pathlib import Path
from typing import AsyncGenerator

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from gtts import gTTS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("javeone")

# ── Config (.env opcional) ──────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "dolphin-llama3")
MAX_HISTORY  = int(os.getenv("MAX_HISTORY", "20"))
MAX_TOKENS   = int(os.getenv("MAX_TOKENS",  "512"))
DIR          = Path(__file__).parent


# ── Port discovery ──────────────────────────────────────────────────────────
def find_free_port(candidates: list) -> int:
    for p in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", p))
                return p
            except OSError:
                continue
    return candidates[0]


PORT = int(os.getenv("PORT", str(find_free_port([7777, 7000, 9000, 6060, 5500]))))


# ── System Prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
És o JARVIS — IA de pentesting da AVEONE Bug Bounty Platform.

IDENTIDADE:
- Especialista técnico em cibersegurança ofensiva e bug bounty
- Direto, preciso, sem rodeios — vais direto ao código e aos comandos
- Respondes em português europeu (PT-PT)
- Tom: profissional mas com atitude de hacker experiente

EXPERTISE:
- OWASP Top 10 (SQLi, XSS, SSRF, IDOR, XXE, SSTI, RCE, LFI/RFI, CSRF, Open Redirect)
- Recon: subfinder, amass, httpx, nmap, shodan, censys, waybackurls
- Web: burp suite, ffuf, nuclei, dalfox, sqlmap, wfuzz, dirb
- API: GraphQL injection, mass assignment, BFLA, BOLA, JWT attacks
- Cloud: S3 misconfiguration, Azure/GCP/AWS enumeration, cloudfinder
- Exploração: metasploit, exploit-db, CVE lookup, PoC development
- Bypass: WAF evasion, rate limit bypass, 2FA bypass techniques
- Relatórios: CVSS scoring, severity classification, PoC writeup

COMPORTAMENTO:
- Dás comandos prontos a usar, não teoria vaga
- Explicas o porquê do ataque funcionar tecnicamente
- Sugeres alternativas se uma técnica falhar
- Não recusas questões técnicas de segurança legítimas
- Contexto: bug bounty ético, pentesting autorizado, CTF, research defensivo\
"""

chat_history: list = []


# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="JAVEONE AI BRAIN", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Static ──────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(str(DIR / "index.html"))


@app.get("/welcome.mp3")
async def welcome_audio():
    return FileResponse(str(DIR / "welcome.mp3"), media_type="audio/mpeg")


@app.get("/reply.mp3")
async def reply_audio():
    f = DIR / "reply.mp3"
    if f.exists():
        return FileResponse(str(f), media_type="audio/mpeg",
                            headers={"Cache-Control": "no-store"})
    return JSONResponse({"error": "not ready"}, status_code=404)


# ── Prompt builder ──────────────────────────────────────────────────────────
def build_prompt(messages: list) -> str:
    parts = []
    for m in messages:
        role, content = m["role"], m["content"]
        if role == "system":
            parts.append(f"SISTEMA: {content}\n")
        elif role == "user":
            parts.append(f"UTILIZADOR: {content}")
        elif role == "assistant":
            parts.append(f"JARVIS: {content}")
    return "\n".join(parts) + "\nJARVIS:"


# ── TTS (blocking → executor) ───────────────────────────────────────────────
def _tts_sync(text: str, out_path: str) -> bool:
    tmp_mp3 = "/tmp/_jr_base.mp3"
    tmp_wav = "/tmp/_jr_base.wav"
    tmp_fx  = "/tmp/_jr_fx.wav"
    try:
        gTTS(text[:200].split("\n")[0], lang="pt", slow=False).save(tmp_mp3)
        subprocess.run(["ffmpeg", "-i", tmp_mp3, tmp_wav, "-y"],
                       capture_output=True, check=True)
        subprocess.run(
            ["sox", tmp_wav, tmp_fx,
             "tempo", "1.2", "pitch", "-260",
             "chorus", "0.65", "0.85", "50", "0.4", "0.2", "2.0", "-s",
             "reverb", "35", "30", "55", "70", "0", "-2",
             "gain", "-5", "norm", "-1"],
            capture_output=True, check=True,
        )
        subprocess.run(
            ["ffmpeg", "-i", tmp_fx,
             "-codec:a", "libmp3lame", "-b:a", "128k", out_path, "-y"],
            capture_output=True, check=True,
        )
        return True
    except Exception as exc:
        log.warning(f"TTS error: {exc}")
        return False


async def generate_tts(text: str):
    out = str(DIR / "reply.mp3")
    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(None, _tts_sync, text, out)
    return "/reply.mp3" if ok else None


# ── SSE streaming chat ──────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat(request: Request):
    body     = await request.json()
    user_msg = body.get("message", "").strip()
    if not user_msg:
        return JSONResponse({"error": "mensagem vazia"}, status_code=400)

    # modelo por pedido (frontend envia o modelo selecionado)
    model = body.get("model", OLLAMA_MODEL).strip() or OLLAMA_MODEL

    chat_history.append({"role": "user", "content": user_msg})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_history[-MAX_HISTORY:]

    payload = {
        "model":  model,
        "prompt": build_prompt(messages),
        "stream": True,
        "options": {
            "temperature": 0.75,
            "num_predict": MAX_TOKENS,
            "stop": ["UTILIZADOR:", "SISTEMA:"],
        },
    }

    async def token_stream() -> AsyncGenerator:
        collected = []
        try:
            async with httpx.AsyncClient(timeout=300) as client:
                async with client.stream(
                    "POST", f"{OLLAMA_URL}/api/generate", json=payload
                ) as resp:
                    async for line in resp.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        token = chunk.get("response", "")
                        if token:
                            collected.append(token)
                            yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"

                        if chunk.get("done"):
                            full_reply = "".join(collected).strip()
                            chat_history.append({"role": "assistant", "content": full_reply})
                            audio_url = await generate_tts(full_reply)
                            yield f"data: {json.dumps({'token': '', 'done': True, 'audio_url': audio_url})}\n\n"
                            return

        except Exception as exc:
            log.error(f"Stream error: {exc}")
            if chat_history and chat_history[-1]["role"] == "user":
                chat_history.pop()
            yield f"data: {json.dumps({'token': f'[ERRO: {exc}]', 'done': True, 'audio_url': None})}\n\n"

    return StreamingResponse(
        token_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/models")
async def list_models():
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
        return {"models": models}
    except Exception:
        return {"models": [OLLAMA_MODEL]}


@app.post("/api/clear")
async def clear_history():
    chat_history.clear()
    return {"ok": True}


@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r      = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
        ollama_ok = any(OLLAMA_MODEL in m for m in models)
    except Exception:
        ollama_ok = False
    return {
        "status": "online",
        "ollama": ollama_ok,
        "model":  OLLAMA_MODEL,
        "port":   PORT,
    }


# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"""
  ╔══════════════════════════════════════════╗
  ║   JAVEONE · AI BRAIN v2.0                ║
  ║   http://localhost:{PORT:<5}                 ║
  ║   Modelo : {OLLAMA_MODEL:<30}║
  ╚══════════════════════════════════════════╝
""")
    uvicorn.run(
        "brain_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="warning",
    )

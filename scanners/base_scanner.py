"""Base scanner class for all AVEONE scanners"""
import asyncio
import httpx
import logging
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from src.models import Finding

log = logging.getLogger("xone.scanners")


class BaseScanner(ABC):
    """Base class for all security scanners"""

    def __init__(
        self,
        xone_url: str = "http://localhost:7777",
        timeout: int = 30
    ):
        self.xone_url = xone_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout, verify=False)
        self.findings: list[Finding] = []

    @property
    @abstractmethod
    def name(self) -> str:
        """Scanner name"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Scanner description"""
        pass

    @abstractmethod
    async def scan(self, target: str, **kwargs) -> list[Finding]:
        """Execute scan and return findings"""
        pass

    async def send_finding(self, finding: Finding) -> bool:
        """Send finding to X-ONE server"""
        try:
            response = await self.client.post(
                f"{self.xone_url}/api/findings",
                json=finding.model_dump(mode='json')
            )
            return response.status_code == 200
        except Exception as e:
            log.error(f"Failed to send finding: {e}")
            return False

    async def send_all_findings(self) -> int:
        """Send all findings to X-ONE and return count"""
        count = 0
        for finding in self.findings:
            if await self.send_finding(finding):
                count += 1
                log.info(f"[{self.name}] Finding sent: {finding.vuln_type}")
        return count

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def create_finding(
        self,
        vuln_type: str,
        url: str,
        payload: str,
        severity: str,
        param: Optional[str] = None,
        context: str = "",
        evidence: Optional[str] = None,
        cvss_score: Optional[float] = None,
        cvss_vector: Optional[str] = None,
    ) -> Finding:
        """Helper to create Finding object"""
        finding = Finding(
            vuln_type=vuln_type,
            url=url,
            payload=payload,
            severity=severity,
            param=param,
            context=context,
            evidence=evidence,
            tool=self.name,
            cvss_score=cvss_score,
            cvss_vector=cvss_vector,
        )
        self.findings.append(finding)
        return finding

    async def health_check(self) -> bool:
        """Check if X-ONE server is online"""
        try:
            response = await self.client.get(f"{self.xone_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    async def chat(self, message: str, model: str = "dolphin-llama3") -> str:
        """Send message to X-ONE and get response"""
        try:
            response = await self.client.post(
                f"{self.xone_url}/api/chat",
                json={"message": message, "model": model}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("content", "")
            return ""
        except Exception as e:
            log.error(f"Chat error: {e}")
            return ""

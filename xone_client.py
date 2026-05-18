"""
X-ONE Client — AVEONE Scanner Integration
==========================================
Importa este módulo em qualquer scanner AVEONE para enviar findings
automaticamente para o X-ONE AI.

Uso básico:
    from xone_client import xone

    xone.finding(
        vuln_type = "XSS Reflected",
        url       = "https://alvo.com/search?q=",
        payload   = "<script>alert(1)</script>",
        severity  = "High",
        param     = "q",
        context   = "Parâmetro refletido sem encode no corpo HTML",
        tool      = "context_xss_scanner.py"
    )

Uso com context manager (auto-envia todos os findings no fim):
    with xone.session("lfi_scanner.py") as s:
        s.add("LFI", url, "../../../../etc/passwd", "High", param="file")
        s.add("LFI", url2, "php://filter/...", "Critical", param="path")
    # envia tudo automaticamente ao sair do with
"""
import json
import logging
import threading
from typing import Optional

try:
    import requests
    _HAS_REQUESTS = True
except ImportError:
    _HAS_REQUESTS = False

try:
    import urllib.request
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False

log = logging.getLogger("xone_client")

XONE_URL     = "http://localhost:7777"
XONE_TIMEOUT = 3


def _post(endpoint: str, data: dict) -> bool:
    url = XONE_URL.rstrip("/") + endpoint
    body = json.dumps(data).encode("utf-8")

    if _HAS_REQUESTS:
        try:
            requests.post(url, json=data, timeout=XONE_TIMEOUT)
            return True
        except Exception:
            pass

    if _HAS_URLLIB:
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            urllib.request.urlopen(req, timeout=XONE_TIMEOUT)
            return True
        except Exception:
            pass

    return False


class XOneClient:
    """Cliente principal para enviar findings ao X-ONE."""

    def finding(
        self,
        vuln_type: str,
        url:       str       = "",
        payload:   str       = "",
        severity:  str       = "Medium",
        param:     str       = "",
        context:   str       = "",
        evidence:  str       = "",
        tool:      str       = "AVEONE",
        async_send: bool     = True,
    ) -> None:
        """
        Envia um finding para o X-ONE.

        Args:
            vuln_type : Tipo de vulnerabilidade (ex: "XSS Reflected", "SQLi", "LFI")
            url       : URL completo onde foi encontrado
            payload   : Payload que confirmou a vulnerabilidade
            severity  : "Critical" | "High" | "Medium" | "Low" | "Info"
            param     : Parâmetro vulnerável (ex: "q", "id", "file")
            context   : Contexto adicional (ex: "refletido no atributo href")
            evidence  : Evidência / resposta do servidor
            tool      : Nome do scanner (ex: "lfi_scanner.py")
            async_send: Se True, envia em background thread (não bloqueia o scanner)
        """
        data = {
            "vuln_type": vuln_type,
            "url":       url,
            "payload":   payload,
            "severity":  severity,
            "param":     param,
            "context":   context,
            "evidence":  evidence,
            "tool":      tool,
        }

        if async_send:
            t = threading.Thread(target=_post, args=("/api/findings", data), daemon=True)
            t.start()
        else:
            ok = _post("/api/findings", data)
            if not ok:
                log.debug("X-ONE não disponível — finding não enviado")

    def session(self, tool: str = "AVEONE") -> "XOneSession":
        """
        Context manager para acumular findings e enviar todos no fim.

        Exemplo:
            with xone.session("jwt_attacker.py") as s:
                s.add("JWT alg:none", url, payload, "Critical")
                s.add("JWT HS256 brute", url, weak_key, "High")
        """
        return XOneSession(tool)

    def is_online(self) -> bool:
        """Verifica se o X-ONE está a correr."""
        try:
            if _HAS_REQUESTS:
                r = requests.get(XONE_URL + "/health", timeout=2)
                return r.status_code == 200
            req = urllib.request.Request(XONE_URL + "/health")
            urllib.request.urlopen(req, timeout=2)
            return True
        except Exception:
            return False


class XOneSession:
    """Acumula findings e envia-os todos ao sair do context manager."""

    def __init__(self, tool: str):
        self.tool     = tool
        self._pending = []

    def add(
        self,
        vuln_type: str,
        url:       str  = "",
        payload:   str  = "",
        severity:  str  = "Medium",
        param:     str  = "",
        context:   str  = "",
        evidence:  str  = "",
    ) -> None:
        """Adiciona um finding à sessão (não envia ainda)."""
        self._pending.append({
            "vuln_type": vuln_type,
            "url":       url,
            "payload":   payload,
            "severity":  severity,
            "param":     param,
            "context":   context,
            "evidence":  evidence,
            "tool":      self.tool,
        })

    def __enter__(self):
        return self

    def __exit__(self, *_):
        for data in self._pending:
            _post("/api/findings", data)
        if self._pending:
            log.debug(f"X-ONE: {len(self._pending)} findings enviados de {self.tool}")


# Instância global para uso direto
xone = XOneClient()


# ── Exemplos de integração por scanner ──────────────────────────────────────
#
# context_xss_scanner.py:
#   from xone_client import xone
#   xone.finding("XSS Reflected", url, payload, "High", param=param,
#                context=f"Contexto: {ctx}", tool="context_xss_scanner.py")
#
# lfi_scanner.py:
#   from xone_client import xone
#   xone.finding("LFI", url, payload, "High", param=param,
#                evidence=response[:200], tool="lfi_scanner.py")
#
# jwt_attacker.py:
#   from xone_client import xone
#   xone.finding("JWT alg:none bypass", url, forged_token, "Critical",
#                context="Token aceite sem verificação de assinatura",
#                tool="jwt_attacker.py")
#
# ssti_scanner.py:
#   from xone_client import xone
#   xone.finding("SSTI Jinja2 RCE", url, payload, "Critical",
#                param=param, evidence=f"{{{{7*7}}}} retornou {result}",
#                tool="ssti_scanner.py")
#
# sqlmap / sqli manual:
#   from xone_client import xone
#   xone.finding("SQL Injection", url, payload, "Critical",
#                param=param, evidence=error_msg, tool="sqli_scanner.py")

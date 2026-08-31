# X-ONE v4.0 — QuickStart 🚀

**Acesso rápido a X-ONE — 3 opções, 1 minuto**

---

## 🟢 Opção 1: Modo Local (Recomendado)

A forma mais rápida para começar — nenhuma dependência externa.

### ⚡ Execução Rápida
```bash
bash setup.sh
```

**O que faz:**
- ✅ Verifica Python 3
- ✅ Cria `venv` (ambiente virtual)
- ✅ Instala dependências
- ✅ Configura `.env`
- ✅ Abre automaticamente no browser: http://localhost:7777

### 📍 Acesso Manual
Se preferires controlar tudo:
```bash
# 1. Ativa ambiente virtual
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate      # Windows

# 2. Instala dependências
pip install -r requirements.txt

# 3. Inicia servidor
python -m src.server
```

**URL:** http://localhost:7777

---

## 🐳 Opção 2: Docker (Isolado)

Se tens Docker instalado — uma única linha:

```bash
docker-compose -f docker/docker-compose.yml up
```

**O que faz:**
- ✅ Inicia Ollama (LLM local)
- ✅ Inicia X-ONE
- ✅ Ambos conectados automaticamente
- ✅ Volumes persistentes para dados

**URL:** http://localhost:7777

### Requisitos:
- [Docker](https://docs.docker.com/install/)
- ~8GB RAM (Ollama + X-ONE)
- Primeiro start pode levar 2-3 min (download do modelo)

---

## ☁️ Opção 3: Deploy na Cloud

Para acesso público (Heroku, Render, Railway, etc.):

### Render.com (Recomendado — Gratuito)

1. **Faz fork do repositório** → https://github.com/Charyflux/xone

2. **Cria novo Web Service:**
   - Connect GitHub repo
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m src.server`
   - Add Environment Variable:
     ```
     OLLAMA_URL=https://ollama-api.example.com
     PORT=10000
     ```

3. **Deploy** → URL pública gerada automaticamente

### Heroku (Alternativa)

```bash
heroku login
git push heroku main
heroku open
```

---

## 🎮 Primeira Execução

### 1️⃣ Abre http://localhost:7777

```
╔════════════════════════════════════════════╗
║              X-ONE v4.0                    ║
║   ◈ AGUARDANDO AUTORIZAÇÃO ◈              ║
│                                            │
│         [▶ INICIAR SISTEMA]               │
╚════════════════════════════════════════════╝
```

### 2️⃣ Clica em "INICIAR SISTEMA"

Interface HUD ativa:
- Dashboard neural com visualizações em tempo real
- Chat com IA pentesting
- Findings panel (vulnerabilidades detectadas)
- Smart Fuzz (IA sugere payloads)
- AVEONE integration (scanners avançados)

### 3️⃣ Seleciona o Modelo

Top-left corner:
- **☠ SEM FILTROS** (dolphin-llama3) — Respostas diretas, sem suavizações
- **⚡ MODO RÁPIDO** (llama3.2) — Mais rápido, contexto menor

### 4️⃣ Começa a Usar

```
X-ONE://> O que é uma XSS Reflected?
```

Exemplos de perguntas:
- "Quais payloads XSS bypássam Cloudflare WAF?"
- "Como fazer SQLi blind em MySQL?"
- "Explica o ataque SSRF em AWS"
- "Gera um payload RCE em template injection"

---

## 🔧 Configuração (.env)

Edita `.env` para customizar:

```bash
# Servidor
PORT=7777
OLLAMA_URL=http://localhost:11434

# Modelo IA
OLLAMA_MODEL=dolphin-llama3  # ou llama3.2, qwen2.5-coder:7b, etc

# Performance
MAX_HISTORY=20       # Mensagens mantidas em contexto
MAX_TOKENS=512       # Tokens por resposta
OLLAMA_NUM_GPU=1     # GPU layers (0=CPU)

# Presets (descomenta um)
# Fast:    MAX_HISTORY=10 MAX_TOKENS=300 OLLAMA_MODEL=llama3.2:1b
# Balanced: MAX_HISTORY=20 MAX_TOKENS=512 OLLAMA_MODEL=llama3.2 (default)
# Quality:  MAX_HISTORY=30 MAX_TOKENS=1024 OLLAMA_MODEL=dolphin-llama3
```

---

## ⚠️ Troubleshooting

### "Connection refused" em localhost:7777
```bash
# Verifica se servidor está rodando
lsof -i :7777

# Mata processo anterior se necessário
kill -9 <PID>

# Re-inicia
python -m src.server
```

### Ollama não encontrado
```bash
# Instala Ollama (macOS/Linux)
curl https://ollama.ai/install.sh | sh

# Inicia Ollama em background
ollama serve

# Em outra aba, carrega modelo
ollama pull dolphin-llama3
```

### Sem GPU (só CPU)
Edita `.env`:
```
OLLAMA_NUM_GPU=0      # Força CPU
OLLAMA_MODEL=llama3.2:1b  # Modelo menor
```

### ModuleNotFoundError
```bash
# Reativa venv
source venv/bin/activate

# Reinstala dependências
pip install -r requirements.txt --force-reinstall
```

---

## 📚 Recursos

| Link | Descrição |
|------|-----------|
| [docs/API.md](docs/API.md) | 10 endpoints REST documentados |
| [docs/ADVANCED_CONFIG.md](docs/ADVANCED_CONFIG.md) | GPU setup, tuning, troubleshooting |
| [docs/EXAMPLES/](docs/EXAMPLES/) | Workflows completos (XSS, SQLi, JWT) |
| [CHANGELOG.md](CHANGELOG.md) | Release notes v4.0 + roadmap |

---

## 🚀 Status

```
X-ONE v4.0 — Neural Network Pentesting
├── Server: FastAPI + Ollama ✅
├── Interface: Futuristic HUD + Chat ✅
├── Scanners: JWT, XSS, SQLi, LFI, SSTI ✅
├── AVEONE: Integração de scanners ✅
├── Docker: Production-ready ✅
└── CI/CD: GitHub Actions (lint + tests) ✅
```

---

## 💡 Tips Pro

- **Ctrl+C no terminal** para parar servidor (graceful shutdown)
- **Limpa história:** Usa `/clear` ou botão CLR no chat
- **Exporta findings:** Botão "REPORT" no findings panel
- **Múltiplas abas:** Cada aba = nova conversa (histórico isolado)
- **GPU acelerada:** Melhor performance com CUDA/ROCm/Metal

---

**Pronto para análises de segurança? Executa `bash setup.sh` e começa! 🔥**

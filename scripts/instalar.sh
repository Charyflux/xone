#!/usr/bin/env bash
# ============================================================
#  JAVEONE · AI BRAIN — Instalador automático (Linux / macOS)
# ============================================================
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'

banner() {
  echo -e "${CYAN}"
  echo "  ╔══════════════════════════════════════════╗"
  echo "  ║   JAVEONE · AI BRAIN — Instalador        ║"
  echo "  ║   github.com/Charyflux/JaveOne           ║"
  echo "  ╚══════════════════════════════════════════╝"
  echo -e "${NC}"
}

step() { echo -e "\n${BOLD}${CYAN}[${1}/${TOTAL}]${NC} ${BOLD}${2}${NC}"; }
ok()   { echo -e "  ${GREEN}✓${NC} ${1}"; }
warn() { echo -e "  ${YELLOW}⚠${NC}  ${1}"; }
fail() { echo -e "  ${RED}✗ ERRO: ${1}${NC}"; exit 1; }

TOTAL=6
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

banner

# ── 1. Detectar OS ──────────────────────────────────────────
step 1 "Detectar sistema operativo"
OS="$(uname -s)"
case "$OS" in
  Linux*)  PLATFORM="linux" ;;
  Darwin*) PLATFORM="mac" ;;
  *)       fail "Sistema não suportado: $OS" ;;
esac
ok "Plataforma: $PLATFORM"

# ── 2. Dependências do sistema ──────────────────────────────
step 2 "Instalar dependências do sistema (ffmpeg, sox, python3)"

if [ "$PLATFORM" = "linux" ]; then
  if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y ffmpeg sox python3 python3-pip python3-venv curl &>/dev/null
    ok "apt: ffmpeg sox python3 instalados"
  elif command -v dnf &>/dev/null; then
    sudo dnf install -y ffmpeg sox python3 python3-pip curl &>/dev/null
    ok "dnf: ffmpeg sox python3 instalados"
  else
    warn "Gestor de pacotes não reconhecido. Instala manualmente: ffmpeg sox python3"
  fi
elif [ "$PLATFORM" = "mac" ]; then
  if ! command -v brew &>/dev/null; then
    fail "Homebrew não encontrado. Instala em https://brew.sh"
  fi
  brew install ffmpeg sox python3 &>/dev/null
  ok "brew: ffmpeg sox python3 instalados"
fi

# ── 3. Instalar Ollama ──────────────────────────────────────
step 3 "Instalar Ollama"

if command -v ollama &>/dev/null; then
  ok "Ollama já instalado: $(ollama --version 2>/dev/null || echo 'versão desconhecida')"
else
  echo "  Descarregando Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
  ok "Ollama instalado"
fi

# Iniciar Ollama em background se não estiver a correr
if ! pgrep -x ollama &>/dev/null; then
  echo "  Iniciando serviço Ollama..."
  ollama serve &>/dev/null &
  sleep 3
  ok "Ollama iniciado em background"
else
  ok "Ollama já está em execução"
fi

# ── 4. Descarregar modelo ───────────────────────────────────
step 4 "Descarregar modelo dolphin-llama3 (4.7 GB — pode demorar)"

MODEL="${OLLAMA_MODEL:-dolphin-llama3}"
if ollama list 2>/dev/null | grep -q "$MODEL"; then
  ok "Modelo $MODEL já descarregado"
else
  echo "  Descarregando $MODEL..."
  ollama pull "$MODEL"
  ok "Modelo $MODEL pronto"
fi

# ── 5. Ambiente Python ──────────────────────────────────────
step 5 "Configurar ambiente Python"

cd "$DIR"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
  ok "Virtualenv criado em .venv/"
fi

source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
ok "Dependências Python instaladas"

# Copiar configuração exemplo se não existir .env
if [ ! -f ".env" ]; then
  cp .env.example .env
  ok ".env criado a partir de .env.example"
fi

# ── 6. Gerar voz de boas-vindas ─────────────────────────────
step 6 "Gerar voz metalica de boas-vindas"

if [ -f "welcome.mp3" ]; then
  ok "welcome.mp3 já existe — a saltar regeneração"
else
  python3 gerar_voz.py && ok "welcome.mp3 gerado" || warn "Falha ao gerar voz (ffmpeg/sox necessários)"
fi

# ── Sumário ─────────────────────────────────────────────────
echo -e "\n${GREEN}${BOLD}══════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  JAVEONE instalado com sucesso!${NC}"
echo -e "${GREEN}${BOLD}══════════════════════════════════════════${NC}"
echo ""
echo -e "  Para iniciar:  ${CYAN}./scripts/start.sh${NC}"
echo -e "  Browser:       ${CYAN}http://localhost:7777${NC}"
echo ""

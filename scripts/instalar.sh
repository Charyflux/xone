#!/usr/bin/env bash
# ============================================================
#  JAVEONE · AI BRAIN v3.0 — Instalador automático
#  Linux / macOS
#  Documentação: https://github.com/Charyflux/JaveOne
# ============================================================
set -e

# ── Cores ────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

TOTAL=7
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

banner() {
  echo -e "${CYAN}"
  echo "  ╔══════════════════════════════════════════════╗"
  echo "  ║   JAVEONE · AI BRAIN v3.0                    ║"
  echo "  ║   Instalador automático — Linux / macOS      ║"
  echo "  ║   github.com/Charyflux/JaveOne               ║"
  echo "  ╚══════════════════════════════════════════════╝"
  echo -e "${NC}"
}

step() {
  echo ""
  echo -e "${BOLD}${CYAN}━━━ [${1}/${TOTAL}] ${2} ━━━${NC}"
}
ok()   { echo -e "  ${GREEN}✓${NC}  ${1}"; }
warn() { echo -e "  ${YELLOW}⚠${NC}   ${1}"; }
info() { echo -e "  ${DIM}→  ${1}${NC}"; }
fail() {
  echo ""
  echo -e "  ${RED}✗ ERRO: ${1}${NC}"
  echo -e "  ${DIM}Consulta a documentação: https://github.com/Charyflux/JaveOne#-resolução-de-problemas${NC}"
  exit 1
}

banner

# ── Pré-verificações ─────────────────────────────────────────
echo -e "${DIM}  Verificando pré-requisitos...${NC}"
[[ "${EUID}" -eq 0 ]] && warn "A correr como root. Recomendado correr como utilizador normal."

# ── 1. Detectar OS ───────────────────────────────────────────
step 1 "Detectar sistema operativo"

OS="$(uname -s)"
case "$OS" in
  Linux*)
    PLATFORM="linux"
    if command -v apt-get &>/dev/null; then PKG="apt"
    elif command -v dnf &>/dev/null;     then PKG="dnf"
    elif command -v pacman &>/dev/null;  then PKG="pacman"
    else PKG="unknown"; fi
    ok "Linux detectado (gestor: ${PKG})"
    ;;
  Darwin*)
    PLATFORM="mac"
    command -v brew &>/dev/null || fail "Homebrew não encontrado. Instala em: https://brew.sh"
    ok "macOS detectado"
    ;;
  *)
    fail "Sistema operativo não suportado: $OS. Usa Linux ou macOS."
    ;;
esac

# ── 2. Dependências do sistema ───────────────────────────────
step 2 "Instalar dependências: Python 3, ffmpeg, sox, curl"

install_pkg() {
  case "$PKG" in
    apt)    sudo apt-get update -qq && sudo apt-get install -y "$@" &>/dev/null ;;
    dnf)    sudo dnf install -y "$@" &>/dev/null ;;
    pacman) sudo pacman -Sy --noconfirm "$@" &>/dev/null ;;
    *)      warn "Instala manualmente: $*" ;;
  esac
}

if [ "$PLATFORM" = "linux" ]; then
  PKGS=()
  command -v python3  &>/dev/null || PKGS+=(python3 python3-pip python3-venv)
  command -v ffmpeg   &>/dev/null || PKGS+=(ffmpeg)
  command -v sox      &>/dev/null || PKGS+=(sox)
  command -v curl     &>/dev/null || PKGS+=(curl)
  command -v git      &>/dev/null || PKGS+=(git)

  if [ ${#PKGS[@]} -gt 0 ]; then
    info "Instalando: ${PKGS[*]}"
    install_pkg "${PKGS[@]}"
  fi
elif [ "$PLATFORM" = "mac" ]; then
  command -v python3 &>/dev/null || brew install python3
  command -v ffmpeg  &>/dev/null || brew install ffmpeg
  command -v sox     &>/dev/null || brew install sox
fi

# Verificações finais
command -v python3 &>/dev/null || fail "Python 3 não instalado. Instala manualmente: https://python.org"
command -v ffmpeg  &>/dev/null || fail "ffmpeg não instalado. Usa: sudo apt install ffmpeg"
command -v sox     &>/dev/null || fail "sox não instalado. Usa: sudo apt install sox"

PYVER="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
ok "Python ${PYVER} ✓"
ok "ffmpeg $(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}') ✓"
ok "sox $(sox --version 2>/dev/null | awk '{print $NF}') ✓"

# ── 3. Instalar Ollama ───────────────────────────────────────
step 3 "Instalar Ollama (gestor de modelos LLM locais)"

if command -v ollama &>/dev/null; then
  ok "Ollama já instalado: $(ollama --version 2>/dev/null | head -1)"
else
  info "Descarregando e instalando Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
  ok "Ollama instalado"
fi

# Iniciar Ollama
if pgrep -x "ollama" &>/dev/null; then
  ok "Ollama já está em execução"
else
  info "Iniciando Ollama em background..."
  if command -v systemctl &>/dev/null && systemctl list-units --type=service | grep -q ollama; then
    sudo systemctl start ollama &>/dev/null || true
  else
    nohup ollama serve &>/dev/null &
  fi
  sleep 4
  pgrep -x "ollama" &>/dev/null && ok "Ollama iniciado" || warn "Ollama pode não ter iniciado. Corre 'ollama serve' manualmente."
fi

# ── 4. Descarregar modelos ───────────────────────────────────
step 4 "Descarregar modelos de IA"

MAIN_MODEL="${OLLAMA_MODEL:-dolphin-llama3}"

if ollama list 2>/dev/null | grep -q "^${MAIN_MODEL}"; then
  ok "Modelo ${MAIN_MODEL} já existe"
else
  echo ""
  echo -e "  ${YELLOW}A descarregar ${MAIN_MODEL} (~4.7 GB)${NC}"
  echo -e "  ${DIM}Pode demorar vários minutos dependendo da velocidade da internet.${NC}"
  echo ""
  ollama pull "${MAIN_MODEL}" || fail "Falha ao descarregar ${MAIN_MODEL}. Verifica a ligação à internet."
  ok "Modelo ${MAIN_MODEL} pronto"
fi

# Modelo rápido (opcional)
if ! ollama list 2>/dev/null | grep -q "^llama3.2:"; then
  echo ""
  read -r -p "  Descarregar também llama3.2 (2 GB, mais rápido em CPU)? [s/N] " FAST
  if [[ "$FAST" =~ ^[sS]$ ]]; then
    ollama pull llama3.2 && ok "llama3.2 pronto" || warn "Falha ao descarregar llama3.2 (opcional)"
  fi
fi

# ── 5. Ambiente Python ───────────────────────────────────────
step 5 "Configurar ambiente Python virtual"

cd "$DIR"

if [ ! -d ".venv" ]; then
  info "Criando virtualenv em .venv/"
  python3 -m venv .venv || fail "Falha ao criar virtualenv. Verifica se python3-venv está instalado."
  ok "Virtualenv criado"
else
  ok "Virtualenv já existe"
fi

info "Ativando ambiente e instalando dependências..."
# shellcheck source=/dev/null
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q || fail "Falha ao instalar dependências Python."
ok "Dependências instaladas (fastapi, uvicorn, httpx, gtts, python-dotenv)"

# ── 6. Configuração ─────────────────────────────────────────
step 6 "Configuração do JAVEONE"

if [ ! -f ".env" ]; then
  cp .env.example .env
  ok ".env criado a partir de .env.example"
  info "Podes editar .env para mudar a porta, modelo ou outros parâmetros"
else
  ok ".env já existe — configuração preservada"
fi

# ── 7. Voz de boas-vindas ────────────────────────────────────
step 7 "Gerar voz metálica de boas-vindas"

if [ -f "welcome.mp3" ]; then
  ok "welcome.mp3 já existe — a saltar regeneração"
else
  info "Gerando voz com gTTS + sox (efeitos metálicos)..."
  python3 gerar_voz.py && ok "welcome.mp3 gerado" || warn "Falha ao gerar voz (ffmpeg/sox em falta?)"
fi

# ── Sumário final ────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}"
echo "  ╔══════════════════════════════════════════════╗"
echo "  ║   ✓  JAVEONE instalado com sucesso!          ║"
echo "  ╚══════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "  ${BOLD}Para iniciar:${NC}"
echo -e "    ${CYAN}./scripts/start.sh${NC}"
echo ""
echo -e "  ${BOLD}Abre no browser:${NC}"
echo -e "    ${CYAN}http://localhost:7777${NC}"
echo ""
echo -e "  ${DIM}Documentação completa: https://github.com/Charyflux/JaveOne${NC}"
echo ""

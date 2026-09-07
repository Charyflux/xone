#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  X-ONE — Instalador (Linux / macOS)
# ═══════════════════════════════════════════════════════════
set -e
cd "$(dirname "$0")"

echo ""
echo "  ☠  X-ONE — Instalação"
echo "  ────────────────────────────────────────────"

# 1) Ollama (motor do modelo local)
if ! command -v ollama >/dev/null 2>&1; then
  echo "  📦  Instalando Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "  ✅  Ollama já instalado."
fi

# 2) Modelo SEM FILTRO (lê do .env se existir, senão usa o 3b)
MODEL="$(grep -E '^OLLAMA_MODEL=' .env 2>/dev/null | cut -d= -f2)"
MODEL="${MODEL:-huihui_ai/qwen2.5-abliterate:3b}"
echo "  🧠  Baixando o modelo sem filtro: $MODEL  (~2 GB)..."
ollama pull "$MODEL"

# 3) Dependências Python (com fallback pro Kali/Debian — PEP 668)
echo "  🐍  Instalando dependências Python..."
python3 -m pip install --upgrade pip >/dev/null 2>&1 || true
python3 -m pip install -r requirements.txt \
  || python3 -m pip install --break-system-packages -r requirements.txt \
  || python3 -m pip install --user --break-system-packages -r requirements.txt

# 4) Config
[ -f .env ] || { cp .env.example .env; echo "  ⚙️   .env criado a partir do exemplo."; }

echo "  ────────────────────────────────────────────"
echo "  ✅  Pronto!  Rode:  ./start.sh"
echo "      Depois abra:   http://localhost:7777"
echo ""

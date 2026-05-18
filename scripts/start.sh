#!/usr/bin/env bash
# JAVEONE · AI BRAIN — Iniciar servidor
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

# Activar venv se existir
if [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
fi

# Garantir Ollama está a correr
if ! pgrep -x ollama &>/dev/null; then
  echo "[*] Iniciando Ollama..."
  ollama serve &>/dev/null &
  sleep 3
fi

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   JAVEONE · AI BRAIN v2.0                ║"
echo "  ║   http://localhost:7777                  ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

python3 brain_server.py

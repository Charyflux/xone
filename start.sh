#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  X-ONE — Iniciar (Linux / macOS)
# ═══════════════════════════════════════════════════════════
cd "$(dirname "$0")"

# garante o Ollama rodando
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
  echo "  🔌  Subindo o Ollama..."
  (ollama serve >/dev/null 2>&1 &)
  sleep 3
fi

echo ""
echo "  ☠  X-ONE ativo em  →  http://localhost:7777"
echo "  (Ctrl+C para parar)"
echo ""
python3 brain_server.py

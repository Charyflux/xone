#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# X-ONE QUICKSTART — Setup Automático
# ═══════════════════════════════════════════════════════════════

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║         X-ONE v4.0 — NEURAL NETWORK PENTESTING            ║"
echo "║              Setup Automático & Launch                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────────────────────
# 1. Verificar Python
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[1/5] Verificando Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não instalado. Por favor instala:${NC}"
    echo "   macOS: brew install python3"
    echo "   Ubuntu/Debian: sudo apt install python3 python3-pip"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} encontrado${NC}"
echo ""

# ─────────────────────────────────────────────────────────────
# 2. Criar venv se não existir
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[2/5] Configurando ambiente virtual...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ venv criado${NC}"
else
    echo -e "${GREEN}✅ venv já existe${NC}"
fi
echo ""

# ─────────────────────────────────────────────────────────────
# 3. Ativar venv & Instalar requirements
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[3/5] Instalando dependências...${NC}"
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependências instaladas${NC}"
echo ""

# ─────────────────────────────────────────────────────────────
# 4. Copiar .env se não existir
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[4/5] Verificando configuração...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env criado (usa configuração default)${NC}"
else
    echo -e "${GREEN}✅ .env já existe${NC}"
fi
echo ""

# ─────────────────────────────────────────────────────────────
# 5. Iniciar Servidor
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[5/5] Iniciando X-ONE...${NC}"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🚀 X-ONE está online em:${NC}"
echo -e "${CYAN}   http://localhost:7777${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════${NC}"
echo ""
echo "💡 Dicas:"
echo "   • Abre http://localhost:7777 no teu browser"
echo "   • Clica em 'INICIAR SISTEMA' na tela de boas-vindas"
echo "   • Usa 'SEM FILTROS' (dolphin-llama3) para análises sem restrições"
echo "   • Integra com AVEONE (botão top-right)"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════${NC}"
echo ""

# Se estamos em macOS ou Linux com xdg-open, abre automaticamente
if command -v open &> /dev/null; then
    # macOS
    sleep 2
    open "http://localhost:7777"
elif command -v xdg-open &> /dev/null; then
    # Linux
    sleep 2
    xdg-open "http://localhost:7777"
fi

# Inicia o servidor
python -m src.server

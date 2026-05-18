@echo off
:: ============================================================
::  JAVEONE · AI BRAIN — Instalador Windows (PowerShell)
:: ============================================================
:: Requer: PowerShell 5+, Python 3.10+, Ollama para Windows

echo.
echo   ╔══════════════════════════════════════════╗
echo   ║   JAVEONE · AI BRAIN — Instalador        ║
echo   ║   Windows Edition                        ║
echo   ╚══════════════════════════════════════════╝
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python 3 nao encontrado.
    echo        Instala em: https://python.org/downloads
    pause & exit /b 1
)

:: Verificar Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [*] Ollama nao encontrado.
    echo     Descarrega em: https://ollama.com/download/windows
    echo     Instala e volta a correr este script.
    pause & exit /b 1
)

:: Iniciar Ollama
echo [1/4] Iniciando Ollama...
start /b ollama serve
timeout /t 3 /nobreak >nul

:: Descarregar modelo
echo [2/4] Descarregando modelo dolphin-llama3 ^(4.7 GB^)...
ollama pull dolphin-llama3

:: Criar venv Python
echo [3/4] Configurando ambiente Python...
python -m venv .venv
call .venv\Scripts\activate.bat
pip install --upgrade pip -q
pip install -r requirements.txt -q

:: Copiar .env
if not exist .env (
    copy .env.example .env
    echo     .env criado
)

:: Gerar voz
echo [4/4] Gerando voz de boas-vindas...
if not exist welcome.mp3 (
    python gerar_voz.py
)

echo.
echo   Instalacao concluida!
echo   Para iniciar: scripts\start.bat
echo   Browser: http://localhost:7777
echo.
pause

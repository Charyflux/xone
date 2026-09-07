@echo off
REM ═══════════════════════════════════════════════════════════
REM  X-ONE — Instalador (Windows)
REM ═══════════════════════════════════════════════════════════
cd /d "%~dp0"
echo.
echo   [X-ONE] Instalacao
echo   ---------------------------------------------

REM 1) Ollama
where ollama >nul 2>&1
if errorlevel 1 (
  echo   [!] Ollama nao encontrado.
  echo       Baixe e instale o Ollama para Windows em:  https://ollama.com/download
  echo       Depois rode este install.bat de novo.
  pause
  exit /b 1
) else (
  echo   [ok] Ollama instalado.
)

REM 2) Modelo sem filtro
echo   [..] Baixando o modelo sem filtro (huihui_ai/qwen2.5-abliterate:3b, ~2 GB)...
ollama pull huihui_ai/qwen2.5-abliterate:3b

REM 3) Dependencias Python
echo   [..] Instalando dependencias Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM 4) Config
if not exist ".env" copy ".env.example" ".env" >nul

echo   ---------------------------------------------
echo   [ok] Pronto!  Rode:  start.bat
echo        Depois abra:    http://localhost:7777
pause

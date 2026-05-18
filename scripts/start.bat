@echo off
:: JAVEONE · AI BRAIN — Iniciar (Windows)

cd /d "%~dp0.."

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

echo Iniciando Ollama...
start /b ollama serve
timeout /t 3 /nobreak >nul

echo.
echo   JAVEONE · AI BRAIN v2.0
echo   http://localhost:7777
echo.

python brain_server.py
pause

@echo off
REM ═══════════════════════════════════════════════════════════
REM  X-ONE — Iniciar (Windows)
REM ═══════════════════════════════════════════════════════════
cd /d "%~dp0"
echo.
echo   [X-ONE] ativo em  ->  http://localhost:7777
echo   (feche esta janela para parar)
echo.
python brain_server.py
pause

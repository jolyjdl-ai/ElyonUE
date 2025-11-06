@echo off
REM =====================================================
REM ÉlyonEU Desktop Premium - Lanceur Rapide (version simple)
REM =====================================================

REM Obtenir le répertoire racine
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
cd /d "%ROOT_DIR%"

REM Lancer directement l'app (l'API doit tourner séparément)
python app\launch_premium.py

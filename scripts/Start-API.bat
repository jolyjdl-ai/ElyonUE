@echo off
REM =====================================================
REM ÉlyonEU API - Lanceur (version API seule)
REM =====================================================

setlocal enabledelayedexpansion

echo.
echo [API] === ÉlyonEU API Server ===
echo.

REM Obtenir le répertoire racine
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
cd /d "%ROOT_DIR%"

echo [API] Répertoire: %ROOT_DIR%

REM Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installé ou pas dans le PATH
    echo.
    pause
    exit /b 1
)

REM Lancer l'API
echo [API] Lancement de l'API FastAPI sur http://127.0.0.1:8000
echo [API] Documentation: http://127.0.0.1:8000/docs
echo.

python -m uvicorn api.elyon_api:app --host 127.0.0.1 --port 8000 --reload

echo.
pause

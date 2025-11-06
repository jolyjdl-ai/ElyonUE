@echo off
REM =====================================================
REM ÉlyonEU Desktop Premium - Lanceur Windows
REM =====================================================

setlocal enabledelayedexpansion

echo.
echo [launcher] === ÉlyonEU Desktop Premium ===
echo [launcher] Démarrage de l'application...
echo.

REM Obtenir le répertoire racine (parent du script)
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."
cd /d "%ROOT_DIR%"

echo [launcher] Répertoire: %ROOT_DIR%

REM Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python n'est pas installé ou pas dans le PATH
    echo.
    pause
    exit /b 1
)

REM Vérifier si l'API tourne déjà
echo [launcher] Vérification de l'API...
timeout /t 1 /nobreak >nul

REM Lancer l'API en arrière-plan si pas déjà lancée
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "python.exe" >nul
if errorlevel 1 (
    echo [launcher] Démarrage de l'API FastAPI...
    start "ÉlyonEU API" python -m uvicorn api.elyon_api:app --host 127.0.0.1 --port 8000
    timeout /t 3 /nobreak >nul
) else (
    echo [launcher] ✓ API déjà en cours d'exécution
)

REM Lancer l'application Premium
echo [launcher] Lancement de l'application Premium...
echo.

python app\launch_premium.py

if errorlevel 1 (
    echo.
    echo [ERROR] Une erreur s'est produite
    pause
    exit /b 1
)

echo.
echo [launcher] Fermeture.
exit /b 0

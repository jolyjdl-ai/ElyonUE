@echo off
REM Lanceur ÉlyonEU Desktop Premium - Windows Batch
setlocal enabledelayedexpansion

echo ╔════════════════════════════════════════╗
echo ║  ÉlyonEU - Application Desktop Premium ║
echo ╚════════════════════════════════════════╝

cd /d "%~dp0"

REM Vérifier Python
where python >nul 2>nul
if errorlevel 1 (
    echo ✗ Python non trouvé dans PATH
    echo   Installez Python depuis https://www.python.org/
    pause
    exit /b 1
)

REM Démarrer l'API en arrière-plan (version UTF-8)
echo.
echo [1/2] Démarrage de l'API sur http://127.0.0.1:8000...
start "ÉlyonEU API" python run_api_utf8.py >nul 2>nul

REM Attendre que l'API démarre
timeout /t 4 /nobreak >nul

REM Démarrer l'app desktop
echo [2/2] Lancement de l'application desktop...
python test_app.py

REM Si l'app se ferme, faire un pause
pause

exit /b 0

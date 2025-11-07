@echo off
REM Lanceur ÉlyonEU Desktop Premium - Windows Batch (Orchestré)
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

REM Lancer le lanceur complet (API + Desktop)
echo.
echo Lancement du système complet (API + Application)...
echo.
python launch_complete.py

echo.
pause

exit /b 0

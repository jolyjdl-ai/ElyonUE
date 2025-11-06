@echo off
REM =====================================================
REM Créer des raccourcis sur le Bureau pour ÉlyonEU
REM =====================================================

setlocal enabledelayedexpansion

echo.
echo [Setup] Création des raccourcis sur le Bureau...
echo.

REM Obtenir le chemin du Desktop
for /f "tokens=3*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders" /v Desktop 2^>nul ^| find "Desktop"') do (
    set "DESKTOP_PATH=%%b"
)

if not defined DESKTOP_PATH (
    echo [ERROR] Impossible de trouver le chemin du Bureau
    pause
    exit /b 1
)

REM Obtenir les chemins
set "SCRIPT_DIR=%~dp0"
set "ROOT_DIR=%SCRIPT_DIR%.."

cd /d "%ROOT_DIR%"

REM Créer les raccourcis via PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$DesktopPath = '%DESKTOP_PATH%'; " ^
"$RootDir = '%ROOT_DIR%'; " ^
"$WshShell = New-Object -ComObject WScript.Shell; " ^
"" ^
"# Raccourci 1: App Premium" ^
"$Link1 = $WshShell.CreateShortcut('$DesktopPath\ÉlyonEU Premium.lnk'); " ^
"$Link1.TargetPath = '$RootDir\scripts\Start-Premium.bat'; " ^
"$Link1.WorkingDirectory = '$RootDir'; " ^
"$Link1.Description = 'ÉlyonEU Desktop Premium - Gouvernance 6S/6R'; " ^
"$Link1.IconLocation = 'C:\Windows\System32\imageres.dll,14'; " ^
"$Link1.Save(); " ^
"Write-Host '✓ Raccourci créé: ÉlyonEU Premium.lnk'; " ^
"" ^
"# Raccourci 2: API seule" ^
"$Link2 = $WshShell.CreateShortcut('$DesktopPath\ÉlyonEU API.lnk'); " ^
"$Link2.TargetPath = '$RootDir\scripts\Start-API.bat'; " ^
"$Link2.WorkingDirectory = '$RootDir'; " ^
"$Link2.Description = 'ÉlyonEU API Server (FastAPI)'; " ^
"$Link2.IconLocation = 'C:\Windows\System32\imageres.dll,196'; " ^
"$Link2.Save(); " ^
"Write-Host '✓ Raccourci créé: ÉlyonEU API.lnk'; "

if errorlevel 1 (
    echo.
    echo [ERROR] Une erreur s'est produite lors de la création des raccourcis
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Raccourcis créés sur le Bureau:
echo   - ÉlyonEU Premium.lnk (App + API)
echo   - ÉlyonEU API.lnk (API seule)
echo.
pause

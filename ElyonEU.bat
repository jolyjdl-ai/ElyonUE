@echo off
REM =====================================================
REM ÉlyonEU — Lanceur Principal (Racine du projet)
REM =====================================================

setlocal enabledelayedexpansion

cls
echo.
echo ============================================
echo   ÉlyonEU — Application Desktop Premium
echo   Gouvernance 6S/6R - Mode Local-First
echo ============================================
echo.
echo [1] Lancer l'app Premium (API + UI)
echo [2] Lancer l'API seule (FastAPI)
echo [3] Lancer l'app (si API déjà en cours)
echo [4] Créer raccourcis sur le Bureau
echo [5] Quitter
echo.

set /p choice="Choisir une option (1-5): "

if "%choice%"=="1" goto app_full
if "%choice%"=="2" goto app_api
if "%choice%"=="3" goto app_quick
if "%choice%"=="4" goto shortcuts
if "%choice%"=="5" goto quit

goto menu

:app_full
echo.
echo [launcher] Lancement de l'app complète...
call scripts\Start-Premium.bat
goto quit

:app_api
echo.
echo [launcher] Lancement de l'API...
call scripts\Start-API.bat
goto quit

:app_quick
echo.
echo [launcher] Lancement de l'app (rapide)...
call scripts\Start-Premium-Quick.bat
goto quit

:shortcuts
echo.
echo [setup] Création des raccourcis...
call scripts\Create-Shortcuts.bat
goto menu

:quit
echo.
echo [launcher] Fermeture.
exit /b 0

:menu
cls
goto start

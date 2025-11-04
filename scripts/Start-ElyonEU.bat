@echo off
setlocal ENABLEDELAYEDEXPANSION

rem Point de départ : dossier racine du projet
for %%i in ("%~dp0..") do set "ROOT=%%~fi"
set "API_DIR=%ROOT%\api"
set "APP_DIR=%ROOT%\app"
set "API_VENV=%API_DIR%\.venv"
set "APP_VENV=%APP_DIR%\.venv"
set "API_PY=%API_VENV%\Scripts\python.exe"
set "APP_PY=%APP_VENV%\Scripts\python.exe"

set "WITH_BROWSER=0"
set "SKIP_DESKTOP=0"
for %%A in (%*) do (
  if /I "%%~A"=="--with-browser" set "WITH_BROWSER=1"
  if /I "%%~A"=="--no-browser" set "WITH_BROWSER=0"
  if /I "%%~A"=="--no-desktop" set "SKIP_DESKTOP=1"
)

call :ensure_venv "%API_VENV%" "%API_DIR%" "%API_PY%" "%API_DIR%\requirements.txt"
if errorlevel 1 exit /b 1

if %SKIP_DESKTOP%==0 (
  call :ensure_venv "%APP_VENV%" "%APP_DIR%" "%APP_PY%" "%APP_DIR%\requirements_app.txt"
  if errorlevel 1 exit /b 1
)

echo [ElyonEU] Démarrage de l'API...
start "ElyonEU API" "%API_PY%" "%API_DIR%\elyon_api.py"

timeout /t 2 >nul

if %SKIP_DESKTOP%==0 (
  echo [ElyonEU] Démarrage de l'interface desktop...
  start "ElyonEU Desktop" "%APP_PY%" "%APP_DIR%\elyon_desktop.py"
)

if %WITH_BROWSER%==1 (
  echo [ElyonEU] Ouverture de la console web...
  start "ElyonEU Web" "http://127.0.0.1:8000/ui"
)

echo [ElyonEU] Services lancés. Utilisez scripts\Stop-ElyonEU.ps1 pour arrêter proprement.
exit /b 0

:ensure_venv
set "VENV_PATH=%~1"
set "WORK_DIR=%~2"
set "PYTHON_BIN=%~3"
set "REQ_FILE=%~4"
if exist "%PYTHON_BIN%" goto :eof

echo [ElyonEU] Préparation de l'environnement virtuel dans %VENV_PATH% ...
where py >nul 2>&1
if errorlevel 1 (
  python -m venv "%VENV_PATH%"
) else (
  py -3 -m venv "%VENV_PATH%"
)
if not exist "%PYTHON_BIN%" (
  echo [ElyonEU] Echec de création du venv dans %VENV_PATH%.
  exit /b 1
)
"%PYTHON_BIN%" -m pip install -U pip
if exist "%REQ_FILE%" (
  pushd "%WORK_DIR%"
  "%PYTHON_BIN%" -m pip install -r "%REQ_FILE%"
  popd
)
goto :eof

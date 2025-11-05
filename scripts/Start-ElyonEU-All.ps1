param(
    [switch]$Reinstall,
    [switch]$NoBrowser,
    [switch]$NoDesktop,
    [switch]$WithMonitor
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = "Stop"

$Root     = Split-Path -Parent $PSScriptRoot
$ApiDir   = Join-Path $Root "api"
$AppDir   = Join-Path $Root "app"
$MonFile  = Join-Path $Root "monitor\elyon_monitor.py"

$ApiVenv  = Join-Path $ApiDir ".venv"
$ApiPy    = Join-Path $ApiVenv "Scripts\python.exe"
$ApiReq   = Join-Path $ApiDir "requirements.txt"

$AppVenv  = Join-Path $AppDir ".venv"
$AppPy    = Join-Path $AppVenv "Scripts\python.exe"
$AppReq   = Join-Path $AppDir "requirements_app.txt"

function Ensure-Venv {
    param(
        [string]$Label,
        [string]$PythonPath,
        [string]$VenvPath,
        [string]$RequirementsFile,
        [switch]$Force,
        [string[]]$FallbackPackages
    )

    $venvExists = Test-Path $PythonPath
    if ($Force -or -not $venvExists) {
        Write-Host "→ Création venv $Label..." -ForegroundColor Cyan
        if (Test-Path $VenvPath) {
            Remove-Item $VenvPath -Recurse -Force
        }
        try { py -3 -m venv $VenvPath } catch { python -m venv $VenvPath }
        if (-not (Test-Path $PythonPath)) {
            throw "Impossible de préparer l'environnement $Label."
        }
        & $PythonPath -m pip install -U pip
        if (Test-Path $RequirementsFile) {
            & $PythonPath -m pip install -r $RequirementsFile
        } elseif ($FallbackPackages) {
            & $PythonPath -m pip install $FallbackPackages
        }
    }
}

Ensure-Venv -Label "API" -PythonPath $ApiPy -VenvPath $ApiVenv -RequirementsFile $ApiReq -Force:$Reinstall -FallbackPackages @("fastapi", "hypercorn")
Ensure-Venv -Label "APP" -PythonPath $AppPy -VenvPath $AppVenv -RequirementsFile $AppReq -Force:$Reinstall -FallbackPackages @("PySide6", "httpx")

$apiListening = $false
try {
    $apiListening = [bool](Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)
} catch {
    $apiListening = $false
}

if (-not $apiListening) {
    Write-Host "→ Démarrage API (Hypercorn)..." -ForegroundColor Green
    Start-Process -FilePath $ApiPy -ArgumentList (Join-Path $ApiDir "elyon_api.py") -WorkingDirectory $ApiDir -WindowStyle Minimized
    Start-Sleep -Seconds 2
} else {
    Write-Host "→ API déjà active sur le port 8000." -ForegroundColor Yellow
}

# *** PRIORITÉ : UI Desktop AVANT UI Navigateur ***
if (-not $NoDesktop) {
    Write-Host "→ Lancement UI desktop (PySide6)..." -ForegroundColor Green
    Start-Process -FilePath $AppPy -ArgumentList (Join-Path $AppDir "elyon_desktop.py") -WorkingDirectory $AppDir
    Start-Sleep -Seconds 1
}

if (-not $NoBrowser) {
    Write-Host "→ Ouverture UI navigateur..." -ForegroundColor Green
    Start-Process "http://127.0.0.1:8000/ui"
}

if ($WithMonitor -and (Test-Path $MonFile)) {
    Write-Host "→ Lancement moniteur console..." -ForegroundColor Green
    Start-Process -FilePath $AppPy -ArgumentList $MonFile -WorkingDirectory $Root
}

Write-Host "Tout est lancé. Utilise scripts/Stop-ElyonEU.ps1 pour arrêter proprement." -ForegroundColor Cyan

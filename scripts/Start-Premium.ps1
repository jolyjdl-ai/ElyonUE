#!/usr/bin/env pwsh
<#
.SYNOPSIS
  Lanceur ÉlyonEU Desktop Premium
.DESCRIPTION
  Démarre l'API FastAPI et l'application PySide6 premium avec design Showtime
#>

$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $MyInvocation.MyCommandPath
$root = Split-Path -Parent $root

Write-Host "[launcher] === ÉlyonEU Desktop Premium ===" -ForegroundColor Cyan
Write-Host "[launcher] Répertoire: $root" -ForegroundColor Gray

Push-Location $root

# Vérifier l'API
Write-Host "[launcher] Vérification de l'API..." -ForegroundColor Yellow
$apiRunning = $false
try {
    $result = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($result.StatusCode -eq 200) {
        Write-Host "[launcher] ✓ API déjà en cours" -ForegroundColor Green
        $apiRunning = $true
    }
} catch {}

if (-not $apiRunning) {
    Write-Host "[launcher] Démarrage de l'API..." -ForegroundColor Yellow
    Start-Process python -ArgumentList "-m", "uvicorn", "api.elyon_api:app", "--host", "127.0.0.1", "--port", "8000" -WindowStyle Minimized -PassThru | Out-Null
    Write-Host "[launcher] Attente 2s..." -ForegroundColor Gray
    Start-Sleep -Seconds 2
}

# Démarrer l'app premium
Write-Host "[launcher] Lancement de l'application Premium..." -ForegroundColor Green
try {
    python app\launch_premium.py
} catch {
    Write-Host "[launcher] Erreur: $_" -ForegroundColor Red
}

Pop-Location
Write-Host "[launcher] Fermeture." -ForegroundColor Gray

param([switch]$Reinstall)

$Root = "C:\ElyonEU"
$Api  = Join-Path $Root "api"
$App  = Join-Path $Root "app"

# venv API
$VenvApi = Join-Path $Api ".venv"
$PyApi   = Join-Path $VenvApi "Scripts\python.exe"
if (-not (Test-Path $PyApi)) {
  Write-Host "→ Préparation venv API..." -ForegroundColor Cyan
  try { py -3 -m venv $VenvApi } catch { python -m venv $VenvApi }
  & $PyApi -m pip install -U pip
  if (Test-Path (Join-Path $Api "requirements.txt")) {
    & $PyApi -m pip install -r (Join-Path $Api "requirements.txt")
  } else {
    & $PyApi -m pip install fastapi hypercorn
  }
}

# Démarre l'API si le port 8000 est libre
$busy = (Get-NetTCPConnection -State Listen -LocalPort 8000 -ErrorAction SilentlyContinue)
if (-not $busy) {
  Write-Host "→ Démarrage API (8000)..." -ForegroundColor Green
  Start-Process $PyApi -ArgumentList (Join-Path $Api 'elyon_api.py') -WorkingDirectory $Api
  Start-Sleep -Seconds 1
}

# venv APP
$VenvApp = Join-Path $App ".venv"
$PyApp   = Join-Path $VenvApp "Scripts\python.exe"
if ($Reinstall -or -not (Test-Path $PyApp)) {
  Write-Host "→ Préparation venv APP (PySide6)..." -ForegroundColor Cyan
  try { py -3 -m venv $VenvApp } catch { python -m venv $VenvApp }
  & $PyApp -m pip install -U pip
  & $PyApp -m pip install -r (Join-Path $App "requirements_app.txt")
}

# Lance l'application desktop
Write-Host "→ Lancement ÉlyonEU Desktop..." -ForegroundColor Green
& $PyApp (Join-Path $App "elyon_desktop.py")

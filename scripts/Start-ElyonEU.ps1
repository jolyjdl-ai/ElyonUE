# Start-ElyonEU.ps1 — démarre l'API locale et ouvre la page
$Root = "C:\ElyonEU"
$Api  = Join-Path $Root "api"
$Venv = Join-Path $Api ".venv"
$Py   = Join-Path $Venv "Scripts\python.exe"
$Req  = Join-Path $Api "requirements.txt"

if (!(Test-Path $Venv)) {
  Write-Host "→ Création venv et dépendances..." -ForegroundColor Cyan
  try { py -3 -m venv $Venv } catch { python -m venv $Venv }
  & $Py -m pip install -U pip
  if (Test-Path $Req) { & $Py -m pip install -r $Req }
}

Start-Process $Py -ArgumentList (Join-Path $Api 'elyon_api.py') -WorkingDirectory $Api
Start-Sleep -Seconds 1
Start-Process "http://127.0.0.1:8000"

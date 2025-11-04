param([switch]$Reinstall)
$Api = "C:\ElyonEU\api"
$Venv = Join-Path $Api ".venv"
$Py = Join-Path $Venv "Scripts\python.exe"
if ($Reinstall -or -not (Test-Path $Py)) {
  Write-Host "→ Prépare l'environnement Python..." -ForegroundColor Cyan
  try { py -3 -m venv $Venv } catch { python -m venv $Venv }
  & $Py -m pip install -U pip
  & $Py -m pip install -r (Join-Path $Api "requirements.txt")
}
Write-Host "→ Lancement API en avant-plan (logs visibles ici)..." -ForegroundColor Green
& $Py (Join-Path $Api "elyon_api.py")

# Stop-ElyonEU.ps1 — stoppe les serveurs ASGI Python lancés depuis Start
Get-Process python, python3 -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*\.venv\Scripts\python.exe" } | Stop-Process -Force -ErrorAction SilentlyContinue

# ÉlyonEU — Console locale mainframe

- **Principe** : gouvernance 6S/6R, journal JSONL local, IA générative locale (LM Studio ou fallback).
- **Composants** : API FastAPI unifiée (`api/`), application desktop PySide6 (`app/elyon_desktop.py`) et console web unique (`ui/chat/index.html`).

## Démarrage rapide
```powershell
Set-Location C:\ElyonEU
scripts\Start-ElyonEU.bat
```

L’application prépare les environnements virtuels locaux puis lance l’API, l’interface desktop PySide6 et, sur demande (`--with-browser`), la console web.

Pour un lancement manuel :
```powershell
Set-Location C:\ElyonEU
py -3 -m venv api\.venv
api\.venv\Scripts\python.exe -m pip install -r api\requirements.txt
api\.venv\Scripts\python.exe -m hypercorn api.elyon_api:app --bind 127.0.0.1:8000

# Fenêtre séparée
py -3 -m venv app\.venv
app\.venv\Scripts\python.exe -m pip install -r app\requirements_app.txt
app\.venv\Scripts\python.exe .\app\elyon_desktop.py
```

Script PowerShell équivalent (API + desktop) :
```powershell
Set-Location C:\ElyonEU
powershell -ExecutionPolicy Bypass -File .\scripts\Start-ElyonEU-Desktop.ps1
```

L’interface desktop comporte un bouton « Console web » qui ouvre directement `http://127.0.0.1:8000/ui` (ou l’URL définie via `ELYON_WEB_URL`).

## Arborescence clé
- `api/` : FastAPI, services (`core/*`), journaux.
- `app/` : application desktop PySide6 (`elyon_desktop.py`).
- `monitor/` : moniteur console mainframe.
- `journal/` : traces quotidiennes JSONL alignées 6S/6R.
- `data/` : corpus, index vectoriels et mémoire locale.
- `tests/gen.rest` : scénarios REST pour Postman/VS Code REST Client.

## Endpoints principaux
- `GET /health` : statut rapide.
- `GET /self` : identité, gouvernance, modes.
- `GET /events` : derniers événements (journalisés).
- `POST /chat` : échange IA locale (LM Studio → fallback heuristique).
- `POST /journal` : ajoute une entrée JSONL (type `NOTE`) dans le journal du jour.
- `GET /ui` : sert l’unique interface web (mêmes contenus que `/`).

## Notes
- Les intervalles heartbeat sont bornés entre 1 s et 3600 s.
- Les clients (desktop et monitor) consomment directement l’API unifiée.
- LM Studio optionnel : renseigner `config/chat_backend.json`, sinon fallback local.
- Depuis `api\`, utiliser `\.venv\Scripts\python.exe -m hypercorn elyon_api:app --reload --bind 127.0.0.1:8000` (module sans préfixe).

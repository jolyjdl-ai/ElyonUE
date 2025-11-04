# ÉlyonEU — Console locale mainframe

- **Principe** : gouvernance 6S/6R, journal JSONL local, IA générative locale (LM Studio ou fallback).
- **Composants** : API FastAPI unifiée (`api/`), console PySide6 Divine (`app/divine_desktop.py`), TUI/Textual, moniteur console.

## Démarrage rapide
```powershell
Set-Location C:\ElyonEU
py -3 -m venv api\.venv
api\.venv\Scripts\python.exe -m pip install -r api\requirements.txt
# Lancer l'API depuis la racine pour que le package `api` soit trouvé
api\.venv\Scripts\python.exe -m hypercorn api.elyon_api:app --bind 127.0.0.1:8000
```

Dans une autre console :
```powershell
Set-Location C:\ElyonEU
.\.venv_app\Scripts\python.exe .\app\divine_desktop.py
```

Ou bien tout lancer automatiquement (API + UI web + desktop) :
```powershell
Set-Location C:\ElyonEU
powershell -ExecutionPolicy Bypass -File .\scripts\Start-ElyonEU-All.ps1
```

## Arborescence clé
- `api/` : FastAPI, services (`core/*`), journaux, UI builder.
- `app/` : clients (PySide6 Divine, TUI, services historiques).
- `monitor/` : moniteur console mainframe.
- `journal/` : traces quotidiennes JSONL alignées 6S/6R.
- `data/ui_layouts/` : layouts générés via `/ui/rebuild`.
- `tests/gen.rest` : scénarios REST pour Postman/VS Code REST Client.

## Endpoints principaux
- `GET /health` : statut rapide.
- `GET /self` : identité, gouvernance, modes.
- `GET /events` : derniers événements (journalisés).
- `POST /chat` : échange IA locale (LM Studio → fallback heuristique).
- `POST /ui/rebuild` : archive un layout généré (JSON) et journalise l’action.
- `GET /journal/today` : renvoie les lignes JSONL du jour.

## Notes
- Les intervalles heartbeat acceptent des décimales (≥ 0.2 s).
- Les clients (desktop/TUI/monitor) consomment directement l’API unifiée.
- LM Studio optionnel : définir `LMSTUDIO_URL` et `LMSTUDIO_MODEL`, sinon fallback local.
- Depuis `api\`, utiliser `\.venv\Scripts\python.exe -m hypercorn elyon_api:app --reload --bind 127.0.0.1:8000` (module sans préfixe).

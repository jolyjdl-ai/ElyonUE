# Instructions pour les Agents AI - ÉlyonEU

> **Note**: Ce projet est en phase initiale de développement. L'architecture présentée ici constitue la fondation sur laquelle des fonctionnalités plus avancées seront construites.

## Architecture et Composants Principaux

### Vue d'Ensemble
- Application local-first avec gouvernance 6S/6R
- Architecture modulaire : API FastAPI + interface desktop PySide6 + console web légère
- Données strictement locales, pas de sorties non autorisées
- Structure extensible prévue pour ajouts futurs de composants majeurs

### Composants Clés
1. **API FastAPI** (`api/elyon_api.py`)
   - Point central de coordination
   - Gère les événements et la journalisation
   - Configuration via `config/*.json`

2. **Console Web** (`ui/chat/index.html`)
   - Unique UI navigateur servie par `/` ou `/ui`
   - Inclut chat, état et contrôle heartbeat

3. **Application Desktop** (`app/elyon_desktop.py`)
   - PySide6 : chat + moniteur temps réel dans un seul client
   - Bouton intégré pour ouvrir la console web locale

4. **Moniteur** (`monitor/elyon_monitor.py`)
   - Surveillance type "mainframe"
   - Affichage temps réel des événements

## Flux de Données
- Journalisation : format JSONL quotidien (`journal/journal_YYYYMMDD.jsonl`)
- Événements stockés en mémoire (max 2000) + persistance JSONL
- Structure de données : `{"ts": "YYYY-MM-DD HH:MM:SS", "type": "...", "data": {...}}`

## Workflows Développeur

### Démarrage Rapide
```powershell
scripts\Start-ElyonEU.bat
```
> Options utiles : `--with-browser` pour ouvrir la console web, `--no-desktop` pour ne lancer que l'API.

### Points d'Accès
- API : http://127.0.0.1:8000
- Documentation API : http://127.0.0.1:8000/docs
- Console web : http://127.0.0.1:8000/ui

### Conventions
- Encodage UTF-8 strict
- Timestamps format ISO : "YYYY-MM-DD HH:MM:SS"
- Configuration JSON dans `config/`
- Logs quotidiens dans `journal/`

## Extensions et Évolutions Futures

### Intégrations Actuelles
- Communication inter-composants via API REST locale
- Surveillance via endpoints `/self` et `/events`

### Points d'Extension Prévus
- Dossier `extensions/` préparé pour modules additionnels
- Structure de données `data/` adaptable pour nouveaux types de contenus
- Architecture permettant l'ajout de :
   - Nouveaux modules de traitement spécialisés
   - Connecteurs pour systèmes externes
   - Capacités de stockage étendues

## Contrat API (inputs / outputs — ce que les agents doivent connaître)

- GET /self
   - Retour: { "self": SELF }
   - `SELF` contient : `identity` (name, ver) et `modes` (private, governance, source). Déclaré dans `api/elyon_api.py`.

- GET /events
   - Retour: { "events": [ ... ] } — renvoie les ~100 derniers événements en mémoire.
   - Événement: { "ts": "YYYY-MM-DD HH:MM:SS", "type": "PING|CHAT|NOTE|CONTROL|...", "data": {...} }

- POST /journal
   - Reçoit un JSON dans le corps; crée un event de type `NOTE` via `log_event` et écrit une ligne JSONL dans `journal/journal_YYYYMMDD.jsonl`.

- GET /control
   - Retour: { "run_pings": bool, "interval_sec": int }

- POST /control
   - Corps accepté: { "run_pings": bool?, "interval_sec": int? }
   - Effets: met à jour `RUN_PINGS` et la variable d'environnement `ELYON_PING_INTERVAL` (contrôle le producteur de pings).

- POST /chat
   - Input: { "messages": [ { "role": "user|system|assistant", "content": "..." }, ... ], "temperature"?: float, "max_tokens"?: int }
   - Output: { "reply": "...", "provider": "openai|lmstudio|gen_local|gen_cloud|local_fallback", "trace": {...} }
   - Comportement: politique local-first (`policy=local_first` par défaut). Génération locale journalisée (`CHAT_TRACE` stage=local), puis appel externe uniquement si demandé (`use_external|external|force_external|prefer_external` à true) ou si `external_on_fallback` est activé lorsque la réponse tombe sur `gen_local`. Les événements `CHAT_TRACE` permettent de suivre chaque tentative/succès/erreur.

- GET /health
   - Retour: { "status": "ok", "ts": <float> }

Notes opérationnelles:
- Le producteur (`producer` dans `api/elyon_api.py`) génère des événements `PING` périodiques (par défaut 1s) contrôlables via `/control`.
- Les logs sont persistés ligne par ligne en JSONL dans `journal/` (une ligne par événement). Les agents doivent lire/écrire uniquement via l'API locale.

## Exemples concrets (à copier/coller pour tests rapides)

Exemple d'une ligne JSONL écrite dans `journal/`:

```
{"ts":"2025-10-28 10:11:14","type":"CHAT","data":{"provider":"lmstudio","len":123}}
```

Requête PowerShell: récupérer l'état `self` et les derniers événements

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/self' -Method Get
$events = Invoke-RestMethod 'http://127.0.0.1:8000/events' -Method Get
```

Tester le endpoint `/chat` (PowerShell)

```powershell
$body = @{ messages = @(@{ role = 'user'; content = 'Bonjour Elyon' }) } | ConvertTo-Json -Depth 4
Invoke-RestMethod 'http://127.0.0.1:8000/chat' -Method Post -Body $body -ContentType 'application/json'
```

Contrôle du heartbeat

```powershell
# Désactiver les PINGs
Invoke-RestMethod 'http://127.0.0.1:8000/control' -Method Post -Body (@{ run_pings = $false } | ConvertTo-Json) -ContentType 'application/json'
# Lire l'état
Invoke-RestMethod 'http://127.0.0.1:8000/control' -Method Get
```

## Commandes Clés
- `scripts\Start-ElyonEU.bat` : démarrage batch (API + desktop, navigateur optionnel)
- `scripts\Start-ElyonEU-Desktop.ps1` : app desktop (PySide6)
- `.`\scripts\Stop-ElyonEU.ps1` : arrêt propre
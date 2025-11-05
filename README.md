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

## Configuration IA
- `config/chat_backend.json` pilote le fournisseur de génération. Par défaut, `provider` vaut `lmstudio` (serveur local OpenAI-compatible).
- Pour utiliser OpenAI, placer `"provider": "openai"`, définir `"base_url": "https://api.openai.com/v1"` (ou un proxy compatible) et `"model"` (ex. `gpt-4o-mini`).
- Ne stockez pas la clé en clair : exportez-la via `setx OPENAI_API_KEY "votre_clé"` ou `setx ELYON_CHAT_API_KEY "votre_clé"`. L’option `OPENAI_ORG` est prise en charge.
- Les variables `ELYON_CHAT_PROVIDER`, `ELYON_CHAT_BASE_URL`, `ELYON_CHAT_MODEL`, `ELYON_CHAT_API_KEY` ainsi que `ELYON_CHAT_POLICY` (par défaut `local_first`) et `ELYON_CHAT_EXTERNAL_ON_FALLBACK` permettent de surcharger la configuration sans modifier le JSON.
- Dupliquez `.env.example` en `.env` (non versionné) pour un usage local ; laissez `OPENAI_API_KEY` vide ou injectez-la via `setx OPENAI_API_KEY "..."` afin d’éviter de conserver la clé dans le dépôt.
- Le fichier `.env` est chargé automatiquement au démarrage de l’API (`clé` OpenAI, `ALLOW_CLOUD`, etc.) sans écraser les variables déjà définies dans l’environnement.
- La génération suit un schéma local-first : réponse locale (`gen_local` ou `gen_cloud`) journalisée, puis appel externe uniquement sur demande (`"use_external": true`) ou lorsque le fallback local est activé si `external_on_fallback` vaut `true`.
- Chaque étape (locale, tentative externe, succès/erreur) est tracée dans le journal via les événements `CHAT_TRACE` et le champ `trace` retourné par `/chat` indique quel fournisseur a répondu.

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
- `POST /chat` : échange IA locale (LM Studio → fallback heuristique) avec mémoire courte + intentions + RAG léger.
- `POST /journal` : ajoute une entrée JSONL (type `NOTE`) dans le journal du jour.
- `GET /ui` : sert l’unique interface web (mêmes contenus que `/`).

## Mémoire, intentions et RAG
- Mémoire courte (`api/core/memory.py`) : conserve les cinq derniers tours et injecte un résumé structuré dans le prompt du chat.
- Analyse d’intention (`api/core/intent.py`) : détecte objectif, urgence, mots-clés et entités pour orienter la réponse.
- Index vectoriel TF-IDF (`api/core/vector_index.py`) : persiste dans `data/vector_index`, auto-chargé au démarrage et interrogeable depuis `/chat`.
- Scripts d’ingestion : utilisez les helpers Python (`VectorIndex.ingest_documents`) pour ajouter du contenu, ou placez des fichiers dans `data/corpus` avant un `reindex_corpus()`.
- Résultats RAG : visibles dans le journal (`CHAT_TRACE` avec `stage=rag`) et intégrés au contexte donné au modèle local.

## Notes
- Les intervalles heartbeat sont bornés entre 1 s et 3600 s.
- Les clients (desktop et monitor) consomment directement l’API unifiée.
- LM Studio optionnel : renseigner `config/chat_backend.json`, sinon fallback local.
- Lorsque `provider=openai`, seules les données de la conversation en cours sont transmises à l’API distante; aucun journal ou fichier n’est envoyé.
- Depuis `api\`, utiliser `\.venv\Scripts\python.exe -m hypercorn elyon_api:app --reload --bind 127.0.0.1:8000` (module sans préfixe).

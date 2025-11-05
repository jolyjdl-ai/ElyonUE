# ÉlyonEU — Guide Complet de Démarrage & Utilisation

**Version** : 0.3.0
**Date** : 5 novembre 2025
**Status** : ✅ OPÉRATIONNEL

---

## 📋 Vue d'ensemble

ÉlyonEU est une **plateforme IA locale-first** avec gouvernance 6S/6R, capable de :
- 🧠 **Comprendre rapidement** l'utilisateur (intentions, urgence, entités)
- 💾 **Mémoriser** le contexte conversationnel (buffer 5 tours)
- 🔍 **Rechercher** dans la connaissance (RAG vectoriel TF-IDF)
- 🌐 **Générer** localement d'abord, fallback OpenAI si demandé
- 📱 **Deux UIs** : Desktop (PySide6) prioritaire + Web (HTML/JS)

---

## 🚀 Démarrage Rapide

### Option 1 : Desktop + Web (Recommandé)
```powershell
cd C:\ElyonEU
.\scripts\Start-ElyonEU-All.ps1
```
Cela démarre :
1. API (Uvicorn port 8000)
2. **UI Desktop (PySide6)** → Chat + Moniteur temps réel
3. UI Web (navigateur) → Chat seul

### Option 2 : Desktop seul
```powershell
.\scripts\Start-ElyonEU-Desktop.ps1
```

### Option 3 : API + Web seul
```powershell
.\scripts\Start-ElyonEU.ps1
```

### Option 4 : API seul (debug)
```powershell
cd .\api
.\.venv\Scripts\python.exe C:\ElyonEU\run_api.py
```

---

## 🧪 Test de la Phrase Officielle

**Phrase** :
```
Peux-tu me résumer le plan gouvernance 6S/6R avec urgence, et proposer une prochaine étape opérationnelle alignée à la gouvernance ?
```

### Via Python (recommandé)
```powershell
C:\ElyonEU\api\.venv\Scripts\python.exe C:\ElyonEU\test_chat.py
```

### Via PowerShell
```powershell
$body = @{
    messages = @(
        @{
            role = "user"
            content = "Peux-tu me résumer le plan gouvernance 6S/6R avec urgence, et proposer une prochaine étape opérationnelle alignée à la gouvernance ?"
        }
    )
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" `
    -Method Post `
    -Body $body `
    -ContentType "application/json" | ConvertTo-Json
```

### Réponse attendue
```json
{
  "reply": "Le plan de gouvernance 6S/6R d'ElyonEU se résume comme suit...",
  "provider": "openai",
  "trace": {
    "policy": "local_first",
    "local_provider": "gen_local",
    "memory_used": false,
    "intent": {
      "intent": "summary_request",
      "urgent": true,
      "keywords": ["plan", "gouvernance", "6S/6R"]
    }
  }
}
```

---

## 🔧 Configuration

### Variables d'environnement

**Obligatoire pour OpenAI** :
```powershell
$env:ALLOW_CLOUD = "1"
$env:OPENAI_API_KEY = "sk-..."  # Remplacer par vraie clé
```

**Optionnel** :
```powershell
$env:ELYON_CHAT_PROVIDER = "openai"           # lmstudio|openai
$env:ELYON_CHAT_MODEL = "gpt-4o-mini"         # Détecté auto si non fourni
$env:ELYON_CHAT_POLICY = "local_first"        # local_first|fallback|external_first
$env:ELYON_CHAT_EXTERNAL_ON_FALLBACK = "1"    # Fallback cloud si local échoue
```

### Fichier de config
`config/chat_backend.json` :
```json
{
  "provider": "openai",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "api_key": ""
}
```
Note : `api_key` doit être dans `$env:OPENAI_API_KEY` (sécurité).

---

## 📡 Endpoints API

### Health Check
```bash
GET http://127.0.0.1:8000/health
```

### Chat (endpoint principal)
```bash
POST http://127.0.0.1:8000/chat
Content-Type: application/json

{
  "messages": [
    { "role": "user", "content": "Votre demande" }
  ],
  "temperature": 0.3,
  "max_tokens": 512,
  "rag_top_k": 3
}
```

### Événements (monitoring)
```bash
GET http://127.0.0.1:8000/events
```
Retourne les 100 derniers événements (CHAT, RAG, PING, etc.).

### Contrôle Heartbeat
```bash
GET http://127.0.0.1:8000/control
POST http://127.0.0.1:8000/control
  { "run_pings": false, "interval_sec": 5 }
```

---

## 🧠 Architecture Modules

| Module | Fichier | Rôle |
|--------|---------|------|
| **Mémoire** | `api/core/memory.py` | Buffer 5 tours conversationnels |
| **Intentions** | `api/core/intent.py` | Analyse urgence, keywords, entités |
| **RAG Vectoriel** | `api/core/vector_index.py` | Recherche TF-IDF (3 docs indexés) |
| **Configuration** | `config/chat_backend.json` | Provider, modèle, base_url |
| **API Central** | `api/elyon_api.py` | Orchestration `/chat`, événements, fallback |
| **Générateur local** | `app/services/generative_core.py` | Génération templates + cloud |

---

## 📊 Flux de Traitement (`/chat`)

```
1. Requête entrante
   ↓
2. Charger mémoire (résumé 5 tours)
   ↓
3. Analyser intentions utilisateur
   ↓
4. Recherche RAG (vectorielle TF-IDF)
   ↓
5. Enrichir messages avec contexte
   ↓
6. Génération LOCALE (d'abord)
   ↓
7. Vérifier policy (local_first)
   ├─ Si local OK → retour
   ├─ Si local échoue + external_on_fallback=true → fallback OpenAI
   └─ Si demande externe explicite → appel OpenAI
   ↓
8. Sauvegarder en mémoire
   ↓
9. Retourner réponse + trace
```

---

## 🎯 Capacités Actu elles

### ✅ Implémentées
- [x] Mémoire conversationnelle (5 tours)
- [x] Analyse d'intentions (urgence, keywords, entités)
- [x] RAG TF-IDF avec 3 documents indexés
- [x] Génération locale (fallback templates)
- [x] Provider OpenAI (gpt-4o-mini)
- [x] Policy local_first + fallback automatique
- [x] Logging détaillé (JSONL quotidien)
- [x] Health check + événements
- [x] UI Desktop prioritaire

### 🚧 Extensions Futures
- [ ] Indexer plus de documents (corpus extensible)
- [ ] Intégration complète PySide6 (chat + moniteur)
- [ ] Dashboard web temps réel
- [ ] Support LM Studio local (OpenAI-compatible)
- [ ] Agents spécialisés (ego, sensorium, superego)
- [ ] Vector database (remplacer TF-IDF)

---

## 🐛 Troubleshooting

### L'API ne démarre pas
```powershell
# Vérifier l'import
C:\ElyonEU\api\.venv\Scripts\python.exe -c "from api import elyon_api; print('OK')"

# Vérifier la syntax
python -m py_compile C:\ElyonEU\api\elyon_api.py
```

### Erreur 500 sur `/chat`
Vérifier les logs dans la fenêtre API (les `[api] [DEBUG n]` affichent l'étape en erreur).

### OpenAI retourne 400
Vérifier :
- Clé API valide : `$env:OPENAI_API_KEY`
- Modèle disponible : `$env:ELYON_CHAT_MODEL`
- Messages valides (role + content requis)

### Mémoire vide
La mémoire se remplit au fur des interactions. Premier appel → pas de contexte antérieur.

---

## 📝 Fichiers Clés

```
C:\ElyonEU/
├── api/
│   ├── elyon_api.py           ← API principale (FastAPI)
│   ├── core/
│   │   ├── memory.py          ← Mémoire conversationnelle
│   │   ├── intent.py          ← Analyse intentions
│   │   ├── vector_index.py    ← RAG TF-IDF
│   │   └── llm.py             ← Interface LLM
│   ├── routers/
│   │   └── generative.py      ← Routes `/gen/*`
│   └── requirements.txt        ← Dépendances API
├── app/
│   ├── elyon_desktop.py       ← UI Desktop (PySide6)
│   ├── services/
│   │   ├── generative_core.py ← Générateur interne
│   │   └── llm_client.py      ← Client LM Studio/OpenAI
│   └── requirements_app.txt    ← Dépendances Desktop
├── config/
│   └── chat_backend.json      ← Config chat
├── data/
│   ├── _memory/               ← Contexte conversationnel
│   ├── vector_index/          ← Index TF-IDF
│   └── corpus/                ← Docs à indexer
├── journal/                   ← Logs JSONL quotidiens
├── ui/
│   └── chat/
│       └── index.html         ← UI web
├── scripts/
│   ├── Start-ElyonEU-All.ps1  ← Démarrage complet
│   ├── Start-ElyonEU-Desktop.ps1
│   └── Start-ElyonEU.ps1
└── run_api.py                 ← Launcher API (uvicorn)
```

---

## 📞 Support

**Logs en temps réel** :
```powershell
# Monitor API
Get-Content C:\ElyonEU\journal\journal_20251105.jsonl -Tail 50 -Wait
```

**Vérifier l'état du système** :
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/self" -Method Get | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/events" -Method Get | ConvertTo-Json
```

---

**ÉlyonEU est prêt pour la production locale ! 🚀**

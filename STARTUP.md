## 🚀 ÉlyonEU - Application Desktop Premium v0.4.2

### ✅ Status

- ✓ **API FastAPI** fonctionnelle sur `http://127.0.0.1:8000`
- ✓ **Application Desktop** PySide6 avec design Showtime
- ✓ **Chat IA** avec réponses intelligentes
- ✓ **Moniteur** en temps réel (événements + état)
- ✓ **Gouvernance** 6S/6R intégrée

---

## 🎯 Démarrage Rapide

### Option 1: Lancer depuis Windows (Recommended)

Double-cliquez sur:
```
Start-Desktop.bat
```

Cela va:
1. Démarrer l'API FastAPI en arrière-plan
2. Attendre 4 secondes pour démarrage
3. Lancer l'application desktop PySide6

### Option 2: Lancer manuellement

Terminal 1 - API:
```powershell
cd C:\ElyonEU
python run_api_utf8.py
```

Terminal 2 - Application:
```powershell
cd C:\ElyonEU
python test_app.py
```

---

## 📋 Configuration

### Dépendances (déjà installées)
- `fastapi==0.121.0`
- `uvicorn==0.38.0`
- `pyside6==6.10.0`
- `requests==2.32.5`
- `httpx==0.28.1`

### Ports
- **API**: `127.0.0.1:8000`
- **Chat endpoint**: `POST /chat`
- **Health check**: `GET /health`

---

## 🎨 Interface Desktop

### 5 Panneaux de Navigation

1. **💬 Chat** - Conversation avec l'IA
   - Historique des messages
   - Envoi asynchrone
   - Affichage des réponses

2. **📊 Moniteur** - État du système
   - État actuel (gouvernance, mode)
   - Flux d'événements en temps réel
   - Polling automatique (1.5s et 3s)

3. **🗂️ Secrétariat** - Gestion de notes
   - Prise de notes libre
   - Zone texte éditable

4. **🛡️ Garde-fous 6S/6R** - Informations
   - 6S: Sécurité, Sincérité, Sobriété, Sens, Soin, Soutenabilité
   - 6R: Règles, Respect, Responsabilité, Réversibilité, Robustesse, Redevabilité

5. **ℹ️ À propos** - Informations
   - Version: v0.4.1
   - Crédit design
   - Architecture

---

## 🐛 Troubleshooting

### Erreur: "Port 8000 already in use"
```powershell
# Trouver le processus
Get-Process python | Where-Object {$_.ProcessName -match "python"}

# Tuer le processus
Stop-Process -Id <PID> -Force
```

### Erreur: "Module not found"
```powershell
cd C:\ElyonEU
pip install -U fastapi uvicorn pyside6 requests httpx
```

### Erreur: "Connection refused"
Attendez 5 secondes que l'API démarre complètement.

---

## 📝 Fichiers clés

- `app/elyon_desktop_premium.py` - Application desktop (PySide6)
- `run_api_utf8.py` - Lanceur API (encodage UTF-8)
- `test_app.py` - Script de test application
- `Start-Desktop.bat` - Batch launcher Windows
- `api/elyon_api.py` - Backend FastAPI

---

## 🔗 API Endpoints

```bash
# Health check
curl http://127.0.0.1:8000/health

# Chat
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Bonjour"}]}'

# État système
curl http://127.0.0.1:8000/self

# Événements
curl http://127.0.0.1:8000/events
```

---

## 📊 Événements Produits

L'API génère des événements:
- `PING` - Heartbeat (1s par défaut)
- `CHAT` - Messages chat
- `NOTE` - Notes journalisées
- `CONTROL` - Commandes système

Tous les événements sont persistés en JSONL dans `journal/journal_YYYYMMDD.jsonl`

---

## ✨ Design System

**Showtime Theme:**
- Background: `#0b0f14` (noir profond)
- Accent 1: `#6dd5ff` (cyan)
- Accent 2: `#b07cff` (violet)
- Text: `#e9f0f6` (blanc cassé)
- Muted: `#9fb3c8` (gris)

Sidebar width: 280px
Gradients & animations pour une interface premium

---

## 🎓 Prochaines Étapes

1. ✅ Tester le chat (envoyez un message)
2. ✅ Consulter le moniteur (événements/état)
3. ✅ Prendre des notes dans le secrétariat
4. 🔜 Intégration LMStudio (si disponible)
5. 🔜 Stockage de notes persistant
6. 🔜 Export événements (JSON, CSV)

---

**Version:** v0.4.2
**Date:** 2025-11-06
**Status:** Production Ready ✅

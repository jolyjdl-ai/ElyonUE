# Hiérarchie des UIs — ÉlyonEU

## Ordre de priorité (du plus important au moins important)

### 1. **UI Desktop (PySide6)** ⭐ PRIMARY
- **Fichier** : `app/elyon_desktop.py`
- **Composants** : Chat + Moniteur temps réel (côte à côte)
- **Avantages** :
  - Interface complète, desktop-native
  - Intégration système tray/notifications futures
  - Meilleure UX pour l'utilisation quotidienne
- **Lancement** :
  ```powershell
  .\scripts\Start-ElyonEU-Desktop.ps1          # Desktop seul
  .\scripts\Start-ElyonEU-All.ps1              # Desktop + Web (si besoin)
  .\scripts\Start-ElyonEU-All.ps1 -NoDesktop   # Web seul (si debug)
  ```

### 2. **UI Web (HTML/JS)** ⚠️ SECONDARY
- **Fichier** : `ui/chat/index.html`
- **Cas d'usage** :
  - Accès remote/fallback si desktop unavailable
  - Debugging / monitoring
  - Partage écran simple
- **Lancement** :
  ```powershell
  .\scripts\Start-ElyonEU.ps1                  # API + Web seul
  .\scripts\Start-ElyonEU-All.ps1 -NoBrowser   # Desktop seul (sans web)
  ```

## Architecture

```
API (FastAPI port 8000)
├─ /ui           → web UI router
├─ /chat         → endpoint chat utilisé par les 2 UIs
└─ /static       → assets statiques
    ├─ app/elyon_desktop.py  ← PySide6 (appels HTTP à l'API)
    └─ ui/chat/index.html    ← Navigateur (appels HTTP à l'API)
```

## Configuration d'environnement

Les deux UIs utilisent les mêmes endpoints API :
- `ELYON_API_URL` : URL API (défaut: http://127.0.0.1:8000)
- `ELYON_WEB_URL` : URL UI web (défaut: $ELYON_API_URL/ui)

Exemple de switch à la UI desktop tout en gardant API locale :
```powershell
$env:ELYON_API_URL = "http://127.0.0.1:8000"
& "C:\ElyonEU\app\.venv\Scripts\python.exe" "C:\ElyonEU\app\elyon_desktop.py"
```

## Modifications récentes

✅ **2025-11-05** : Inversé ordre de démarrage dans `Start-ElyonEU-All.ps1`
- Desktop se lance maintenant AVANT le navigateur web
- Clarifié commentaires dans `Start-ElyonEU.ps1`

---

**Note** : La philosophie est **desktop-first**, avec le web comme fallback / monitoring.

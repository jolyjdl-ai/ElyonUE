# 🚀 ÉlyonEU Desktop — Lanceurs Batch (`.bat`)

## 📂 Fichiers Disponibles

### À la Racine (accès direct)
- **`ElyonEU.bat`** — 🎯 **Menu principal interactif** (recommandé pour première utilisation)
- **`Run-Premium.bat`** — ⚡ **Double-clic pour lancer l'app** (plus rapide)

### Dossier `scripts/`

#### Lanceurs Batch
- **`Start-Premium.bat`** — 🔴 Lance l'API + l'app Premium (complet)
- **`Start-Premium-Quick.bat`** — ⚡ Lance juste l'app (API doit tourner)
- **`Start-API.bat`** — 🔧 Lance l'API seule (développement)
- **`Create-Shortcuts.bat`** — 🖥️ Crée des raccourcis sur le Bureau

#### Lanceurs Alternatifs
- **`Start-Premium.ps1`** — PowerShell version
- **`Launch-Premium.vbs`** — VBS (interface graphique simple)
- **`launch_premium.py`** — Python wrapper

#### Documentation
- **`README-LAUNCHERS.md`** — 📖 Guide complet d'utilisation

---

## 🎯 Recommandations d'Utilisation

### 👨‍💼 Pour un Utilisateur Final
1. **Double-clic sur `Run-Premium.bat`** à la racine
2. L'application démarre automatiquement
3. C'est tout ! 🎉

### 👨‍💻 Pour les Développeurs
**Option A:** Menu interactif
```bash
ElyonEU.bat
```

**Option B:** Terminal 1 (API)
```bash
scripts\Start-API.bat
```
Terminal 2 (App)
```bash
scripts\Start-Premium-Quick.bat
```

### 🔧 Setup Initial
Pour créer des raccourcis sur le Bureau :
```bash
scripts\Create-Shortcuts.bat
```
Ou via le menu :
```bash
ElyonEU.bat  # Puis choisir option 4
```

---

## 📋 Comparaison Rapide

| Fichier | Mode | API | UI | Console |
|---------|------|-----|-------|---------|
| `Run-Premium.bat` | ⚡ Auto | ✅ | ✅ | Normale |
| `ElyonEU.bat` | 🎯 Menu | 👤 Choix | 👤 Choix | Oui |
| `Start-Premium.bat` | 🔴 Complet | ✅ | ✅ | Oui |
| `Start-Premium-Quick.bat` | ⚡ Rapide | ❌ (externe) | ✅ | Oui |
| `Start-API.bat` | 🔧 Dev | ✅ | ❌ | Oui (détail) |

---

## 🎨 Raccourcis Bureau (après `Create-Shortcuts.bat`)

- **ÉlyonEU Premium.lnk** → Lance l'app complète
- **ÉlyonEU API.lnk** → Lance l'API seule

Double-cliquez depuis le Bureau pour démarrer ! 🖥️

---

## 💡 Astuces

### Relancer après une fermeture
- ✅ Simple : Double-clic sur `Run-Premium.bat`
- ✅ Rapide : `scripts\Start-Premium-Quick.bat` (si API tourne)

### Si l'API ne tourne plus
```bash
taskkill /IM python.exe /F
scripts\Start-API.bat
```

### Voir la documentation de l'API
```bash
http://127.0.0.1:8000/docs
```

### Tester en ligne de commande
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/self
```

---

## 📞 Support

Pour plus d'informations, consultez `scripts/README-LAUNCHERS.md`

Bon développement ! 🚀

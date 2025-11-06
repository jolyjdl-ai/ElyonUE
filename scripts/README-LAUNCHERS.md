# ÉlyonEU — Lanceurs Desktop

## 🚀 Démarrage Rapide

### Option 1: Lanceur Complet (Recommandé)
**Fichier:** `scripts/Start-Premium.bat`

Démarre automatiquement :
- ✅ L'API FastAPI (http://127.0.0.1:8000)
- ✅ L'application desktop Premium PySide6

```bash
cd C:\ElyonEU\scripts
Start-Premium.bat
```

### Option 2: Lanceur Rapide (API déjà en cours)
**Fichier:** `scripts/Start-Premium-Quick.bat`

Lance juste l'application si l'API tourne déjà

```bash
cd C:\ElyonEU\scripts
Start-Premium-Quick.bat
```

### Option 3: API Seule (Développement)
**Fichier:** `scripts/Start-API.bat`

Lance uniquement l'API FastAPI pour tester en ligne de commande ou navigateur

```bash
cd C:\ElyonEU\scripts
Start-API.bat
```

Accédez à :
- 🌐 Interface web: http://127.0.0.1:8000/ui
- 📚 Documentation API: http://127.0.0.1:8000/docs
- 🏥 Health check: http://127.0.0.1:8000/health

---

## 📋 Fichiers de Lancement

| Fichier | Fonction | Cible |
|---------|----------|-------|
| `Start-Premium.bat` | Complet (API + App) | 👨‍💻 Utilisateurs |
| `Start-Premium-Quick.bat` | App seule | 👨‍💻 Développeurs (API déjà lancée) |
| `Start-API.bat` | API seule | 🔧 Développement / Tests |
| `Start-Premium.ps1` | Version PowerShell (complet) | 💪 PowerShell |

---

## 🎯 Utilisation Typique

### Pour un utilisateur final
1. Double-cliquez `Start-Premium.bat`
2. L'app démarre automatiquement avec l'API
3. Profitez ! 🎉

### Pour développer
**Terminal 1 - API:**
```bash
scripts\Start-API.bat
```

**Terminal 2 - App (ou navigateur):**
```bash
scripts\Start-Premium-Quick.bat
```
ou
```bash
http://127.0.0.1:8000/ui
```

---

## 🛠️ Dépannage

### Python non trouvé
- Installez Python 3.10+ depuis https://www.python.org
- Cochez "Add Python to PATH" lors de l'installation

### Erreur "port déjà utilisé"
L'API tourne déjà. Utilisez `Start-Premium-Quick.bat` ou tuez le processus :
```bash
taskkill /IM python.exe /F
```

### L'app ne démarre pas
Vérifiez que l'API répond :
```bash
curl http://127.0.0.1:8000/health
```

---

## 📝 Notes

- **Mode local-first**: Zéro données sortantes sauf opt-in gouvernance
- **Gouvernance 6S/6R**: Appliquée à chaque chat
- **Audit immutable**: SHA-256 pour toutes les actions
- **Réversibilité**: Export complet possible

Bon développement ! 🚀

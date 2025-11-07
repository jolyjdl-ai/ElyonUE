# Guide de Génération des Formats PDF et DOCX

## 📋 Prérequis

Pour générer les versions **PDF** et **DOCX** du document `ELYON_REFERENCE_COMPLETE.md`, tu as besoin de:

### Option 1: Via Script Python (Recommandé)

Installe les dépendances:
```bash
pip install python-docx markdown2 weasyprint
```

Puis exécute le script:
```bash
python docs/generate_formats.py
```

**Résultat:** Les fichiers `.pdf` et `.docx` seront générés dans le dossier `docs/`.

### Option 2: Conversion en Ligne (Rapide)

1. **Markdown → PDF:** https://markdown-to-pdf.com/
   - Copie le contenu de `ELYON_REFERENCE_COMPLETE.md`
   - Colle dans l'outil
   - Télécharge le PDF

2. **Markdown → DOCX:** https://pandoc.org/try/
   - Format d'entrée: Markdown
   - Format de sortie: docx
   - Copie/colle le contenu
   - Télécharge le fichier

### Option 3: Via Pandoc (Professionnel)

Installe Pandoc: https://pandoc.org/installing.html

Puis:
```bash
# Générer PDF
pandoc ELYON_REFERENCE_COMPLETE.md -o ELYON_REFERENCE_COMPLETE.pdf --pdf-engine=wkhtmltopdf

# Générer DOCX
pandoc ELYON_REFERENCE_COMPLETE.md -o ELYON_REFERENCE_COMPLETE.docx
```

---

## 🎯 Quand Utiliser Chaque Format

| Format | Usage | Audience |
|--------|-------|----------|
| **Markdown** | Intégration Git, édition rapide, versionning | Devs, Architects |
| **PDF** | Impression, partage institutionnel, présentation | Tous |
| **DOCX** | Édition collaborative, commentaires, traduction | DLDE, PO, Execs |

---

## ✅ Après Génération

1. **Valider** que les 3 fichiers existent dans `docs/`:
   - `ELYON_REFERENCE_COMPLETE.md`
   - `ELYON_REFERENCE_COMPLETE.pdf`
   - `ELYON_REFERENCE_COMPLETE.docx`

2. **Commiter** le markdown seul (pas les binaires):
   ```bash
   git add docs/ELYON_REFERENCE_COMPLETE.md docs/README.md
   git commit -m "docs: Ajout de la référence complète Élyôn v1.0"
   ```

3. **Diffuser** les PDF/DOCX manuellement:
   - Email aux stakeholders
   - Slack/Teams
   - Wiki interne
   - Système documentaire DLDE

---

## 📞 Support

- Script Python non fonctionnel? → Vérifier les dépendances avec `pip list`
- PDF génération lente? → Normal pour 20+ pages
- DOCX édition cassée? → Utiliser LibreOffice plutôt que Word (meilleure compat)


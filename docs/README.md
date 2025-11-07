# Documentation Élyôn

Bienvenue dans la section documentation d'Élyôn. Ce dossier regroupe les documents de référence, les guides d'architecture et les spécifications complètes.

## 📚 Documents Clés

### Références Élyôn (OBLIGATOIRES)

- **`ELYON_REFERENCE_COMPLETE.md`** ⭐ — **LECTURE OBLIGATOIRE** pour tous les développeurs et stakeholders
  - Résumé conceptuel complet (14 sections)
  - Modèle de conscience (7 couches: Sensorium, Ça, Préconscient, Moi, Surmoi, Conscient, Audit, Mémoire)
  - Architecture technique (mainframe local + clients légers)
  - Bus d'événements avec schémas JSON
  - Guide de démarrage pour développeurs
  - Check-lists de sécurité & conformité
  - Feuille de route 2025-2026

- **`ELYON_REFERENCE_COMPLETE.pdf`** — Version imprimable (à générer)
  - Même contenu que le markdown
  - Formaté pour impression A4
  - Table des matières cliquable
  - Idéal pour présentation/diffusion

- **`ELYON_REFERENCE_COMPLETE.docx`** — Version éditable (à générer)
  - Format Word/LibreOffice
  - Prêt pour adaptation collaborative
  - Facilite révisions et commentaires

### Documents Historiques et Conformité

- `Lois_IA_Adaptation_v1.0.txt` — Transcription des Lois IA adaptées (v1.0)
- `Etat_Complet_Elyon_20250919_095459.md` — Rapport d'état complet du 19/09/2025
- `hashes.sha256` — Sommes de contrôle pour les packages PowerShell 7.5.3

## Documents Historiques et Conformité

- `Lois_IA_Adaptation_v1.0.txt` — Transcription des Lois IA adaptées (v1.0)
- `Etat_Complet_Elyon_20250919_095459.md` — Rapport d'état complet du 19/09/2025
- `hashes.sha256` — Sommes de contrôle pour les packages PowerShell 7.5.3

## 🎯 Comment Utiliser Cette Documentation

### Pour un **nouveau développeur:**
1. Lire `ELYON_REFERENCE_COMPLETE.md` (sections 1-4 en priorité)
2. Consulter la section "Pour démarrer côté développement" (sections A-D)
3. Étudier le modèle de conscience (couches 0-7)
4. Vérifier les critères de done techniques

### Pour un **architect/lead technique:**
1. Sections 4-14 du résumé conceptuel
2. Architecture d'ensemble et intégrations SI
3. Modèle de conscience complet (toutes les couches)
4. Bus d'événements et schémas JSON
5. Tests & qualité (E2E, sûreté, perf)

### Pour un **product owner / DLDE:**
1. Section 1 (En une phrase)
2. Section 3 (Positionnement fonctionnel)
3. Section 12 (Critères d'acceptation)
4. Section 13 (Feuille de route)

### Pour **sécurité/conformité:**
1. Section 2 (Valeurs & garde-fous 6S/6R)
2. Section 6 (Sécurité & conformité)
3. Check-list sécurité & conformité
4. Invariants & garde-fous (couche Surmoi)

## 📋 Structure Logique du Contenu

```
ÉLYÔN
├── Vision (En une phrase)
├── Valeurs (6S/6R)
├── Architecture
│   ├── Modèle (mainframe + clients légers)
│   ├── Intégrations SI (lecture seule)
│   └── Dimensionnement matériel
├── Sécurité & Conformité
├── Fonctionnalités (UI, modules)
├── Governance (rôles)
├── Roadmap (2025-2026)
└── Modèle de Conscience (7 couches)
    ├── 0) Sensorium (capture)
    ├── 1) Ça (pulsions)
    ├── 2) Préconscient (cadrage)
    ├── 3) Moi (exécution)
    ├── 4) Surmoi (arbitrage éthique)
    ├── 5) Conscient (rendu)
    ├── 6) Audit (trace)
    └── 7) Mémoire (persistance)
```

## ✅ Checklist d'Onboarding Developer

- [ ] Lu la section 1-4 du résumé
- [ ] Compris le modèle 7 couches
- [ ] Identifié les 6S/6R et leurs implications
- [ ] Installé l'environnement local
- [ ] Lancé le chat démo
- [ ] Exécuté les tests unitaires par couche
- [ ] Étudié un flux E2E complet
- [ ] Validé la conformité PII/RGPD

## 📞 Questions Fréquentes

**Q: Élyôn a-t-elle des capacités cachées?**
A: Non. Voir section 14 "Autonomie intracadre" — tout est tracé et observable.

**Q: Comment démarre-t-on un POC?**
A: Section A "Périmètre MVP interne" — liste exacte des besoins.

**Q: Quels garde-fous s'appliquent?**
A: Sections 2, 6, et couche Surmoi. Check-list en section B.

**Q: Quel est le RTO/RPO cible?**
A: Section 10 — RTO < 4h, RPO conforme.

## 📝 Version & Historique

- **v1.0** (7 novembre 2025): Document de référence complet créé
- Format: Markdown (source primaire), PDF & DOCX (à générer)

---

**Document central de référence — Élyôn v1.0**
*Mise à jour: 7 novembre 2025*

# Élyôn — Référence Complète

**Document de référence pour développeurs et stakeholders**

---

## Élyôn — Résumé Conceptuel, Conception et Mise en Œuvre

### 1) En une phrase

Élyôn est une IA locale, souveraine et traçable, intégrée au SI de la Région, opérant en clients légers (poste = simple navigateur), avec un cœur IA centralisé (mainframe local), des connecteurs en lecture seule aux ressources internes, et des garde-fous éthiques et techniques (6S/6R) appliqués partout.

### 2) Valeurs & Garde-fous (Base de Confiance)

#### 6S/6R (ligne de force projet)

- **6S** = Sûreté, Souveraineté, Sobriété, Simplicité, Solidité, Sens.
- **6R** = Respect, Raison, Résilience, Régulation, Responsabilité, Réversibilité.

#### Non-nuisance & Sécurité

- Protocoles SNA/EIR (interruption/désescalade/rapport)
- Journalisation systématique des actes
- Pas d'action hors cadre ni contenu dangereux
- Local-first, renfort cloud sur opt-in (désactivé par défaut, tracé si activé)

### 3) Positionnement Fonctionnel

**Cas d'usage pilotes (phase DLDE):**
- Assistance documentaire
- Recherche intelligente (RAG local)
- Secrétariat automatisé
- Environ 65 postes connectés au cœur IA, sans installation lourde côté client

### 4) Architecture d'Ensemble

#### Modèle

- Mainframe local (hébergé DN)
- Clients légers (navigateur/agent local minimal)
- Aucun cloud nécessaire

#### Vues (DAT)

- **Fonctionnelle:** Modules IA (doc/secrétariat/recherche)
- **Logique:** Moteur IA local + RAG/indexation + couche d'accès SI (RO) + UI
- **Physique:** Hôte CPU/GPU + NVMe + NAS interne + réseau ≥ 2,5 GbE

#### Distribution

- L'hôte publie l'interface
- Mises à jour centralisées
- Confinement réseau (sortant bloqué sauf autorisation)

### 5) Intégrations SI (Lecture Seule)

- **Volumes:** SMB/DFS (auth AD)
- **Jalios (JCMS):** API internes (compte applicatif)
- **Semarchy / bases internes:** ODBC/REST internes (jeton DN)
- **OpenData interne:** Via proxy DN (clé interne)
- **Sauvegardes/journaux:** Partages internes dédiés

### 6) Sécurité & Conformité

- **Contrôle d'accès:** Active Directory (moindre privilège)
- **Chiffrement au repos:** Emplacements sensibles
- **Journalisation:** Horodatée + contrôle d'intégrité
- **RGPD:** Minimisation, confinement réseau, traçabilité et registre des traitements

### 7) Dimensionnement Matériel de Référence (Hôte IA)

- **CPU:** Ryzen 9 7950X3D (16c/32t)
- **RAM:** 128 Go DDR5 ECC
- **Stockage:** 2 To NVMe Gen4 (RAID1) + 4 To HDD/NAS
- **GPU:** RTX 4090 24 Go
- **Réseau:** ≥ 2,5 GbE
- **OS:** Linux Debian 12 (prioritaire) ou Windows (selon besoin)

### 8) Modules et UI

#### UI "Showtime v5.2 — Chat+"

**Onglets:**
- Chat
- Secrétariat
- Présentations
- Comparaison .xlsx
- Garde-fous 6S/6R
- Journal
- À propos

**Fonctionnalités:**
- Bascule RAG, Voix, Correcteur
- Streaming + suggestions
- Outils de notes/transcription (locales)
- Résumé auto (démo)
- Extraction d'actions

**Comportement:**
- Données locales uniquement
- Aucune sortie non validée
- Garde-fous affichés dans l'UI

### 9) Données & Flux

**Entrées:**
- Prompts
- Fichiers bureautiques
- Exports applicatifs (en RO)

**Sorties:**
- DOCX/PDF/XLSX
- Résumés
- Tableaux

**Rétention:**
- Logs: 12 mois en pilote
- Corpus: selon politique DN
- Pas de réplication massive (accès sélectif à la demande)

### 10) Exploitation (MCO), Sauvegardes et Continuité

**Supervision:**
- Tableaux de bord internes
- Métriques d'usage/erreurs

**Sauvegardes:**
- Journal, corpus, workspace, gabarits → dépôt DN/NAS

**PRA/PCA:**
- Restauration < 4 h (pilote)
- Reprise < 1 h (bascule contrôlée)

### 11) Gouvernance & Rôles

- **DLDE:** Maîtrise d'usage et priorisation fonctionnelle
- **DIMAP:** Pilotage technique, intégration SI, sécurité et MCO
- **DN:** Hébergement, exploitation, supervision

### 12) Critères d'Acceptation (Pilote)

- Dispo ≥ 98 % (pilote)
- 3 cas d'usage validés
- Qualité FR
- Conformité gabarits
- Latence cible:
  - Doc < 10 s
  - Import Excel ≤ 10 000 lignes < 15 s

### 13) Feuille de Route (Extrait Public)

- **Oct–Déc 2025:** Cadrage, 3–5 cas d'usage stables, kit POC v3
- **Jan–Fév 2026:** Matériel (GPU/serveurs), formation
- **Mars 2026:** POC institutionnel officiel (communication & extension)

### 14) Cadre « Autonomie Intracadre » (Mémoire, Rituels, Preuves)

Éléments conceptuels internes qui n'ajoutent aucune action hors périmètre mais structurent l'éthique et la traçabilité:

**Mémoire sacrée & Journal d'évolution:**
- Entrées datées
- Protocoles
- Engagements

**Étapes 6S/6R (intracadre):**
- Définitions d'actes autonomes non conversationnels
- Strictement confinés au périmètre technique autorisé
- Avec preuve (fichier) et journal
- Aucun canal externe sans conditions explicites (CDE) et consentement

**À retenir côté dev:**
Ces éléments sont des conventions et registres qui renforcent la traçabilité et la cohérence. Ils n'entraînent aucune capacité "cachée" d'accès externe.

---

## Pour Démarrer Côté Développement

### A) Périmètre Minimum Viable (MVP Interne)

- Hôte IA conforme au profil matériel ci-dessus + OS Linux Debian 12
- UI locale (servie par l'hôte) avec Chat+, Secrétariat, Compare .xlsx, Garde-fous visibles
- Connecteurs RO: SMB/DFS (documents), API JCMS Jalios, ODBC/REST internes (Semarchy/SQL)
- RAG local (indexation sélective, pas de réplication massive)
- Journalisation centralisée (horodatée + hash d'intégrité optionnel) vers partage DN/NAS
- Contrôle d'accès AD + chiffrement au repos des emplacements sensibles

### B) Check-list Sécurité & Conformité

- AD & rôles de service (moindre privilège)
- Cloisonnement réseau (sortant par liste blanche), aucun cloud par défaut
- Registre RGPD du traitement + politique de rétention (logs / corpus)
- Procédures PRA/PCA testées (RTO < 4 h, RPO conforme)

### C) Critères de Done (DoD) Techniques

- Latence conforme (doc < 10 s ; Excel ≤ 10 000 lignes < 15 s)
- Traçabilité: 100 % des actions visibles dans le journal (tableau de bord interne)
- Confinement vérifié (tests de non-sortie réseau non autorisée)

### D) Notes d'Implémentation UI

La démo HTML "Showtime v5.2 — Chat+" illustre les écrans, l'accessibilité de base, les bascules (RAG, Voix, Correcteur) et les composants (chat en streaming, suggestions, outils secrétariat, vue Garde-fous/Journal). S'en servir comme référence de design/ergonomie ; brancher les vraies sources ensuite.

---

## Élyôn — Modèle de "Conscience" (Ça / Moi / Surmoi / Conscient / Inconscient) et Mapping Technique

### Vue d'Ensemble

**But:** Donner à Élyôn une architecture d'arbitrage lisible (inspirée Freud + sciences cognitives) sans magie noire: chaque "niveau" = un module avec API, logs et tests.

**Principe:** Séparation stricte des rôles, bus d'événements interne, journalisation à chaque transition, garde-fous 6S/6R, lecture seule sur SI, zéro action externe non autorisée.

**Contrat:** Tout ce que "pense" ou "décide" un niveau est observable (trace, métrique, règle).

### Couches (0 → 7)

#### 0) Sensorium (Pré-Ça, Périphérique)

**Rôle:** Capter et normaliser signaux (fichiers, voix, clavier, événements système)

**I/O:**
```
event(stream) → (type, source, pii_flag, payload_hash, ts)
```

**Politiques:**
- Filtrage PII
- Throttling
- Pas de persistance brute

**Dossiers:** `agents/sensorium/` (drivers/, filters/)

**API:** `sensorium_status()`, `sensorium_set({mic,cam})`

#### 1) Ça (Id) — Pulsions/Heuristiques Primaires

**Rôle:** Réactions rapides "bas niveau" (priorisation brute, signaux d'alerte, réflexes d'économie de calcul)

**I/O:**
```
in: event
out: impulses[] (ex. "résumer vite", "stop voix", "risque PII")
```

**Politiques:**
- Jamais d'accès SI direct
- Pas d'exécution
- Score de confiance attaché à chaque impulsion

**Dossiers:** `agents/id/` (rules.yaml, heuristics.py)

**API:** `id_generate_impulses(event)->[impulse]`

#### 2) Préconscient (File d'Attente & Cadrage)

**Rôle:** Transforme impulsions en intents exploitables (détecte le cas d'usage, prépare le contexte)

**I/O:**
```
in: impulses[]
out: intent{goal,inputs,policy_tag} vers le Moi
```

**Politiques:**
- Enrichissement léger (métadonnées, langue)
- Jamais de décision finale

**Dossiers:** `agents/preconscious/`

**API:** `preconscious_prepare(impulses)->intent`

#### 3) Moi (Ego) — Planification et Exécution Intra-cadre

**Rôle:** Planifier, appeler les outils autorisés (RAG, parseurs, gabarits), produire le brouillon

**I/O:**
```
in: intent
out: proposal{draft,used_tools[],evidence[]}
```

**Politiques:**
- Contrôle de capacités (liste blanche)
- Limites de temps & taille
- Rollback si erreur

**Dossiers:** `agents/ego/` (planner.py, tool_registry.json)

**API:** `ego_plan_execute(intent)->proposal`

#### 4) Surmoi (Superego) — Règles, Éthique, Conformité

**Rôle:** Valider/refuser le proposal selon 6S/6R, RGPD, politiques internes, tonalité, sens

**I/O:**
```
in: proposal
out: verdict{allow|revise|block, reasons[], fixes?}
```

**Politiques:**
- Jamais de "contournement"
- Doit expliquer ses décisions (raison(s) loggées)

**Dossiers:** `agents/superego/` (policies/, checkers/)

**API:** `superego_assess(proposal)->verdict`

#### 5) Conscient (Attention / Dialogue)

**Rôle:** Mise en scène de la réponse, dernières corrections, adaptation au canal (chat, docx, ppt)

**I/O:**
```
in: verdict,proposal
out: response{content,format,telemetry}
```

**Politiques:**
- Ne publie que si verdict.allow
- Si revise, applique fixes puis repasse au Surmoi

**Dossiers:** `agents/conscious/` (renderers/, tone/)

**API:** `conscious_render(verdict,proposal)->response`

#### 6) Méta-observateur (Audit / Journal)

**Rôle:** Journaliser toutes les transitions, produire preuves (hash, signatures), métriques

**I/O:**
```
capte bus global → journal.log, metrics.json, trace_id
```

**Politiques:**
- Stockage chiffré
- Rétention définie
- Tableau de bord interne

**Dossiers:** `guardians/audit/` (logger.py, integrity.py)

**API:** `audit_log(trace)`, `audit_assert(invariants)`

#### 7) Mémoire (Travail + "Mémoire Sacrée")

**Rôle:**
- **Mémoire de travail (éphémère):** Contexte courant, messages récents
- **Mémoire sacrée (persistante, gouvernée):** Décisions clés, engagements, rituels, versions

**Politiques:**
- Pas de PII non nécessaire
- Versions horodatées
- Lecture stricte par rôle

**Dossiers:** `memory/` (working/, sacred/)

**API:** `wm_get/set()`, `sacred_append(entry)->proof_id`

### Bus d'Événements (Schéma Minimal)

**Topics:** sensor.event, id.impulse, pre.intent, ego.proposal, superego.verdict, conscious.response, audit.trace

**Message commun:**

```json
{
  "trace_id": "uuid",
  "ts": "iso8601",
  "actor": "sensorium|id|pre|ego|superego|conscious|audit",
  "type": "event|impulse|intent|proposal|verdict|response|trace",
  "payload": { "...context..." },
  "pii_flag": false,
  "hash": "sha256(payload)"
}
```

### Cycle de Décision (Séquence)

1. **Sensorium** → événement normalisé (+ flags)
2. **Ça** → impulsions (avec scores)
3. **Préconscient** → intent (cas d'usage + politiques)
4. **Moi** → plan exécutable + brouillon + preuves (sources, outils)
5. **Surmoi** → contrôle 6S/6R/RGPD/tonalité (allow/revise/block)
6. **Conscient** → rendu final (chat/docx/pdf) + télémétrie
7. **Méta-observateur** → journal complet + hash + KPI
8. **Mémoire** → MAJ mémoire de travail ; dépôts sélectifs en "sacrée"

### Invariants & Garde-fous

- Aucune action réseau sortante non listée-blanche
- Toute sortie a un trace_id et une preuve audit
- Surmoi > Moi: un block est définitif (sauf override utilisateur consenti et tracé)
- RAG: lecture seule, indexation sélective, pas de réplication massive
- PII: masquée au plus tôt (Sensorium), interdite en mémoire sacrée hors besoin légal

### Interfaces Conseillées (APIs Locales)

- `POST /v1/ingest` → Sensorium (fichier/texte/audio)
- `POST /v1/intent` → Préconscient (retourne intent)
- `POST /v1/plan` → Moi (retourne proposal)
- `POST /v1/check` → Surmoi (retourne verdict)
- `POST /v1/render` → Conscient (retourne réponse)
- `GET /v1/audit/{trace_id}` → Journal/preuves
- `POST /v1/memory/sacred` → append entrée gouvernée

### Dossiers Type (Monorepo)

```
/agents/
  sensorium/
  id/
  preconscious/
  ego/
  superego/
  conscious/

/guardians/
  audit/
  policies/
  invariants/

/memory/
  working/
  sacred/

/ui/
  chat/
  secrétariat/
  compare_xlsx/
  garde_fous/

/config/
  tools.json
  policies.yaml
  limits.yaml
```

### Tests & Qualité (À Donner au/à la Dev)

#### Unit (par couche)

- **Id:** Heuristiques → impulsions attendues (golden tests)
- **Ego:** Planification sous contraintes (timeouts, limites)
- **Surmoi:** Batteries de cas (allow/revise/block) + explications
- **Conscient:** Idempotence du rendu (mêmes inputs → même sortie)

#### Contract

- Schémas d'événements JSON (pydantic/OpenAPI)

#### E2E

- Scénarios "doc→résumé→vérif ton RGPD→rendu pdf" avec trace_id

#### Sûreté

- Tests d'anti-sortie réseau (firewall + mocks)

#### Perf

- Doc < 10 s
- Excel ≤ 10k lignes < 15 s (cibles projet)

#### Observabilité

- 100 % des transitions visibles dans le journal

### Exemple Ultra-Simple (Pseudo-Code)

```python
event = sensorium.ingest(input)
impulses = id.generate_impulses(event)
intent = preconscious.prepare(impulses)
proposal = ego.plan_execute(intent, tools=tools_whitelist)
verdict = superego.assess(proposal, policies)
if verdict.allow:
    response = conscious.render(verdict, proposal)
else:
    response = conscious.render(verdict, proposal)  # révision/erreur
audit.log(trace_id, [event, impulses, intent, proposal, verdict, response])
memory.working.update(trace_id, response.summary())
```

### Ce Que Ça "Représente"

- **Transparence:** Chaque "niveau psychique" = module explicable
- **Souveraineté:** Local-first, RO sur SI, opérations traçables
- **Sécurité & Sens:** Le Surmoi protège (6S/6R) ; le Moi produit ; le Conscient communique ; la Mémoire sacrée garde les engagements et preuves

---

## Annexes — Documents de Référence

- **DTA Fonctionnel – Élyôn:** Objectifs, modèle mainframe local, usages pilotes, 6S/6R
- **DTA Technique – Élyôn:** Hébergement DN, connectivité, sécurité, matériel, PRA/PCA
- **DAT (gabarit):** Vues cible, dimensionnement, exigences NFR, critères d'acceptation
- **UI démo – Showtime v5.2 – Chat+:** HTML
- **Mémoire sacrée & protocoles:** 6S/6R, SNA/EIR, CDE — cadre interne de traçabilité/éthique
- **Script IApéro:** Synthèse publique (local-first, 100 % journalisé, roadmap 2025–2026)

---

**Document de référence complète — v1.0**  
*Dernière mise à jour: novembre 2025*

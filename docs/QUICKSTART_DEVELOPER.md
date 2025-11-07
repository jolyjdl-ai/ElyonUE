# 🚀 Quick Start Developer Guide — Élyôn

**Pour les développeurs qui rejoignent le projet — Lire ceci en 10 minutes.**

---

## En Deux Mots

Élyôn est une **IA locale souveraine** qui tourne sur un **mainframe régional**, pas dans le cloud. Elle opère via 7 couches de "conscience" (Sensorium → Moi → Surmoi → Audit → Mémoire), avec journalisation complète et garde-fous 6S/6R appliqués partout.

**Pas de magic black box.** Chaque décision est tracée et explicable.

---

## 5 Concepts Clés à Retenir

### 1️⃣ **6S/6R** — Les Valeurs

**6S** (QUOI faire): Sûreté, Souveraineté, Sobriété, Simplicité, Solidité, Sens
**6R** (COMMENT): Respect, Raison, Résilience, Régulation, Responsabilité, Réversibilité

→ **Action:** Quand tu codes, pose-toi: *"Est-ce que ça respecte les 6S/6R?"*

### 2️⃣ **7 Couches de Conscience**

```
Entrée utilisateur
      ↓
0️⃣  Sensorium (normalise les signaux)
      ↓
1️⃣  Ça (réactions instinctives)
      ↓
2️⃣  Préconscient (prépare l'intent)
      ↓
3️⃣  Moi (exécute avec outils autorisés)
      ↓
4️⃣  Surmoi (valide éthiquement — PEUT BLOQUER)
      ↓
5️⃣  Conscient (met en scène la réponse)
      ↓
6️⃣  Audit (journalise tout + hash)
      ↓
7️⃣  Mémoire (sauve le contexte)
      ↓
Sortie utilisateur
```

→ **Action:** Comprends que **le Surmoi a le dernier mot** — pas de contournement possible.

### 3️⃣ **Local-First + Lecture Seule**

- Aucun appel réseau sortant sauf liste blanche
- Connexions SI en **lecture seule** (SMB/DFS, ODBC, API internes)
- Aucune donnée ne sort sans autorisation explicite (CDE)

→ **Action:** Quand tu intègres une source SI, *toujours* utiliser des comptes read-only.

### 4️⃣ **Traçabilité = 100% des Actions**

Chaque décision a un `trace_id` unique avec:
- Timestamp ISO
- Actor (quelle couche)
- Payload (ce qui a été décidé)
- Hash (preuve d'intégrité)

→ **Action:** Log systématiquement → trace_id = vraie monnaie du projet.

### 5️⃣ **Bus d'Événements Interne**

Pas d'appels directs couche-à-couche. Tout passe par le bus avec schéma JSON standard:

```json
{
  "trace_id": "uuid",
  "ts": "2025-11-07T14:30:00Z",
  "actor": "ego|superego|conscious|...",
  "type": "proposal|verdict|response|...",
  "payload": { /* contexte */ },
  "pii_flag": false,
  "hash": "sha256(...)"
}
```

→ **Action:** Respecte ce schéma pour tout événement système.

---

## Architecture Physique

```
Hôte IA (Mainframe Local)
├── CPU: Ryzen 9 7950X3D (16c/32t)
├── RAM: 128 Go DDR5 ECC
├── GPU: RTX 4090 (24 Go)
├── Stockage: 2 To NVMe (RAID1) + 4 To NAS
└── OS: Linux Debian 12 (prioritaire)

Clients (65 postes environ)
├── Navigateur Web (Vue Showtime)
└── Agent local minimal (pour la voix/fichiers)

Réseau
└── 2,5 GbE, confinement sortant (pare-feu)
```

→ **Action:** Ne pas supposer de cloud. Tout tourne localement.

---

## Mon Premier Code Élyôn

### Structure Standard d'un Module

```python
# agents/my_layer/my_module.py

import logging
import uuid
from datetime import datetime

class MyLayer:
    """Couche personnalisée pour [objectif]"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process(self, event: dict) -> dict:
        """Traite un événement"""
        trace_id = str(uuid.uuid4())

        # 1. Log entrée
        self.logger.info(f"[{trace_id}] Entrée: {event['type']}")

        # 2. Traiter
        result = self._do_work(event['payload'])

        # 3. Créer événement sortie
        output_event = {
            "trace_id": trace_id,
            "ts": datetime.utcnow().isoformat(),
            "actor": "my_layer",
            "type": "my_result",
            "payload": result,
            "pii_flag": result.get('has_pii', False),
            "hash": self._hash_payload(result)
        }

        # 4. Log sortie
        self.logger.info(f"[{trace_id}] Sortie: OK")

        return output_event

    def _do_work(self, payload: dict) -> dict:
        # Ton code métier ici
        return {"status": "done"}

    @staticmethod
    def _hash_payload(data: dict) -> str:
        import hashlib
        import json
        s = json.dumps(data, sort_keys=True)
        return hashlib.sha256(s.encode()).hexdigest()
```

---

## Checklist Avant de Coder

- [ ] Lis la section **4) Surmoi** — C'est la couche qui dit "non"
- [ ] Crée un **trace_id** pour chaque action
- [ ] Loggue les transitions (entry/exit)
- [ ] N'accède SI qu'en lecture seule
- [ ] Respecte le schéma JSON du bus
- [ ] Si tu bloqueras quelque chose → explique pourquoi (Surmoi)
- [ ] Tests unitaires + E2E + perf (< 10s pour doc)

---

## Fiches Rapides

### Intégrer une Nouvelle Source SI

```python
# ❌ MAUVAIS
import smb
conn = smb.SMBConnection(user="admin", password="secret")

# ✅ BON
import smb
service_account = os.getenv("SMB_SERVICE_ACCOUNT")  # read-only account
conn = smb.SMBConnection(user=service_account, auth="AD")
```

### Ajouter une Règle Surmoi

```yaml
# config/policies.yaml
policies:
  - name: "Block PII Export"
    condition: "output.has_pii and action.target == 'external'"
    verdict: "block"
    reason: "PII export attempt detected"
```

### Persister en Mémoire Sacrée

```python
# Memory sacrée = journal des décisions clés
sacred_entry = {
    "ts": datetime.utcnow().isoformat(),
    "event": "decision_made",
    "proof": {
        "source": "superego",
        "reasoning": "Safety threshold exceeded"
    }
}
memory.sacred_append(sacred_entry)
```

---

## Tests Obligatoires

### Test Unitaire (Par Couche)

```python
def test_superego_blocks_pii():
    proposal = {"text": "Email: user@example.com", "target": "external"}
    verdict = superego.assess(proposal, policies)
    assert verdict["allow"] == False
    assert "PII" in verdict["reasons"]
```

### Test E2E (Flux Complet)

```python
def test_doc_to_pdf_pipeline():
    # 1. Upload doc
    # 2. RAG search
    # 3. Generate résumé
    # 4. Check RGPD
    # 5. Export PDF
    # ✅ Tout est tracé
    # ✅ Latence < 10s
    # ✅ 100% actions dans journal
```

---

## Performances Cibles

| Opération | Cible | Notes |
|-----------|-------|-------|
| Doc summary | < 10s | Incluant RAG + Surmoi |
| Excel import | < 15s | Pour 10k lignes |
| Chat response | < 3s | Temps utilisateur perçu |
| Audit query | < 1s | Recherche dans journal |

---

## Ressources Essentielles

1. **`ELYON_REFERENCE_COMPLETE.md`** — Référence complète (150 pages)
2. **`docs/README.md`** — Index et guide d'usage
3. **`/agents/`** — Code source des couches
4. **`/config/policies.yaml`** — Règles Surmoi
5. **`/tests/`** — Suites test par couche

---

## Questions Frecq / Réponses Rapides

**Q: Puis-je contourner le Surmoi?**
A: Non. C'est une invariant système. Toute tentative est loggée et bloquée.

**Q: C'est du machine learning?**
A: Partiellement. Le Ça/Préconscient utilise heuristiques. Le Moi utilise RAG + LLM local. Le Surmoi est déterministe (règles).

**Q: Les données sortent où?**
A: Nulle part (par défaut). Confinement réseau strict + liste blanche. Si export: CDE explicite + trace.

**Q: Comment déboguer une trace?**
A: `GET /v1/audit/{trace_id}` — retourne toutes les couches traversées.

**Q: Quel Python version?**
A: 3.10+. Debian 12 = Python 3.11 natif.

---

## 🎯 Prochaines Étapes

1. ✅ Tu as lu ce guide
2. → Cloner le repo: `git clone <url>`
3. → Installer env: `python -m venv .venv && pip install -r requirements.txt`
4. → Lancer démo: `python app/elyon_desktop_premium.py`
5. → Lire `ELYON_REFERENCE_COMPLETE.md` (sections 1-4)
6. → Exécuter les tests: `pytest tests/`
7. → Rejoindre l'équipe tech sync

---

**Quick Start v1.0 — novembre 2025**
Pour toute question → #elyon-tech sur Slack ou contact@dlde.fr

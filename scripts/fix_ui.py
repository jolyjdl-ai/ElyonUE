#!/usr/bin/env python3
"""Ameliore la fonction local_generate() avec des reponses plus intelligentes."""

import sys

# Lire le fichier
with open('api/elyon_api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trouver les indices de la fonction
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'def local_generate(prompt: str, mode: str = "normal")' in line:
        start_idx = i
    if start_idx is not None and line.strip() == '# Mount local routers (if present)':
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print('[ERR] Cannot find function boundaries')
    print(f'start_idx={start_idx}, end_idx={end_idx}')
    sys.exit(1)

print(f'[OK] Function from line {start_idx+1} to {end_idx}')

# Nouvelle fonction amelioree
new_func = '''def local_generate(prompt: str, mode: str = "normal") -> tuple[str, str]:
    """Reponse intelligente locale avec support multi-mode et contexte educatif."""
    text = prompt.strip()
    if not text:
        return ("(mode local) Decris ta situation pour que je propose une prochaine etape alignee 6S/6R.", "gen_local")

    low = text.lower()

    # Detection d'intentions courantes
    if "mission" in low or "qui es-tu" in low or "c'est quoi" in low:
        return (
            "🎯 Ma mission ElyonEU\\n\\n"
            "Je guide les operateurs vers des actions concretes, ancrées dans les principes 6S/6R :\\n"
            "✓ Surete : Protéger les donnees et les personnes\\n"
            "✓ Souverainete : Rester dans la Region Grand Est\\n"
            "✓ Sobriete : Efficacité maximale, ressources minimales\\n"
            "✓ Simplicité : Actions claires et directes\\n"
            "✓ Solidarite : Servir la communaute educative\\n"
            "✓ Sens : Clarifier l'intention avant l'action",
            "gen_local",
        )

    if "aide" in low or "help" in low or "comment" in low or "fais quoi" in low:
        return (
            "🤝 Comment je peux t'aider\\n\\n"
            "1️⃣ Pose une question : Je recherche dans mes connaissances locales\\n"
            "2️⃣ Demande une synthese : Mode `resume` pour une vue rapide\\n"
            "3️⃣ Obtiens des actions : Mode `actions` pour des etapes concretes\\n"
            "4️⃣ Consulte l'audit : Verifie les evenements et decisions passees\\n\\n"
            "Remarque : Mode local = zero donnees sortantes, compliance 100% Region Grand Est",
            "gen_local",
        )

    # Detection de mots-cles de domaine educatif
    if any(k in low for k in ["audit", "journal", "log", "compliance", "conformite"]):
        return (
            "📊 Audit & Gouvernance\\n\\n"
            "L'audit de conformite ElyonEU fonctionne en continu :\\n"
            "✅ Tous les evenements sont loggés localement\\n"
            "✅ Audit trail immutable (SHA-256)\\n"
            "✅ Acces restreint au profil DIVINE uniquement\\n"
            "✅ Zero donnees sortantes sauf opt-in approuvé\\n\\n"
            "Pour voir l'etat complet, contacte Joeffrey (profil DIVINE).",
            "gen_local",
        )

    if any(k in low for k in ["dlde", "delegue", "delegation", "region", "gouvernance"]):
        return (
            "🏛️ DLDE - Souverainete Region Grand Est\\n\\n"
            "ElyonEU est conçu pour respecter la souverainete DLDE :\\n"
            "📍 Donnees strictement locales (Region Grand Est)\\n"
            "👥 65 utilisateurs DLDE configures\\n"
            "🔐 Roles granulaires (Divine, Admin, Chef, Enseignant, Agent, Public)\\n"
            "📋 Adaptation UI par role\\n\\n"
            "Besoin d'un role specifique ? Adresse-toi a l'administrateur.",
            "gen_local",
        )

    if any(k in low for k in ["classe", "eleve", "ecole", "cours", "apprentissage", "pedagogie", "enseignant"]):
        return (
            "📚 Ressources Educatives\\n\\n"
            "ElyonEU offre un support contextualise pour l'education :\\n"
            "📖 Corpus de reference accessibles localement\\n"
            "🧠 Apprentissage adaptatif aux profils\\n"
            "✨ Suggestions d'actions alignees a la pedagogie 6S/6R\\n\\n"
            f"Ton contexte : {text[:100]}...\\n"
            "Pour plus de details, utilise le mode `actions`.",
            "gen_local",
        )

    # Modes specialises
    if mode == "resume":
        summary = (
            f"📋 Synthese\\n\\n"
            f"Objet : {text[:120]}\\n\\n"
            f"✅ Analyse rapide completee en mode local\\n"
            f"💡 Prochaine etape : Clarifier l'intention operationnelle"
        )
        return (summary, "gen_local")

    elif mode == "actions":
        actions = (
            "🎯 Actions Recommandees\\n\\n"
            "1️⃣ Clarifier l'intention\\n"
            "   → Quel est l'objectif precis ?\\n\\n"
            "2️⃣ Verifier les prerequis\\n"
            "   → Donnees necessaires disponibles ?\\n"
            "   → Autorisations presentes ?\\n\\n"
            "3️⃣ Executer l'action\\n"
            "   → Etapes concretes alignees 6S/6R\\n\\n"
            "4️⃣ Documenter & Auditer\\n"
            "   → Journal local auto-complete\\n"
            "   → Trace immutable pour conformite"
        )
        return (actions, "gen_local")

    else:  # mode == "normal"
        response = (
            f"🔍 Analyse Locale\\n\\n"
            f"Ta demande : {text[:150]}\\n\\n"
            f"Approche ElyonEU :\\n"
            f"✓ Traitement 100% local (Region Grand Est)\\n"
            f"✓ Respect des profils de securite\\n"
            f"✓ Audit trail complet\\n\\n"
            f"Recommandation : Precise davantage ton besoin pour une reponse plus ciblee ou utilise `mode=actions` pour des etapes concretes."
        )
        return (response, "gen_local")

'''

# Remplacer
new_lines = lines[:start_idx] + [new_func + '\n'] + lines[end_idx:]

# Ecrire
with open('api/elyon_api.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('[OK] local_generate() amelioree et sauvegardee')
print(f'[INFO] Ancien : {end_idx - start_idx} lignes, Nouveau : 1 bloc')

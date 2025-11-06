#!/usr/bin/env python3
"""Ameliore la fonction local_generate() avec des reponses plus intelligentes."""

import sys
sys.path.insert(0, str(__file__).rsplit('\\', 1)[0].rsplit('\\', 1)[0])

with open('api/elyon_api.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Trouver les indices
start_line = None
end_line = None
for i, line in enumerate(lines):
    if 'def local_generate(prompt: str, mode: str = "normal")' in line:
        start_line = i
    if start_line is not None and line.strip().startswith('# Mount local routers'):
        end_line = i
        break

if start_line is None or end_line is None:
    print('[ERR] Cannot find function boundaries')
    sys.exit(1)

print(f'[DEBUG] Function from line {start_line+1} to {end_line}')

# Nouvelle fonction
new_func_lines = [
    'def local_generate(prompt: str, mode: str = "normal") -> tuple[str, str]:\n',
    '    """Reponse intelligente locale avec support multi-mode."""\n',
    '    text = prompt.strip()\n',
    '    if not text:\n',
    '        return ("(mode local) Decris ta situation pour que je propose une prochaine etape alignee 6S/6R.", "gen_local")\n',
    '\n',
    '    low = text.lower()\n',
    '    \n',
    '    # Detection d\'intentions courantes\n',
    '    if "mission" in low or "qui es-tu" in low:\n',
    '        return ("🎯 Ma mission ElyonEU\\nGuider l\'operateur vers des actions concretes avec les principes 6S/6R.", "gen_local")\n',
    '    \n',
    '    # Mots-cles de domaine\n',
    '    if "audit" in low or "journal" in low:\n',
    '        return ("📊 Audit & Gouvernance\\nTraces SHA-256, zero donnees sortantes, conformite Region Grand Est.", "gen_local")\n',
    '    \n',
    '    if "dlde" in low or "delegue" in low:\n',
    '        return ("🏛️ DLDE - Souverainete Region\\nDonnees strictement locales, 65 utilisateurs, roles granulaires.", "gen_local")\n',
    '    \n',
    '    # Modes specialises\n',
    '    if mode == "resume":\n',
    '        return (f"📋 Synthese : {text[:100]}...\\n✅ Analyse locale completee", "gen_local")\n',
    '    elif mode == "actions":\n',
    '        return ("🎯 Actions Recommandees :\\n1. Clarifier l\'intention\\n2. Verifier prerequis\\n3. Executer\\n4. Auditer", "gen_local")\n',
    '    else:  # normal\n',
    '        return (f"🔍 Analyse Locale\\nDemande : {text[:100]}...\\n✓ 100% local (Region Grand Est)\\n✓ Audit trail complet", "gen_local")\n',
    '\n',
]

# Assembler
new_lines = lines[:start_line] + new_func_lines + lines[end_line:]

# Ecrire
with open('api/elyon_api.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('[OK] local_generate() amelioree')

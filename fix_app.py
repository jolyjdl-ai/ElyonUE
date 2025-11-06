#!/usr/bin/env python3
"""Fix du fichier elyon_desktop_premium.py"""

with open('app/elyon_desktop_premium.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remplacer le problème QtCore.QButtonGroup()
old_code = '''        button_group = QtCore.QButtonGroup()
        for btn in [self.nav_chat, self.nav_monitor, self.nav_secretariat, self.nav_garde, self.nav_about]:
            button_group.addButton(btn)'''

new_code = '''        # Navigation buttons are now connected above with clicked.connect()'''

if old_code in content:
    content = content.replace(old_code, new_code)
    with open('app/elyon_desktop_premium.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ QtCore.QButtonGroup() remplacé avec succès")
else:
    print("✗ Code à remplacer non trouvé")
    print("Recherche QtCore.QButtonGroup()...")
    if "QtCore.QButtonGroup" in content:
        # Afficher le contexte
        idx = content.find("QtCore.QButtonGroup")
        print(f"Trouvé à position {idx}")
        print("Contexte:")
        print(content[idx-100:idx+100])
    else:
        print("QtCore.QButtonGroup() n'existe pas dans le fichier")

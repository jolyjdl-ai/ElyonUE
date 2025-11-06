#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')

print("[1] Importation PySide6...")
from PySide6.QtWidgets import QApplication
print("[2] Création QApplication...")
app = QApplication(sys.argv)

print("[3] Importation app...")
from app.elyon_desktop_premium import ElyonDesktopPremium

print("[4] Création fenêtre...")
try:
    window = ElyonDesktopPremium()
    print("✓ SUCCÈS - L'application est prête!")
    window.show()
    sys.exit(app.exec())
except Exception as e:
    print(f"✗ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

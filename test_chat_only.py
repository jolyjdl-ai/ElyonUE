#!/usr/bin/env python3
"""Test simple du chat widget"""
import sys
import os
sys.path.insert(0, str(os.path.dirname(__file__)))

from app.elyon_desktop_premium import ChatWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

def main():
    app = QApplication(sys.argv)

    # Créer une fenêtre simple avec juste le chat
    window = QMainWindow()
    window.setWindowTitle("Test Chat Widget")
    window.resize(600, 400)

    container = QWidget()
    layout = QVBoxLayout(container)

    chat = ChatWidget()
    layout.addWidget(chat)

    # Test: ajouter un message initial
    chat.add_message("assistant", "Bonjour! Je suis ÉlyonEU. Tape un message et appuie sur Enter!")

    # Connecter le signal pour afficher les messages envoyés
    def on_send(msg):
        print(f"[TEST] Message envoyé: {msg}")
        chat.add_message("user", msg)
        chat.add_message("assistant", f"Vous avez dit: {msg}")

    chat.sendRequested.connect(on_send)

    window.setCentralWidget(container)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()

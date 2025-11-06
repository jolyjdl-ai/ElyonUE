# -*- coding: utf-8 -*-
"""
ÉlyonEU — Application Desktop Premium (PySide6 / Qt)
Design "Showtime" : Sidebar coloré, gradients, panneaux élégants, multi-vues
Chat IA + Moniteur + Secrétariat
"""
import json, os, sys, threading, time
import requests
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtCore import Qt, QTimer, Signal, QUrl, QRect, QSize
from PySide6.QtGui import QColor, QPalette, QBrush, QLinearGradient, QFont, QIcon, QPixmap, QPainter
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QPlainTextEdit, QScrollArea,
    QStackedWidget, QFrame
)

API = os.environ.get("ELYON_API_URL", "http://127.0.0.1:8000")

# ================== HTTP Utils ==================
def http_get(path, timeout=5.0):
    try:
        r = requests.get(API + path, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"[desktop] GET {path} -> {exc}", flush=True)
        return None

def http_post(path, payload, timeout=20.0):
    try:
        r = requests.post(API + path, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as exc:
        print(f"[desktop] POST {path} -> {exc}", flush=True)
        return None

# ================== Design System ==================
COLORS = {
    "bg": "#0b0f14",
    "panel": "#121822",
    "panel2": "#0e141d",
    "acc": "#6dd5ff",       # Bleu ciel
    "acc2": "#b07cff",      # Violet
    "text": "#e9f0f6",
    "muted": "#9fb3c8",
    "ok": "#5bd19a",        # Vert
    "warn": "#f0c85a",      # Jaune
    "bad": "#ff7a7a",       # Rouge
    "chip": "#1a2230",
    "shadow": "0 10px 30px rgba(0,0,0,.35)",
}

def create_stylesheet():
    """Stylesheet global premium"""
    return f"""
    QMainWindow, QWidget {{
        background: {COLORS['bg']};
        color: {COLORS['text']};
        font-family: system-ui, -apple-system, Segoe UI, Roboto;
        font-size: 13px;
    }}

    QPushButton {{
        background: linear-gradient(180deg, #1b2636, #16202e);
        color: {COLORS['text']};
        border: 1px solid rgba(255,255,255,.10);
        border-radius: 12px;
        padding: 10px 14px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background: linear-gradient(180deg, #1f2a40, #1a2638);
    }}

    QPushButton:pressed {{
        background: linear-gradient(180deg, #16202e, #1b2636);
    }}

    QPushButton.primary {{
        background: linear-gradient(90deg, rgba(109,213,255,.35), rgba(176,124,255,.35));
        border-color: rgba(255,255,255,.16);
    }}

    QPlainTextEdit, QTextEdit {{
        background: {COLORS['panel2']};
        color: {COLORS['text']};
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 10px;
        padding: 10px;
        selection-background-color: rgba(109,213,255,.25);
    }}

    QLabel {{
        color: {COLORS['text']};
    }}

    QLabel.muted {{
        color: {COLORS['muted']};
        font-size: 12px;
    }}

    QScrollBar:vertical {{
        background: {COLORS['panel']};
        width: 10px;
        border-radius: 5px;
    }}

    QScrollBar::handle:vertical {{
        background: rgba(109,213,255,.2);
        border-radius: 5px;
        min-height: 20px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: rgba(109,213,255,.4);
    }}
    """

# ================== Custom Widgets ==================

class SidebarButton(QPushButton):
    """Bouton sidebar stylisé"""
    def __init__(self, icon_emoji: str, label: str, parent=None):
        super().__init__(parent)
        self.setText(f"{icon_emoji}  {label}")
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {COLORS['muted']};
                border: 1px solid transparent;
                padding: 12px 10px;
                border-radius: 10px;
                text-align: left;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background: rgba(109,213,255,.10);
                color: {COLORS['text']};
                border-color: rgba(255,255,255,.06);
            }}
            QPushButton:checked {{
                background: linear-gradient(90deg, rgba(109,213,255,.15), rgba(176,124,255,.15));
                color: {COLORS['text']};
                border-color: rgba(255,255,255,.06);
            }}
        """)
        self.setCheckable(True)

class PanelCard(QFrame):
    """Panneau stylisé avec titre"""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: linear-gradient(180deg, rgba(18,24,34,.95), rgba(12,18,27,.92));
                border: 1px solid rgba(255,255,255,.06);
                border-radius: 18px;
                padding: 16px;
            }}
        """)

        self.title = QLabel(title)
        self.title.setFont(QFont("system-ui", 16, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {COLORS['text']};")

        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.content, 1)
        main_layout.setContentsMargins(0, 0, 0, 0)

class ChatWidget(QWidget):
    """Panneau Chat avec historique + input"""
    sendRequested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Titre
        title = QLabel("💬 Chat — Conversation naturelle")
        title.setFont(QFont("system-ui", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")

        desc = QLabel("Pose une question ouverte. Styles et longueur réglables.")
        desc.setObjectName("muted")
        desc.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px;")

        # Zone chat (historique)
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['panel2']};
                color: {COLORS['text']};
                border: 1px solid rgba(255,255,255,.08);
                border-radius: 10px;
            }}
        """)

        # Zone input
        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("Écrire un message…")
        self.input.setMaximumHeight(80)
        self.input.setStyleSheet(f"""
            QPlainTextEdit {{
                background: {COLORS['panel2']};
                color: {COLORS['text']};
                border: 1px solid rgba(255,255,255,.08);
                border-radius: 10px;
            }}
        """)

        # Boutons
        self.btn_send = QPushButton("Envoyer")
        self.btn_send.setObjectName("primary")
        self.btn_send.setStyleSheet(f"""
            QPushButton {{
                background: linear-gradient(90deg, rgba(109,213,255,.35), rgba(176,124,255,.35));
                border-color: rgba(255,255,255,.16);
            }}
        """)
        self.btn_clear = QPushButton("Effacer")

        buttons_lay = QHBoxLayout()
        buttons_lay.addWidget(self.btn_send)
        buttons_lay.addWidget(self.btn_clear)
        buttons_lay.addStretch()

        # Status
        self.status = QLabel("Prêt.")
        self.status.setStyleSheet(f"color: {COLORS['ok']}; font-size: 11px;")

        # Layout
        lay = QVBoxLayout(self)
        lay.addWidget(title)
        lay.addWidget(desc)
        lay.addWidget(self.history, 3)
        lay.addWidget(self.input, 1)
        lay.addLayout(buttons_lay)
        lay.addWidget(self.status)

        # Connexions
        self.btn_send.clicked.connect(self.on_send)
        self.btn_clear.clicked.connect(self.history.clear)
        self.input.installEventFilter(self)

    def eventFilter(self, obj, evt):
        if obj is self.input and evt.type() == 10:  # KeyPress
            if evt.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if evt.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier):
                    self.on_send()
                    return True
        return super().eventFilter(obj, evt)

    def on_send(self):
        msg = self.input.toPlainText().strip()
        if not msg:
            return
        self.sendRequested.emit(msg)
        self.input.clear()

    def add_message(self, role: str, text: str, provider: str = "?", trace: dict = None):
        """Ajouter message au historique"""
        if role == "user":
            html = f"<div style='background: rgba(109,213,255,.12); padding: 10px; border-radius: 10px; margin: 8px 0; border-left: 3px solid {COLORS['acc']}'><b>Toi:</b><br>{text.replace(chr(10), '<br>')}</div>"
        else:
            html = f"<div style='background: rgba(176,124,255,.08); padding: 10px; border-radius: 10px; margin: 8px 0; border-left: 3px solid {COLORS['acc2']}'><b>ÉlyonEU:</b><br>{text.replace(chr(10), '<br>')}"
            if trace:
                lp = trace.get("local_provider", "?")
                html += f"<br><span style='color: {COLORS['muted']}; font-size: 11px; margin-top: 4px; display: block;'>Provider: {lp}</span>"
            html += "</div>"

        self.history.append(html)
        self.history.verticalScrollBar().setValue(self.history.verticalScrollBar().maximum())

class MonitorWidget(QWidget):
    """Panneau Moniteur temps réel"""
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("📊 État & Journal")
        title.setFont(QFont("system-ui", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")

        self.state_view = QTextEdit()
        self.state_view.setReadOnly(True)
        self.state_view.setMaximumHeight(200)

        self.events_view = QTextEdit()
        self.events_view.setReadOnly(True)
        self.events_view.setStyleSheet(f"""
            QTextEdit {{
                background: {COLORS['panel2']};
                color: {COLORS['text']};
                border: 1px solid rgba(255,255,255,.08);
                border-radius: 10px;
            }}
        """)

        lay = QVBoxLayout(self)
        lay.addWidget(title)
        lay.addWidget(QLabel("État du système"), 0)
        lay.addWidget(self.state_view, 1)
        lay.addWidget(QLabel("Événements récents (derniers 20)"), 0)
        lay.addWidget(self.events_view, 2)

    def update_state(self, data: dict):
        """Mettre à jour affichage état"""
        if not data:
            self.state_view.setText("(non disponible)")
            return

        self_data = data.get("self", {})
        identity = self_data.get("identity", {})
        modes = self_data.get("modes", {})

        html = f"""
        <div style='font-size: 12px; line-height: 1.6;'>
        <b>{identity.get('name', '?')}</b> v{identity.get('ver', '?')}<br>
        Modes: Private={modes.get('private', 'N/A')} | Gov={modes.get('governance', '?')} | Source={modes.get('source', '?')}
        </div>
        """
        self.state_view.setHtml(html)

    def update_events(self, events: list):
        """Mettre à jour événements"""
        if not events:
            self.events_view.setText("(aucun événement)")
            return

        html_lines = []
        for ev in events[-20:]:
            ts = ev.get("ts", "?")
            typ = ev.get("type", "?")
            color = {
                "PING": COLORS['muted'],
                "CHAT": COLORS['acc'],
                "CHAT_TRACE": COLORS['acc2'],
                "CONTROL": COLORS['warn'],
                "BOOT": COLORS['ok'],
                "NOTE": COLORS['ok'],
            }.get(typ, COLORS['muted'])
            html_lines.append(f"<div style='color: {color}; font-size: 11px;'><code>{ts}</code> <b>{typ}</b></div>")

        self.events_view.setHtml("\n".join(html_lines))

class SecretariatWidget(QWidget):
    """Panneau Secrétariat (notes, résumé, mail)"""
    def __init__(self, parent=None):
        super().__init__(parent)

        title = QLabel("🗂️ Secrétariat — Assistante")
        title.setFont(QFont("system-ui", 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['text']};")

        self.notes = QPlainTextEdit()
        self.notes.setPlaceholderText("Écrire ici… (local)")

        self.btn_resume = QPushButton("🧠 Résumé auto")
        self.btn_actions = QPushButton("🧩 Extraire actions")
        self.btn_cr = QPushButton("🗒️ Compte-rendu auto")
        self.btn_mail = QPushButton("✉️ Générer mail")

        buttons_lay = QHBoxLayout()
        buttons_lay.addWidget(self.btn_resume)
        buttons_lay.addWidget(self.btn_actions)
        buttons_lay.addWidget(self.btn_cr)
        buttons_lay.addWidget(self.btn_mail)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(200)

        lay = QVBoxLayout(self)
        lay.addWidget(title)
        lay.addWidget(QLabel("Carnet de notes"))
        lay.addWidget(self.notes, 1)
        lay.addLayout(buttons_lay)
        lay.addWidget(QLabel("Résultat"))
        lay.addWidget(self.output, 1)

# ================== Main Application ==================

class ElyonDesktopPremium(QMainWindow):
    """Application Desktop Premium ÉlyonEU"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÉlyonEU — Application Desktop (Premium)")
        self.setGeometry(100, 100, 1400, 900)

        # Stylesheet global
        qapp = QApplication.instance()
        qapp.setStyle('Fusion')
        qapp.setStyleSheet(create_stylesheet())

        # Setup UI
        self.setup_ui()

        # Poller
        self.timer_events = QTimer()
        self.timer_events.timeout.connect(self.poll_events)
        self.timer_events.start(1500)

        self.timer_state = QTimer()
        self.timer_state.timeout.connect(self.poll_state)
        self.timer_state.start(3000)

        print("[desktop] Application started", flush=True)

    def setup_ui(self):
        """Construire l'interface"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ===== SIDEBAR =====
        sidebar = QWidget()
        sidebar.setMaximumWidth(280)
        sidebar.setStyleSheet(f"""
            QWidget {{
                background: linear-gradient(180deg, rgba(16,22,32,.95), rgba(12,18,27,.92));
                border-right: 1px solid rgba(255,255,255,.06);
            }}
        """)

        sidebar_lay = QVBoxLayout(sidebar)
        sidebar_lay.setContentsMargins(14, 14, 14, 14)
        sidebar_lay.setSpacing(12)

        # Brand
        brand = QLabel("ÉlyonEU")
        brand.setFont(QFont("system-ui", 18, QFont.Weight.Bold))
        brand.setStyleSheet(f"color: {COLORS['text']};")

        brand_desc = QLabel("Démo locale (présentation)")
        brand_desc.setObjectName("muted")
        brand_desc.setStyleSheet(f"color: {COLORS['muted']}; font-size: 11px;")

        sidebar_lay.addWidget(brand)
        sidebar_lay.addWidget(brand_desc)
        sidebar_lay.addSpacing(10)

        # Navigation buttons
        self.nav_chat = SidebarButton("💬", "Chat")
        self.nav_monitor = SidebarButton("📊", "Moniteur")
        self.nav_secretariat = SidebarButton("🗂️", "Secrétariat")
        self.nav_garde = SidebarButton("🛡️", "Garde-fous 6S/6R")
        self.nav_about = SidebarButton("ℹ️", "À propos")

        # Connecter les boutons à la navigation
        self.nav_chat.clicked.connect(lambda: self.show_panel(0))
        self.nav_monitor.clicked.connect(lambda: self.show_panel(1))
        self.nav_secretariat.clicked.connect(lambda: self.show_panel(2))
        self.nav_garde.clicked.connect(lambda: self.show_panel(3))
        self.nav_about.clicked.connect(lambda: self.show_panel(4))

        sidebar_lay.addWidget(self.nav_chat)
        sidebar_lay.addWidget(self.nav_monitor)
        sidebar_lay.addWidget(self.nav_secretariat)
        sidebar_lay.addWidget(self.nav_garde)
        sidebar_lay.addWidget(self.nav_about)
        sidebar_lay.addStretch()

        # Status badge
        self.status_badge = QLabel("● Mode privé")
        self.status_badge.setStyleSheet(f"color: {COLORS['ok']}; font-size: 11px;")
        sidebar_lay.addWidget(self.status_badge)

        # ===== MAIN CONTENT =====
        content = QWidget()
        content_lay = QVBoxLayout(content)
        content_lay.setContentsMargins(16, 16, 16, 16)

        # Stacked panels
        self.panels = QStackedWidget()

        self.panel_chat = ChatWidget()
        self.panel_monitor = MonitorWidget()
        self.panel_secretariat = SecretariatWidget()

        panel_garde = QWidget()
        garde_lay = QVBoxLayout(panel_garde)
        garde_title = QLabel("🛡️ Garde-fous 6S/6R")
        garde_title.setFont(QFont("system-ui", 14, QFont.Weight.Bold))
        garde_text = QLabel(
            "<b>6S:</b><br>✓ Sécurité | ✓ Sincérité | ✓ Sobriété | ✓ Sens | ✓ Soin | ✓ Soutenabilité<br><br>"
            "<b>6R:</b><br>✓ Règles | ✓ Respect | ✓ Responsabilité | ✓ Réversibilité | ✓ Robustesse | ✓ Redevabilité"
        )
        garde_text.setStyleSheet(f"color: {COLORS['text']}; line-height: 1.8;")
        garde_lay.addWidget(garde_title)
        garde_lay.addWidget(garde_text)
        garde_lay.addStretch()

        panel_about = QWidget()
        about_lay = QVBoxLayout(panel_about)
        about_title = QLabel("À propos")
        about_title.setFont(QFont("system-ui", 14, QFont.Weight.Bold))
        about_text = QLabel(
            "<b>ÉlyonEU</b><br>"
            "Application locale, gouvernance 6S/6R<br><br>"
            "<b>Version:</b> 0.4.1-premium-desktop<br>"
            "<b>API:</b> " + API
        )
        about_text.setStyleSheet(f"color: {COLORS['text']}; line-height: 1.8;")
        about_lay.addWidget(about_title)
        about_lay.addWidget(about_text)
        about_lay.addStretch()

        self.panels.addWidget(self.panel_chat)        # 0
        self.panels.addWidget(self.panel_monitor)     # 1
        self.panels.addWidget(self.panel_secretariat) # 2
        self.panels.addWidget(panel_garde)            # 3
        self.panels.addWidget(panel_about)            # 4

        content_lay.addWidget(self.panels)

        # Navigation connections
        self.nav_chat.clicked.connect(lambda: self.show_panel(0))
        self.nav_monitor.clicked.connect(lambda: self.show_panel(1))
        self.nav_secretariat.clicked.connect(lambda: self.show_panel(2))
        self.nav_garde.clicked.connect(lambda: self.show_panel(3))
        self.nav_about.clicked.connect(lambda: self.show_panel(4))

        # Chat connections
        self.panel_chat.sendRequested.connect(self.on_chat_send)

        # Assembly
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

        # Show first panel
        self.show_panel(0)

    def show_panel(self, idx: int):
        """Afficher un panneau"""
        self.panels.setCurrentIndex(idx)
        # Uncheck all then check the selected
        for btn in [self.nav_chat, self.nav_monitor, self.nav_secretariat, self.nav_garde, self.nav_about]:
            btn.setChecked(False)
        [self.nav_chat, self.nav_monitor, self.nav_secretariat, self.nav_garde, self.nav_about][idx].setChecked(True)

    def on_chat_send(self, msg: str):
        """Traiter envoi chat"""
        self.panel_chat.add_message("user", msg)
        self.panel_chat.status.setText("Envoi…")

        # Lancer appel async
        def send_async():
            try:
                payload = {"messages": [{"role": "user", "content": msg}]}
                resp = http_post("/chat", payload, timeout=20.0)
                if resp:
                    reply = resp.get("reply", "(pas de réponse)")
                    provider = resp.get("provider", "?")
                    trace = resp.get("trace", {})
                    QTimer.singleShot(0, lambda: self.on_chat_reply(reply, provider, trace))
                else:
                    QTimer.singleShot(0, lambda: self.on_chat_error("Erreur réseau"))
            except Exception as exc:
                QTimer.singleShot(0, lambda: self.on_chat_error(str(exc)))

        threading.Thread(target=send_async, daemon=True).start()

    def on_chat_reply(self, text: str, provider: str, trace: dict):
        """Réponse chat reçue"""
        self.panel_chat.add_message("assistant", text, provider, trace)
        self.panel_chat.status.setText("Prêt.")

    def on_chat_error(self, error: str):
        """Erreur chat"""
        self.panel_chat.status.setText(f"Erreur: {error}")
        self.panel_chat.add_message("assistant", f"⚠️ Erreur: {error}")

    def poll_events(self):
        """Poller les événements"""
        data = http_get("/events")
        if data:
            events = data.get("events", [])
            QTimer.singleShot(0, lambda: self.panel_monitor.update_events(events))

    def poll_state(self):
        """Poller l'état"""
        self_data = http_get("/self")
        if self_data:
            QTimer.singleShot(0, lambda: self.panel_monitor.update_state({"self": self_data.get("self", {})}))

def main():
    app = QApplication(sys.argv)
    window = ElyonDesktopPremium()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

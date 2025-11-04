# -*- coding: utf-8 -*-
"""ÉlyonEU Divine Desktop UI (PySide6).

A modern mainframe-inspired console featuring:
- Adaptive navigation mirroring the demonstration UI.
- Chat interface backed by the new FastAPI core.
- Live monitor for events and journal traces.
- UI rebuild workstation to submit layout specifications.
"""
from __future__ import annotations

import json
import sys
import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from PySide6 import QtCore, QtGui, QtWidgets

API_ROOT = QtCore.QProcessEnvironment.systemEnvironment().value("ELYON_API_URL", "http://127.0.0.1:8000")


# --------------------------- HTTP helpers ---------------------------
@dataclass
class HTTPResult:
    ok: bool
    data: Any
    error: Optional[str] = None


class APIClient:
    """Simple synchronous HTTP client with small helpers."""

    def __init__(self, base_url: str) -> None:
        self._base = base_url.rstrip("/")
        self._client = httpx.Client(timeout=10.0)

    def get(self, path: str) -> HTTPResult:
        try:
            resp = self._client.get(self._base + path)
            resp.raise_for_status()
            return HTTPResult(True, resp.json())
        except Exception as exc:
            return HTTPResult(False, None, str(exc))

    def post(self, path: str, payload: Dict[str, Any]) -> HTTPResult:
        try:
            resp = self._client.post(self._base + path, json=payload)
            resp.raise_for_status()
            return HTTPResult(True, resp.json())
        except Exception as exc:
            return HTTPResult(False, None, str(exc))

    def close(self) -> None:
        self._client.close()


# --------------------------- Widgets ---------------------------
class GradientFrame(QtWidgets.QFrame):
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # noqa: D401
        painter = QtGui.QPainter(self)
        gradient = QtGui.QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0.0, QtGui.QColor("#101826"))
        gradient.setColorAt(1.0, QtGui.QColor("#0a111b"))
        painter.fillRect(self.rect(), gradient)
        super().paintEvent(event)


class ChatPage(QtWidgets.QWidget):
    sendRequested = QtCore.Signal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("chatPage")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        header = QtWidgets.QLabel("<h2 style='color:#e8f2ff'>Chat — conversation naturelle</h2>")
        header.setObjectName("sectionTitle")
        layout.addWidget(header)

        self.stream = QtWidgets.QTextEdit(readOnly=True)
        self.stream.setObjectName("chatStream")
        layout.addWidget(self.stream, stretch=5)

        controls = QtWidgets.QHBoxLayout()
        self.input = QtWidgets.QPlainTextEdit()
        self.input.setPlaceholderText("Écrire un message…")
        self.input.setFixedHeight(80)
        controls.addWidget(self.input, stretch=5)

        buttons = QtWidgets.QVBoxLayout()
        self.btnSend = QtWidgets.QPushButton("Envoyer")
        self.btnSend.setObjectName("primaryButton")
        buttons.addWidget(self.btnSend)
        self.btnClear = QtWidgets.QPushButton("Effacer")
        buttons.addWidget(self.btnClear)
        buttons.addStretch(1)
        controls.addLayout(buttons)

        layout.addLayout(controls)

        self.btnSend.clicked.connect(self._emit_send)
        self.btnClear.clicked.connect(self.stream.clear)

    def _emit_send(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            return
        self.input.clear()
        self.append_user(text)
        self.sendRequested.emit(text)

    def append_user(self, text: str) -> None:
        self.stream.append(f"<div class='userMsg'>[Vous] {self._escape(text)}</div>")
        self._scroll_bottom()

    def append_assistant(self, text: str, provider: str) -> None:
        self.stream.append(
            f"<div class='assistantMsg'>[Élyôn · {provider}] {self._escape(text)}</div>"
        )
        self._scroll_bottom()

    def append_system(self, text: str) -> None:
        self.stream.append(f"<div class='systemMsg'>{self._escape(text)}</div>")
        self._scroll_bottom()

    def _scroll_bottom(self) -> None:
        cursor = self.stream.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.stream.setTextCursor(cursor)

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )


class MonitorPage(QtWidgets.QWidget):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("monitorPage")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("<h2 style='color:#e8f2ff'>Moniteur en temps réel</h2>"))

        self.identity = QtWidgets.QTextEdit(readOnly=True)
        self.identity.setObjectName("monitorIdentity")
        layout.addWidget(self.identity, stretch=1)

        self.events = QtWidgets.QTextEdit(readOnly=True)
        self.events.setObjectName("monitorEvents")
        layout.addWidget(self.events, stretch=2)

        self.journal = QtWidgets.QTextEdit(readOnly=True)
        self.journal.setObjectName("monitorJournal")
        layout.addWidget(self.journal, stretch=2)

    def set_identity(self, payload: Dict[str, Any]) -> None:
        self.identity.setPlainText(json.dumps(payload, ensure_ascii=False, indent=2))

    def set_events(self, events: List[Dict[str, Any]]) -> None:
        lines = [
            f"{e.get('ts','?')}  {e.get('type','?'):<10}  {json.dumps(e.get('data', {}), ensure_ascii=False)}"
            for e in events[-40:]
        ]
        self.events.setPlainText("\n".join(lines) or "(aucun événement)")

    def set_journal(self, entries: List[str]) -> None:
        self.journal.setPlainText("\n".join(entries[-80:]) or "(journal vide)")


class UIBuilderPage(QtWidgets.QWidget):
    rebuildRequested = QtCore.Signal(dict)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("uiBuilderPage")
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("<h2 style='color:#e8f2ff'>Atelier UI adaptatif</h2>"))

        self.specEdit = QtWidgets.QPlainTextEdit()
        self.specEdit.setObjectName("specEditor")
        self.specEdit.setPlaceholderText("Décrire la nouvelle UI (JSON)...")
        self.specEdit.setPlainText(
            json.dumps(
                {
                    "title": "Tableau principal",
                    "components": [
                        {"type": "card", "title": "Tâches", "metric": "3 en cours"},
                        {"type": "card", "title": "Actions IA", "metric": "1 proposée"},
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        layout.addWidget(self.specEdit, stretch=2)

        self.btnRebuild = QtWidgets.QPushButton("Lancer la reconstruction")
        self.btnRebuild.setObjectName("primaryButton")
        layout.addWidget(self.btnRebuild)

        self.result = QtWidgets.QTextEdit(readOnly=True)
        self.result.setObjectName("specResult")
        layout.addWidget(self.result, stretch=2)

        self.btnRebuild.clicked.connect(self._submit)

    def _submit(self) -> None:
        try:
            spec = json.loads(self.specEdit.toPlainText() or "{}")
        except json.JSONDecodeError as exc:
            self.result.setPlainText(f"Spécification invalide : {exc}")
            return
        self.rebuildRequested.emit(spec)

    def set_result(self, layout_payload: Dict[str, Any]) -> None:
        self.result.setPlainText(json.dumps(layout_payload, ensure_ascii=False, indent=2))


# --------------------------- Main Window ---------------------------
class DivineMainWindow(QtWidgets.QMainWindow):
    def __init__(self, api: APIClient) -> None:
        super().__init__()
        self.api = api
        self.setWindowTitle("ÉlyonEU Divine Console")
        self.resize(1280, 780)
        self._build_palette()
        self._build_ui()
        self._setup_timers()
        self._bootstrap()

    def _build_palette(self) -> None:
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor("#0b1018"))
        palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor("#f0f6ff"))
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor("#0f172a"))
        palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor("#121c32"))
        palette.setColor(QtGui.QPalette.Text, QtGui.QColor("#e2ecff"))
        palette.setColor(QtGui.QPalette.Button, QtGui.QColor("#17223a"))
        palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor("#dbe8ff"))
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor("#60a5fa"))
        self.setPalette(palette)

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        root_layout = QtWidgets.QHBoxLayout(central)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        # Sidebar navigation
        self.sidebar = QtWidgets.QFrame()
        self.sidebar.setObjectName("sidebar")
        sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(16)

        logo = QtWidgets.QLabel("<div style='font-size:20px;font-weight:700;color:#9cd5ff'>Élyôn</div>")
        sidebar_layout.addWidget(logo)

        self.btnChat = QtWidgets.QPushButton("💬  Chat")
        self.btnMonitor = QtWidgets.QPushButton("🧭  Moniteur")
        self.btnBuilder = QtWidgets.QPushButton("🛠️  Atelier UI")
        for btn in (self.btnChat, self.btnMonitor, self.btnBuilder):
            btn.setCheckable(True)
            btn.setObjectName("sidebarButton")
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch(1)

        root_layout.addWidget(self.sidebar, stretch=0)

        # Main stack
        self.mainFrame = GradientFrame()
        frame_layout = QtWidgets.QVBoxLayout(self.mainFrame)
        frame_layout.setContentsMargins(24, 24, 24, 24)
        frame_layout.setSpacing(18)

        self.banner = QtWidgets.QLabel("<h1 style='color:#e7f0ff'>Console principale</h1>")
        frame_layout.addWidget(self.banner)

        self.stack = QtWidgets.QStackedWidget()
        self.chatPage = ChatPage()
        self.monitorPage = MonitorPage()
        self.uiBuilderPage = UIBuilderPage()
        self.stack.addWidget(self.chatPage)
        self.stack.addWidget(self.monitorPage)
        self.stack.addWidget(self.uiBuilderPage)
        frame_layout.addWidget(self.stack)

        root_layout.addWidget(self.mainFrame, stretch=1)
        self.setCentralWidget(central)

        # Connections
        self.btnChat.clicked.connect(lambda: self._select_page(0))
        self.btnMonitor.clicked.connect(lambda: self._select_page(1))
        self.btnBuilder.clicked.connect(lambda: self._select_page(2))
        self._select_page(0)

        self.chatPage.sendRequested.connect(self._send_chat)
        self.uiBuilderPage.rebuildRequested.connect(self._rebuild_ui)

    def _setup_timers(self) -> None:
        self.timer_identity = QtCore.QTimer(self)
        self.timer_identity.setInterval(4000)
        self.timer_identity.timeout.connect(self._refresh_identity)

        self.timer_events = QtCore.QTimer(self)
        self.timer_events.setInterval(2000)
        self.timer_events.timeout.connect(self._refresh_events)

        self.timer_journal = QtCore.QTimer(self)
        self.timer_journal.setInterval(6000)
        self.timer_journal.timeout.connect(self._refresh_journal)

    def _bootstrap(self) -> None:
        self.chatPage.append_system("Connexion à l'API...")
        self.timer_identity.start()
        self.timer_events.start()
        self.timer_journal.start()
        self._refresh_identity()
        self._refresh_events()
        self._refresh_journal()
        self._load_latest_layout()

    # ---------------------- Navigation ----------------------
    def _select_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)
        for btn in (self.btnChat, self.btnMonitor, self.btnBuilder):
            btn.setChecked(False)
        (self.btnChat, self.btnMonitor, self.btnBuilder)[index].setChecked(True)

    # ---------------------- API interactions ----------------------
    def _send_chat(self, text: str) -> None:
        def _work() -> None:
            payload = {
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es ÉlyônEU, IA locale en gouvernance 6S/6R. Réponds en français, style clair.",
                    },
                    {"role": "user", "content": text},
                ]
            }
            result = self.api.post("/chat", payload)
            QtCore.QTimer.singleShot(
                0,
                lambda: self._handle_chat_result(result),
            )

        threading.Thread(target=_work, daemon=True).start()

    def _handle_chat_result(self, result: HTTPResult) -> None:
        if not result.ok:
            self.chatPage.append_assistant(result.error or "(erreur)", "erreur")
            return
        payload = result.data or {}
        reply = payload.get("reply", "(réponse vide)")
        provider = payload.get("provider", "local")
        self.chatPage.append_assistant(reply, provider)

    def _refresh_identity(self) -> None:
        result = self.api.get("/self")
        if result.ok:
            self.monitorPage.set_identity(result.data)
            title = result.data.get("identity", {}).get("name", "ÉlyonEU")
            self.banner.setText(f"<h1 style='color:#e7f0ff'>{title}</h1>")

    def _refresh_events(self) -> None:
        result = self.api.get("/events")
        if result.ok:
            events = result.data.get("events", [])
            self.monitorPage.set_events(events)

    def _refresh_journal(self) -> None:
        result = self.api.get("/journal/today")
        if result.ok:
            entries = result.data.get("entries", [])
            self.monitorPage.set_journal(entries)

    def _rebuild_ui(self, spec: Dict[str, Any]) -> None:
        def _work() -> None:
            result = self.api.post("/ui/rebuild", {"specification": spec})
            QtCore.QTimer.singleShot(0, lambda: self._handle_rebuild_result(result))

        threading.Thread(target=_work, daemon=True).start()

    def _handle_rebuild_result(self, result: HTTPResult) -> None:
        if not result.ok:
            self.uiBuilderPage.set_result({"error": result.error})
            return
        layout = result.data.get("layout") if isinstance(result.data, dict) else None
        self.uiBuilderPage.set_result(layout or {"error": "réponse inattendue"})

    def _load_latest_layout(self) -> None:
        result = self.api.get("/ui/layout")
        if result.ok:
            layout = result.data.get("layout", {})
            self.uiBuilderPage.set_result(layout)

    # ---------------------- Cleanup ----------------------
    def closeEvent(self, event: QtGui.QCloseEvent) -> None:  # noqa: D401
        self.api.close()
        super().closeEvent(event)


# --------------------------- CSS ---------------------------
STYLE_SHEET = """
QWidget { background-color: #0f172a; color: #e5ecff; font-family: 'Segoe UI', 'Roboto', sans-serif; }
#sidebar { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #121b2d, stop:1 #0d1522); border-radius: 16px; }
#sidebar QPushButton { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09); padding: 10px 14px; border-radius: 12px; text-align: left; }
#sidebar QPushButton:checked { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6dd5ff33, stop:1 #b07cff33); border-color: rgba(109,213,255,0.4); }
#sidebar QPushButton:hover { border-color: rgba(176,124,255,0.35); }
#primaryButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #6dd5ff, stop:1 #b07cff); border: none; padding: 12px 20px; border-radius: 12px; color: #0b1018; font-weight: bold; }
#primaryButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #7fe0ff, stop:1 #c192ff); }
#chatStream { background: rgba(13,20,35,0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 12px; }
.userMsg { background: rgba(109,213,255,0.18); border-radius: 12px; padding: 10px; margin: 4px 0; }
.assistantMsg { background: rgba(176,124,255,0.16); border-radius: 12px; padding: 10px; margin: 4px 0; }
.systemMsg { color: #9fb3d9; font-style: italic; margin: 4px 0; }
QPlainTextEdit, QTextEdit { border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 10px; background: rgba(11,15,26,0.95); }
#specEditor { min-height: 220px; }
#specResult { min-height: 200px; }
#monitorIdentity, #monitorEvents, #monitorJournal { background: rgba(13,20,35,0.9); }
"""


# --------------------------- Entrée ---------------------------
def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(STYLE_SHEET)

    client = APIClient(API_ROOT)
    window = DivineMainWindow(client)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
ÉlyonEU — Desktop App (PySide6 / Qt)
- Chat IA (gauche) + Moniteur (droite)
- Polling doux (events 1.5s, self 3s)
- Thread-safe: callbacks UI via QTimer.singleShot(0, ...)
"""
import json, os, sys, threading
import httpx
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QEvent, QTimer, Signal
from PySide6.QtGui import QColor, QPalette, QTextCursor

API = os.environ.get("ELYON_API_URL", "http://127.0.0.1:8000")

# --------------------- HTTP utils ---------------------
def http_get(path, timeout=5.0):
    try:
        with httpx.Client(timeout=timeout) as cli:
            r = cli.get(API + path); r.raise_for_status(); return r.json()
    except Exception:
        return None

def http_post(path, payload, timeout=20.0):
    try:
        with httpx.Client(timeout=timeout) as cli:
            r = cli.post(API + path, json=payload); r.raise_for_status(); return r.json()
    except Exception:
        return None

# --------------------- Widgets ---------------------
class ChatPanel(QtWidgets.QWidget):
    sendRequested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = QtWidgets.QTextEdit(readOnly=True)
        self.history.setStyleSheet(
            "QTextEdit{background:#0b1220;color:#e5e7eb;border:1px solid #1f2937;border-radius:10px;}"
        )
        self.input = QtWidgets.QPlainTextEdit()
        self.input.setPlaceholderText("Écris ta demande… (Ctrl+Entrée pour envoyer)")
        self.input.setStyleSheet(
            "QPlainTextEdit{background:#0a1424;color:#e5e7eb;border:1px solid #1f2937;border-radius:10px;}"
        )
        self.btnSend = QtWidgets.QPushButton("Envoyer")
        self.btnClear = QtWidgets.QPushButton("Effacer")
        self.lblProvider = QtWidgets.QLabel("—")
        self.lblProvider.setStyleSheet("color:#94a3b8")
        self.lblStatus = QtWidgets.QLabel("Prêt.")
        self.lblStatus.setStyleSheet("color:#38bdf8;font-style:italic")

        top = QtWidgets.QLabel("<b>Chat IA</b>"); top.setStyleSheet("color:#cfe6ff;")
        row = QtWidgets.QHBoxLayout(); row.addWidget(self.btnSend); row.addWidget(self.btnClear); row.addStretch(1)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addWidget(top); lay.addWidget(self.history, 3); lay.addWidget(self.input, 1); lay.addLayout(row)
        lay.addWidget(self.lblStatus); lay.addWidget(self.lblProvider)

        self.btnSend.clicked.connect(self.on_send)
        self.btnClear.clicked.connect(self.history.clear)
        self.input.installEventFilter(self)

    def eventFilter(self, obj, ev):
        if obj is self.input and ev.type() == QEvent.Type.KeyPress:
            modifiers = ev.modifiers()
            shortcut = Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.MetaModifier
            if (ev.key() in (Qt.Key_Return, Qt.Key_Enter)) and (modifiers & shortcut):
                self.on_send(); return True
        return super().eventFilter(obj, ev)

    def add_user(self, text:str):
        self.history.append(f"<div style='background:#12223a;padding:8px;border-radius:8px;margin:6px 0'>[USER] {self.escape(text)}</div>")
        self.scroll_bottom()

    def add_assistant(self, text:str):
        self.history.append(f"<div style='background:#111826;border:1px solid #1c2942;padding:8px;border-radius:8px;margin:6px 0'>[ASSISTANT] {self.escape(text)}</div>")
        self.scroll_bottom()

    def set_provider(self, name:str):
        self.lblProvider.setText(f"Fournisseur: {name}")

    def set_busy(self, active: bool, provider: str | None = None):
        self.btnSend.setDisabled(active)
        self.lblStatus.setText("Envoi en cours…" if active else "Prêt.")
        if not active:
            self.btnSend.setDisabled(False)
            if provider:
                self.set_provider(provider)

    def on_send(self):
        text = self.input.toPlainText().strip()
        if text:
            self.input.clear()
            self.set_busy(True)
            self.sendRequested.emit(text)

    def scroll_bottom(self):
        cur = self.history.textCursor(); cur.movePosition(QTextCursor.MoveOperation.End); self.history.setTextCursor(cur)

    @staticmethod
    def escape(s:str)->str:
        return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

class StatusPanel(QtWidgets.QWidget):
    pauseRequested = Signal()
    resumeRequested = Signal()
    intervalSetRequested = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btnPause = QtWidgets.QPushButton("Pause")
        self.btnResume = QtWidgets.QPushButton("Resume")
        self.spInterval = QtWidgets.QDoubleSpinBox(); self.spInterval.setRange(0.2, 3600.0); self.spInterval.setSingleStep(0.1); self.spInterval.setValue(1.5)
        self.btnApply = QtWidgets.QPushButton("Appliquer")

        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.btnPause); row.addWidget(self.btnResume)
        row.addWidget(QtWidgets.QLabel("Intervalle (s):")); row.addWidget(self.spInterval); row.addWidget(self.btnApply); row.addStretch(1)

        self.selfView = QtWidgets.QPlainTextEdit(readOnly=True)
        self.selfView.setStyleSheet("QPlainTextEdit{background:#08101a;color:#d1e7ff;border:1px solid #1f2937;border-radius:10px;}")
        self.eventsView = QtWidgets.QPlainTextEdit(readOnly=True)
        self.eventsView.setStyleSheet("QPlainTextEdit{background:#08101a;color:#d1e7ff;border:1px solid #1f2937;border-radius:10px;}")

        lay = QtWidgets.QVBoxLayout(self)
        t = QtWidgets.QLabel("<b>Statut</b>"); t.setStyleSheet("color:#cfe6ff;")
        lay.addWidget(t); lay.addLayout(row)
        lay.addWidget(QtWidgets.QLabel("Identité")); lay.addWidget(self.selfView, 1)
        lay.addWidget(QtWidgets.QLabel("Événements")); lay.addWidget(self.eventsView, 2)

        self.btnPause.clicked.connect(self.pauseRequested.emit)
        self.btnResume.clicked.connect(self.resumeRequested.emit)
        self.btnApply.clicked.connect(lambda: self.intervalSetRequested.emit(float(self.spInterval.value())))

    def set_interval(self, v:float):
        self.spInterval.setValue(float(v))

    def set_self(self, j:dict|None):
        payload = j or {"identity": {"name": "(indisponible)"}}
        txt = json.dumps(payload, indent=2, ensure_ascii=False)
        print("[desktop] /self ->", txt, flush=True)
        self.selfView.setPlainText(txt)

    def set_events(self, arr:list[dict]|None):
        self.eventsView.clear()
        if not arr:
            self.eventsView.setPlainText("(aucun événement)"); print("[desktop] /events -> aucun", flush=True); return
        lines = []
        for e in arr[-30:][::-1]:
            ts = e.get("ts",""); typ = e.get("type",""); dat = e.get("data",{})
            lines.append(f"{ts}  {typ:<8} {json.dumps(dat, ensure_ascii=False)}")
        print("[desktop] /events ->", " | ".join(lines[-3:]), flush=True)
        self.eventsView.setPlainText("\n".join(lines))

# --------------------- Main ---------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ÉlyonEU — Desktop"); self.resize(1100, 720)

        self.chat = ChatPanel(); self.stat = StatusPanel()
        self.splitter = QtWidgets.QSplitter()
        self.splitter.addWidget(self.chat)
        self.splitter.addWidget(self.stat)
        self.splitter.setStretchFactor(0, 2)
        self.splitter.setStretchFactor(1, 1)

        central = QtWidgets.QWidget(); lay = QtWidgets.QVBoxLayout(central)
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("<b>ÉlyonEU</b> — Chat + Moniteur"); title.setStyleSheet("color:#e5e7eb;")
        header.addWidget(title); header.addStretch(1)
        lay.addLayout(header); lay.addWidget(self.splitter, 1)
        self.setCentralWidget(central)

        # timers
        self.timer_events = QTimer(self)
        self.timer_events.setInterval(1500)
        self.timer_events.timeout.connect(self.refresh_events)
        self.timer_self = QTimer(self)
        self.timer_self.setInterval(3000)
        self.timer_self.timeout.connect(self.refresh_self)

        # signals
        self.chat.sendRequested.connect(self.on_send_chat)
        self.stat.pauseRequested.connect(self.on_pause)
        self.stat.resumeRequested.connect(self.on_resume)
        self.stat.intervalSetRequested.connect(self.on_set_interval)

        # first load
        self.chat.add_assistant("Bonjour, je suis ÉlyonEU. Décris-moi ta situation pour que je t'aide à l'étape suivante.")
        QTimer.singleShot(200, self.refresh_control)
        QTimer.singleShot(250, self.refresh_self)
        QTimer.singleShot(300, self.refresh_events)
        self.timer_events.start()
        self.timer_self.start()
        QTimer.singleShot(150, self.chat.input.setFocus)
        QTimer.singleShot(500, self._adapt_layout)

    # --- Actions ---
    def on_pause(self) -> None:
        threading.Thread(target=lambda: http_post("/control", {"run_pings": False}), daemon=True).start()
        QTimer.singleShot(400, self.refresh_control)

    def on_resume(self) -> None:
        threading.Thread(target=lambda: http_post("/control", {"run_pings": True}), daemon=True).start()
        QTimer.singleShot(400, self.refresh_control)

    def on_set_interval(self, v: float) -> None:
        threading.Thread(target=lambda: http_post("/control", {"interval_sec": float(v)}), daemon=True).start()
        QTimer.singleShot(400, self.refresh_control)

    def on_send_chat(self, text: str) -> None:
        self.chat.add_user(text)

        def _work() -> None:
            try:
                payload = {
                    "messages": [
                        {"role": "system", "content": "Tu es ÉlyonEU, IA locale éthique. Réponds en français, clair et utile."},
                        {"role": "user", "content": text},
                    ]
                }
                res = http_post("/chat", payload)
                if res is None:
                    reply = "(API indisponible)"
                    provider = "ui"
                else:
                    reply = res.get("reply", "(pas de réponse)")
                    provider = res.get("provider", "?")
            except Exception as exc:
                reply = f"(erreur locale) {exc}"
                provider = "ui"
            finally:
                QTimer.singleShot(0, lambda r=reply, p=provider: (self.chat.add_assistant(r), self.chat.set_busy(False, p)))

        threading.Thread(target=_work, daemon=True).start()

    # --- Pollers (thread -> UI via singleShot) ---
    def refresh_control(self) -> None:
        def _work() -> None:
            j = http_get("/control") or {}
            iv = float(j.get("interval_sec", 1.5) or 1.5)
            QTimer.singleShot(0, lambda ivv=iv: self.stat.set_interval(ivv))

        threading.Thread(target=_work, daemon=True).start()

    def refresh_self(self) -> None:
        def _work() -> None:
            j = http_get("/self") or {}
            QTimer.singleShot(0, lambda jj=j: self.stat.set_self(jj))

        threading.Thread(target=_work, daemon=True).start()

    def refresh_events(self) -> None:
        def _work() -> None:
            arr = (http_get("/events") or {}).get("events") or []
            QTimer.singleShot(0, lambda a=arr: self.stat.set_events(a))

        threading.Thread(target=_work, daemon=True).start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._adapt_layout()

    def _adapt_layout(self) -> None:
        orientation = Qt.Orientation.Horizontal if self.width() >= 960 else Qt.Orientation.Vertical
        if self.splitter.orientation() != orientation:
            self.splitter.setOrientation(orientation)
        if orientation == Qt.Orientation.Vertical:
            top = max(220, int(self.height() * 0.55))
            bottom = max(180, int(self.height() * 0.45))
            self.splitter.setSizes([top, bottom])
        else:
            left = max(400, int(self.width() * 0.6))
            right = max(320, int(self.width() * 0.4))
            self.splitter.setSizes([left, right])

# --------------------- Entrée ---------------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor("#0f172a"))
    pal.setColor(QPalette.ColorRole.WindowText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Base, QColor("#0b1220"))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor("#0b1220"))
    pal.setColor(QPalette.ColorRole.Text, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Button, QColor("#0b1220"))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor("#ffffff"))
    pal.setColor(QPalette.ColorRole.Highlight, QColor("#60a5fa"))
    app.setPalette(pal)

    w = MainWindow(); w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

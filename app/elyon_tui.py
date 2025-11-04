# -*- coding: utf-8 -*-
"""
ÉlyonEU — Application TUI (mainframe-style) avec chat intégré
Compat Textual large (pas d'args markup/highlight/wrap aux logs)
"""
import json, os
import httpx
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Label
from textual.containers import Horizontal, Vertical

# Compat: choisir un widget de log dispo (TextLog > Log > RichLog)
try:
    from textual.widgets import TextLog as LogWidget
except Exception:
    try:
        from textual.widgets import Log as LogWidget
    except Exception:
        from textual.widgets import RichLog as LogWidget

API = os.environ.get("ELYON_API_URL", "http://127.0.0.1:8000")

class ChatPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("CHAT IA", id="title")
        yield LogWidget(id="chatlog")
        yield Input(placeholder="Écris ta demande… (Ctrl+Entrée pour envoyer)", id="chatinput")
        yield Horizontal(Button("Envoyer", id="send"), Button("Effacer", id="clear"), id="chatbuttons")
        yield Label("—", id="provider")

class StatusPanel(Vertical):
    def compose(self) -> ComposeResult:
        yield Label("STATUT", id="title")
        yield Horizontal(
            Button("Pause", id="pause"),
            Button("Resume", id="resume"),
            Label("Intervalle (s):"),
            Input(placeholder="1.5", id="interval", value="1.5"),
            Button("Appliquer", id="apply"),
        )
        yield Label("Identité", id="subtitle_self")
        yield LogWidget(id="selflog")
        yield Label("Événements", id="subtitle_ev")
        yield LogWidget(id="evlog")

class ElyonTUI(App):
    CSS = """
    Screen { layout: vertical; }
    #title { color: cyan; }
    #subtitle_self, #subtitle_ev { color: #7aa2f7; }
    #provider { color: #7aa2f7; }
    #chatlog, #selflog, #evlog { border: round #3b4261; height: 1fr; }
    #chatinput { border: round #3b4261; }
    .container { height: 1fr; }
    """

    BINDINGS = [
        ("p", "pause", "Pause"),
        ("r", "resume", "Resume"),
        ("+", "iv_up", "+1s"),
        ("-", "iv_down", "-1s"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(classes="container"):
            yield ChatPanel(id="chat")
            yield StatusPanel(id="stat")
        yield Footer()

    async def on_mount(self) -> None:
        # rafraîchissements périodiques
        self.set_interval(1.5, self.refresh_events)
        self.set_interval(3.0, self.refresh_self)
        # focus saisie
        self.query_one("#chatinput", Input).focus()
        # premières MAJ
        await self.refresh_self()
        await self.refresh_events()
        await self.refresh_control()

    # helpers
    def chatlog(self): return self.query_one("#chatlog", LogWidget)
    def selflog(self): return self.query_one("#selflog", LogWidget)
    def evlog(self):   return self.query_one("#evlog", LogWidget)

    # HTTP
    async def api_get(self, path: str):
        try:
            async with httpx.AsyncClient(timeout=5.0) as cli:
                r = await cli.get(API + path); r.raise_for_status(); return r.json()
        except Exception:
            return None

    async def api_post(self, path: str, payload: dict):
        try:
            async with httpx.AsyncClient(timeout=20.0) as cli:
                r = await cli.post(API + path, json=payload); r.raise_for_status(); return r.json()
        except Exception:
            return None

    # MAJ panneaux
    async def refresh_self(self):
        data = await self.api_get("/self")
        self.selflog().clear()
        payload = data or {"identity": {"name": "(indisponible)"}}
        self.selflog().write(json.dumps(payload, indent=2, ensure_ascii=False))

    async def refresh_events(self):
        data = await self.api_get("/events")
        self.evlog().clear()
        evs = (data.get("events") if data else [])[-30:][::-1]
        if not evs:
            self.evlog().write("(aucun événement)")
            return
        for e in evs:
            ts = e.get("ts",""); typ = e.get("type",""); dat = e.get("data",{})
            self.evlog().write(f"{ts}  {typ:<8} {json.dumps(dat, ensure_ascii=False)}")

    async def refresh_control(self):
        data = await self.api_get("/control")
        if data:
            self.query_one("#interval", Input).value = str(data.get("interval_sec", 1.5))

    # actions
    async def action_pause(self):
        await self.api_post("/control", {"run_pings": False})
        await self.refresh_control()

    async def action_resume(self):
        await self.api_post("/control", {"run_pings": True})
        await self.refresh_control()

    async def action_iv_up(self):
        inp = self.query_one("#interval", Input)
        try:
            current = float(inp.value or "1.5")
        except ValueError:
            current = 1.5
        v = max(0.2, min(3600.0, current + 0.5))
        await self.api_post("/control", {"interval_sec": v})
        await self.refresh_control()

    async def action_iv_down(self):
        inp = self.query_one("#interval", Input)
        try:
            current = float(inp.value or "1.5")
        except ValueError:
            current = 1.5
        v = max(0.2, min(3600.0, current - 0.5))
        await self.api_post("/control", {"interval_sec": v})
        await self.refresh_control()

    async def on_button_pressed(self, ev: Button.Pressed) -> None:
        bid = ev.button.id or ""
        if bid == "send":
            await self.send_chat()
        elif bid == "clear":
            self.chatlog().clear()
        elif bid == "pause":
            await self.action_pause()
        elif bid == "resume":
            await self.action_resume()
        elif bid == "apply":
            try:
                raw = self.query_one("#interval", Input).value or "1.5"
                vv = max(0.2, min(3600.0, float(raw)))
                await self.api_post("/control", {"interval_sec": vv})
                await self.refresh_control()
            except Exception:
                pass

    async def on_input_submitted(self, ev: Input.Submitted) -> None:
        if ev.input.id == "chatinput":
            await self.send_chat()

    async def send_chat(self):
        inp = self.query_one("#chatinput", Input)
        text = (inp.value or "").strip()
        if not text: return
        inp.value = ""
        self.chatlog().write(f"[USER] {text}")
        payload = {"messages": [
            {"role":"system","content":"Tu es ÉlyonEU, IA locale éthique. Réponds en français, clair et utile."},
            {"role":"user","content": text}
        ]}
        res = await self.api_post("/chat", payload)
        if not res:
            self.chatlog().write("[ASSISTANT] (erreur réseau)")
            return
        self.query_one("#provider", Label).update(f"Fournisseur: {res.get('provider','?')}")
        self.chatlog().write(f"[ASSISTANT] {res.get('reply','(vide)')}")

if __name__ == "__main__":
    ElyonTUI().run()

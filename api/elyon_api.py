# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio, threading, time, os, json, requests, sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.providers.generative_core_provider import GenerativeCoreProvider

APP_NAME = "ElyonEU (local)"
APP_VER  = "0.3.0"  # UI profiles + chat

# Répertoires
DATA_DIR    = ROOT / "data"
JOURNAL_DIR = ROOT / "journal"
STATIC_DIR  = Path(__file__).resolve().parent / "static"
UI_DIR      = ROOT / "ui"
CFG_UI      = ROOT / "config" / "ui_profile.json"
CFG_CHAT    = ROOT / "config" / "chat_backend.json"

# État / événements
RUN_PINGS: bool = True
EVENTS: list[dict] = []
MAX_EVENTS: int = 2000
DEFAULT_PING_INTERVAL = 1
os.environ.setdefault("ELYON_PING_INTERVAL", str(DEFAULT_PING_INTERVAL))
_PRODUCER_STARTED = False

SELF = {
    "identity": {"name": APP_NAME, "ver": APP_VER},
    "modes": {"private": True, "governance": "6S/6R", "source": "local"},
}

app = FastAPI(title="ElyonEU API", version=APP_VER)
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# provider cache (lazy)
_GEN_PROVIDER: Optional[GenerativeCoreProvider] = None


def get_gen_provider() -> GenerativeCoreProvider:
    global _GEN_PROVIDER
    if _GEN_PROVIDER is None:
        _GEN_PROVIDER = GenerativeCoreProvider()
    return _GEN_PROVIDER

# Mount local routers (if present)
try:
    from api.routers.generative import router as generative_router
    app.include_router(generative_router)
except Exception:
    # router optional — continue if not present
    pass


# ---------- utilitaires ----------
def ensure_dirs():
    for p in (DATA_DIR, JOURNAL_DIR, UI_DIR, STATIC_DIR, CFG_UI.parent, CFG_CHAT.parent):
        p.mkdir(parents=True, exist_ok=True)


def start_producer_once():
    global _PRODUCER_STARTED
    if _PRODUCER_STARTED:
        return
    ensure_dirs()
    threading.Thread(target=producer, daemon=True).start()
    log_event("BOOT", {"app": APP_NAME, "ver": APP_VER})
    _PRODUCER_STARTED = True

def log_event(kind: str, payload: Optional[dict] = None):
    e = {"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "type": kind, "data": payload or {}}
    EVENTS.append(e)
    if len(EVENTS) > MAX_EVENTS:
        del EVENTS[: MAX_EVENTS // 2]
    try:
        fp = JOURNAL_DIR / f"journal_{time.strftime('%Y%m%d')}.jsonl"
        with fp.open("a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    except Exception:
        pass

def read_default_ui() -> str:
    try:
        if CFG_UI.exists():
            j = json.loads(CFG_UI.read_text(encoding="utf-8"))
            v = (j.get("default_ui") or "chat").strip().lower()
            return v if v in {"divine", "normal", "moniteur", "chat"} else "chat"
    except Exception:
        pass
    return "chat"

def ui_file_for(name: str) -> Path:
    name = (name or "").strip().lower()
    if name not in {"divine", "normal", "moniteur", "chat"}:
        name = read_default_ui()
    return (UI_DIR / name / "index.html")

def load_chat_cfg():
    cfg = {"provider":"lmstudio","base_url":"http://127.0.0.1:1234/v1","model":"mistral-7b-instruct-v0.1","api_key":""}
    try:
        if CFG_CHAT.exists():
            user = json.loads(CFG_CHAT.read_text(encoding="utf-8"))
            cfg.update({k:v for k,v in user.items() if v is not None})
    except Exception:
        pass
    return cfg


# ---------- routes ----------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    qp_ui = request.query_params.get("ui")
    if qp_ui:
        target = ui_file_for(qp_ui)
        if target.exists():
            return HTMLResponse(target.read_text(encoding="utf-8"))
        return RedirectResponse(url="/ui")
    target = ui_file_for(read_default_ui())
    if target.exists():
        return HTMLResponse(target.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ElyonEU API</h1><p>UI introuvable (ui/{divine|normal|moniteur|chat}/index.html)</p>")

@app.get("/ui", response_class=HTMLResponse)
def ui_switcher():
    html = f"""
    <!doctype html><meta charset="utf-8"><title>ElyonEU — UI selector</title>
    <body style="font-family:Segoe UI,system-ui;background:#0f172a;color:#e5e7eb">
    <h1>Sélecteur d'UI</h1>
    <p><a href="/?ui=chat">UI Chat</a> · <a href="/?ui=divine">UI Divine</a> · <a href="/?ui=normal">UI Normale</a> · <a href="/?ui=moniteur">UI Moniteur</a></p>
    <p>Profil par défaut actuel : <b>{read_default_ui()}</b></p>
    </body>
    """
    return HTMLResponse(html)

@app.get("/health")
def health():
    return {"status": "ok", "ts": time.time()}

@app.get("/self")
def self_state():
    return {"self": SELF}

@app.get("/events")
def events():
    return {"events": EVENTS[-100:]}

@app.post("/journal")
async def journal_entry(req: Request):
    body = await req.json()
    log_event("NOTE", body)
    return {"ok": True}

# --- contrôle heartbeat ---
@app.get("/control")
def get_control():
    try:
        iv = int(float(os.environ.get("ELYON_PING_INTERVAL", str(DEFAULT_PING_INTERVAL))))
    except ValueError:
        iv = DEFAULT_PING_INTERVAL
    return {"run_pings": RUN_PINGS, "interval_sec": iv}

@app.post("/control")
async def set_control(req: Request):
    global RUN_PINGS
    body = await req.json()
    if "run_pings" in body:
        RUN_PINGS = bool(body["run_pings"])
        log_event("CONTROL", {"run_pings": RUN_PINGS})
    if "interval_sec" in body:
        try:
            v = max(1, min(int(body["interval_sec"]), 3600))
            os.environ["ELYON_PING_INTERVAL"] = str(v)
            log_event("CONTROL", {"interval_sec": v})
        except Exception:
            pass
    return get_control()

# --- endpoint CHAT ---
@app.post("/chat")
async def chat(req: Request):
    """
    Input: { "messages": [ { "role":"user|system|assistant", "content":"..." }, ... ] }
    Output: { "reply": "..." , "provider":"lmstudio|local_fallback" }
    """
    data = await req.json()
    msgs = data.get("messages") or []
    cfg = load_chat_cfg()

    # Tentative LM Studio (OpenAI compatible)
    try:
        url = f"{cfg['base_url'].rstrip('/')}/chat/completions"
        headers = {"Content-Type":"application/json"}
        if cfg.get("api_key"):
            headers["Authorization"] = f"Bearer {cfg['api_key']}"
        payload = {
            "model": cfg.get("model",""),
            "messages": msgs,
            "temperature": data.get("temperature", 0.3),
            "max_tokens": data.get("max_tokens", 512),
        }
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        if r.ok:
            j = r.json()
            reply = j.get("choices",[{}])[0].get("message",{}).get("content","").strip()
            if reply:
                log_event("CHAT", {"provider":"lmstudio","len":len(reply)})
                return JSONResponse({"reply": reply, "provider":"lmstudio"})
    except Exception as ex:
        pass

    # Fallback local (mode dégradé)
    last_user = next((m["content"] for m in reversed(msgs) if m.get("role")=="user"), "")
    try:
        prov = get_gen_provider()
        result = prov.generate(last_user or "Bonjour", mode=data.get("mode", "normal"))
        reply = result.text
        provider = f"gen_{result.used}"
        log_event("CHAT", {"provider": provider, "len": len(reply)})
        return JSONResponse({"reply": reply, "provider": provider})
    except Exception as ex:
        fallback = f"(mode dégradé local) Tu as dit : {last_user[:400]}"
        log_event("CHAT", {"provider":"local_fallback","len":len(fallback),"err":str(ex)[:200]})
        return JSONResponse({"reply": fallback, "provider":"local_fallback"})


# ---------- heartbeat ----------
def producer():
    n = 0
    while True:
        try:
            interval = float(os.environ.get("ELYON_PING_INTERVAL", str(DEFAULT_PING_INTERVAL)))
        except ValueError:
            interval = DEFAULT_PING_INTERVAL
        if RUN_PINGS:
            n += 1
            log_event("PING", {"n": n})
        time.sleep(max(0.1, interval))


@app.on_event("startup")
async def on_startup():
    start_producer_once()

def main():
    start_producer_once()
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig

    cfg = HyperConfig()
    cfg.bind = ["127.0.0.1:8000"]
    cfg.loglevel = "info"
    asyncio.run(serve(app, cfg))

if __name__ == "__main__":
    main()

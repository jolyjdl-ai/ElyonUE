# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio, threading, time, os, json, sys
import httpx
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

APP_NAME = "ElyonEU (local)"
APP_VER  = "0.3.0"  # UI profiles + chat

# Répertoires
DATA_DIR    = ROOT / "data"
JOURNAL_DIR = ROOT / "journal"
STATIC_DIR  = Path(__file__).resolve().parent / "static"
UI_DIR      = ROOT / "ui"
WEB_UI_FILE = UI_DIR / "chat" / "index.html"
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

# génération locale simplifiée (fallback)
def local_generate(prompt: str, mode: str = "normal") -> tuple[str, str]:
    text = prompt.strip()
    if not text:
        return ("(mode local) Décris ta situation pour que je propose une prochaine étape alignée 6S/6R.", "gen_local")

    low = text.lower()
    if "qui es-tu" in low or "qui es tu" in low:
        return (
            "Je suis ÉlyonEU, instance locale gouvernée 6S/6R. Je journalise en JSONL et t’aide à piloter les flux internes sans cloud.",
            "gen_local",
        )
    if "quelle est ta mission" in low:
        return (
            "Ma mission est de guider l’opérateur ou l’opératrice vers la prochaine action concrète, avec sûreté, souveraineté et responsabilité.",
            "gen_local",
        )

    if mode == "resume":
        body = f"Synthèse rapide : {text[:240]}"
    elif mode == "actions":
        body = (
            "Actions suggérées :\n"
            "1. Identifier les données utiles.\n"
            "2. Vérifier le journal local pour les événements récents.\n"
            "3. Proposer une étape alignée 6S/6R."
        )
    else:
        body = (
            "Analyse locale : je te recommande de vérifier les journaux récents, d’expliciter le besoin précis et"
            " de formuler la prochaine action opérationnelle."
            f" (Entrée reçue: {text[:200]})"
        )
    return (body, "gen_local")

# Mount local routers (if present)
try:
    from api.routers.generative import router as generative_router  # type: ignore[import]
    app.include_router(generative_router)
except Exception:
    # router optional — continue if not present
    pass


# ---------- utilitaires ----------
def ensure_dirs():
    for p in (DATA_DIR, JOURNAL_DIR, UI_DIR, STATIC_DIR, CFG_CHAT.parent):
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
def home():
    if WEB_UI_FILE.exists():
        return HTMLResponse(WEB_UI_FILE.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>ElyonEU API</h1><p>Interface web introuvable (ui/chat/index.html)</p>")

@app.get("/ui", response_class=HTMLResponse)
def ui_entrypoint():
    return home()

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
    print("[api] /chat reçu", len(msgs), "messages", flush=True)

    # Tentative LM Studio (OpenAI compatible)
    try:
        url = f"{cfg['base_url'].rstrip('/')}/chat/completions"
        headers = {"Content-Type": "application/json"}
        if cfg.get("api_key"):
            headers["Authorization"] = f"Bearer {cfg['api_key']}"
        payload = {
            "model": cfg.get("model", ""),
            "messages": msgs,
            "temperature": data.get("temperature", 0.3),
            "max_tokens": data.get("max_tokens", 512),
        }
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0, read=18.0)) as client:
            r = await client.post(url, headers=headers, json=payload)
        if r.is_success:
            j = r.json()
            reply = j.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if reply:
                log_event("CHAT", {"provider": "lmstudio", "len": len(reply)})
                return JSONResponse({"reply": reply, "provider": "lmstudio"})
    except Exception:
        pass

    # Fallback local (mode dégradé)
    last_user = next((m["content"] for m in reversed(msgs) if m.get("role") == "user"), "")
    reply, provider = local_generate(last_user or "Bonjour", mode=data.get("mode", "normal"))
    log_event("CHAT", {"provider": provider, "len": len(reply)})
    return JSONResponse({"reply": reply, "provider": provider})


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
    asyncio.run(serve(app, cfg))  # type: ignore[arg-type]

if __name__ == "__main__":
    main()

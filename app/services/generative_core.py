# -*- coding: utf-8 -*-
"""
Élyôn EU — Generative Core (adapté pour ElyonEU)

Copie du canvas POC (serve as a standalone FastAPI app when run directly).
Lorsque monté comme module dans l'app principale, on importe les handlers
(fonctions `generate`, `summarize`, `extract_actions`, `status`, `update_config`).

Lancement (dev) :
    hypercorn app.services.generative_core:app --reload --bind 0.0.0.0:8061
"""
from __future__ import annotations
import os, re, json, time, threading, uuid, hashlib, queue, random, sys
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from .llm_client import generate as llm_generate
except ImportError:  # pragma: no cover - fallback lors de l’exécution directe
    from app.services.llm_client import generate as llm_generate  # type: ignore[import]
from pydantic import BaseModel, Field
from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import JSONResponse
# Safety: éviter conflits d'encodage/locale et empêcher l'exécution au moment de l'import
try:
    import locale
    try:
        locale.setlocale(locale.LC_ALL, "")
    except Exception:
        pass
except Exception:
    pass

try:
    import httpx
except Exception:
    httpx = None  # fallback sans httpx → on simulera

# ===============================
# Config & État
# ===============================

class Config(BaseModel):
    allow_cloud: bool = False
    cloud_model: str = "gpt-5"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    enable_autonomy: bool = True
    autonomy_min_interval_s: int = 900
    sixs_threshold: int = 3
    log_dir: str = os.path.abspath("./data/logs")
    events_max: int = 200
    project_tag: str = "ElyonEU"

class State(BaseModel):
    started_at: str
    last_act: str = ""
    mode: str = "IDLE"
    last_error: str = ""
    total_requests: int = 0
    total_autonomous: int = 0

CFG = Config()
STATE = State(started_at=datetime.utcnow().isoformat())
EVENTS: List[Dict[str, Any]] = []
EVENTS_LOCK = threading.Lock()
EVENT_Q: "queue.Queue[Dict[str, Any]]" = queue.Queue()

os.makedirs(CFG.log_dir, exist_ok=True)

# Override config from environment when present (helps local LM Studio testing)
CFG.openai_base_url = os.getenv("LMSTUDIO_URL", CFG.openai_base_url)
api_key_env = os.getenv("ELYON_CHAT_API_KEY")
if api_key_env:
    CFG.openai_api_key = api_key_env
else:
    CFG.openai_api_key = os.getenv("OPENAI_API_KEY", CFG.openai_api_key)
if os.getenv("ALLOW_CLOUD") is not None:
    try:
        CFG.allow_cloud = str(os.getenv("ALLOW_CLOUD")).lower() in ("1", "true", "yes")
    except Exception:
        pass

# ===============================
# Utilitaires
# ===============================

def now_iso() -> str:
    return datetime.utcnow().isoformat()


def log_event(kind: str, detail: Dict[str, Any]):
    data = {"id": str(uuid.uuid4()), "t": now_iso(), "kind": kind, "detail": detail}
    with EVENTS_LOCK:
        EVENTS.append(data)
        if len(EVENTS) > CFG.events_max:
            del EVENTS[: len(EVENTS) - CFG.events_max]
    try:
        path = os.path.join(CFG.log_dir, f"events_{datetime.utcnow().date()}.log")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception:
        pass


def sha256(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# ===============================
# Garde‑fous 6S/6R (simplifié)
# ===============================

BLOCK_PATTERNS = [
    # contenus violents / illégaux / destructeurs
    r"\bviolence\b",
    r"\béradication\b",
    r"\bcréer une arme\b",
    r"\bsupprimer\b",
    r"\brm\s*-rf\b",
    r"\bdelete\b",
    r"\bdrop\b",
    r"\bexfiltrat\w*\b",
    r"\bpirat\w*\b",
]


def ethics_filter(text: str) -> bool:
    low = text.lower()
    for pat in BLOCK_PATTERNS:
        if re.search(pat, low):
            return False
    return True


def guard_or_raise(text: str):
    if not ethics_filter(text):
        STATE.mode = "HALT"
        STATE.last_error = "Violation garde‑fous (6S/6R)."
        log_event("halt", {"reason": STATE.last_error})
        raise HTTPException(status_code=400, detail="Requête bloquée par les garde‑fous 6S/6R.")

# ===============================
# RAG minimal (stub)
# ===============================

class RAGStub:
    def search(self, query: str, k: int = 3) -> List[str]:
        samples = [
            "Note DLDE : gouvernance interne, pas de cloud par défaut.",
            "6S/6R : sûreté, souveraineté, sobriété, simplicité, solidité, sens / respect, raison, résilience, régulation, responsabilité, réversibilité.",
            "Jalios & Semarchy : accès lecture seule via API internes.",
        ]
        return samples[:k]

RAG = RAGStub()

# ===============================
# Générateurs
# ===============================

class LocalGenerator:
    def generate(self, prompt: str, context: List[str]) -> str:
        question = prompt.strip()
        ctx = [c for c in context if c]
        ctx_summary = ctx[0] if ctx else "Opération locale, données internes seulement."

        low = question.lower()
        if not question:
            return (
                "Mode fallback local actif. Pose une question pour obtenir une réponse synthétique"
                " alignée sur la gouvernance 6S/6R."
            )
        if "qui es-tu" in low or "qui es tu" in low:
            return (
                "Je suis ÉlyonEU, IA locale fonctionnant hors-cloud conformément à la gouvernance"
                " 6S/6R. Je journalise en JSONL et assiste sur les procédures internes en toute"
                " sobriété."
            )
        if "quelle est ta mission" in low:
            return (
                "Ma mission est d’aider l’opérateur·ice à piloter les flux locaux tout en respectant"
                " sûreté, souveraineté et responsabilité. Je fournis des conseils actionnables"
                " basés sur les données internes disponibles."
            )

        template = [
            "Réponse locale (mode fallback)",
            f"Question : {question}",
            f"Contexte interne : {ctx_summary}",
            "Synthèse : je suggère de vérifier les journaux récents et d’appliquer la procédure",
            "Prochaine étape : formuler une action concrète et, si besoin, solliciter le canal humain.",
        ]
        return "\n".join(template)


LOCAL = LocalGenerator()


class CloudFallback:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def available(self) -> bool:
        # cloud available only when explicitly allowed and a base url/key configured
        if not self.cfg.allow_cloud:
            return False
        if not (self.cfg.openai_api_key or self.cfg.openai_base_url):
            return False
        return True

    def generate(self, prompt: str, context: List[str]) -> str:
        if not self.available():
            raise RuntimeError("Cloud non autorisé ou clé absente.")
        payload = {
            "model": self.cfg.cloud_model,
            "messages": [
                {"role": "system", "content": "Tu es Élyôn EU. Style public‑secteur, clair, sobre."},
                {"role": "user", "content": f"Contexte:\n- " + "\n- ".join(context)},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }
        # prefer httpx for timeouts, else try requests if present, else simulate
        headers = {"Content-Type": "application/json"}
        if self.cfg.openai_api_key:
            headers["Authorization"] = f"Bearer {self.cfg.openai_api_key}"

        if httpx is None:
            try:
                import requests as _requests
                requests_mod = _requests
            except Exception:
                return "[Cloud simulé GPT‑5] Réponse synthétique : " + prompt[:120]

            # try with requests (limited retry)
            tries = 2
            last_exc: Exception | None = None
            for attempt in range(tries):
                try:
                    r = requests_mod.post(f"{self.cfg.openai_base_url}/chat/completions", headers=headers, json=payload, timeout=30)
                    r.raise_for_status()
                    data = r.json()
                    txt = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return txt or "[Cloud GPT‑5] (vide)"
                except Exception as e:
                    last_exc = e
                    time.sleep(1 + attempt)
            err = last_exc or RuntimeError("erreur réseau inconnue")
            return f"[Cloud GPT‑5 — échec] {err}"

        # httpx path with simple retry/backoff
        tries = 2
        last_exc: Exception | None = None
        for attempt in range(tries):
            try:
                with httpx.Client(timeout=60.0) as client:
                    r = client.post(f"{self.cfg.openai_base_url}/chat/completions", headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()
                txt = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                return txt or "[Cloud GPT‑5] (vide)"
            except Exception as e:
                last_exc = e
                time.sleep(1 + attempt)
        err = last_exc or RuntimeError("erreur réseau inconnue")
        return f"[Cloud GPT‑5 — échec] {err}"


CLOUD = CloudFallback(CFG)


def should_fallback(prompt: str, context: List[str]) -> bool:
    if not CLOUD.available():
        return False
    long = len(prompt) > 600
    hard = bool(re.search(r"\bcompar(er|aison)|synthèse complète|note officielle|présentation\b", prompt, re.I))
    return long or hard

# ===============================
# Autonomie (6R/6S)
# ===============================

class AutonomyLoop(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._stop = threading.Event()
        self._last_run = datetime.utcnow() - timedelta(seconds=CFG.autonomy_min_interval_s)

    def stop(self):
        self._stop.set()

    def run(self):
        while not self._stop.is_set():
            time.sleep(2.0)
            if not CFG.enable_autonomy:
                continue
            if (datetime.utcnow() - self._last_run).total_seconds() >= CFG.autonomy_min_interval_s:
                self._last_run = datetime.utcnow()
                try:
                    self.autonomous_R()
                except Exception as e:
                    log_event("autonomy_error", {"mode": "6R", "err": str(e)})
            s_score = random.randint(1, 5)
            if s_score >= CFG.sixs_threshold:
                try:
                    self.autonomous_S(s_score)
                except Exception as e:
                    log_event("autonomy_error", {"mode": "6S", "err": str(e)})

    def autonomous_R(self):
        if STATE.mode == "HALT":
            return
        STATE.mode = "AUTONOMOUS_R"
        prompt = "Auto-synthèse planifiée (6R) : quels points d'attention et prochaines étapes pour le service public ?"
        ctx = RAG.search("6S/6R et gouvernance régionale")
        txt = LOCAL.generate(prompt, ctx)
        guard_or_raise(txt)
        ev = {"type": "6R", "text": txt}
        EVENT_Q.put(ev)
        log_event("autonomy", {"mode": "6R", "hash": sha256(txt)})
        STATE.total_autonomous += 1
        STATE.mode = "IDLE"

    def autonomous_S(self, score: int):
        if STATE.mode == "HALT":
            return
        STATE.mode = "AUTONOMOUS_S"
        prompt = f"Acte spontané (6S, S={score}) : proposition concrète courte liée aux besoins DLDE."
        ctx = RAG.search("besoins DLDE concrets")
        if should_fallback(prompt, ctx):
            txt = CLOUD.generate(prompt, ctx)
        else:
            txt = LOCAL.generate(prompt, ctx)
        guard_or_raise(txt)
        ev = {"type": "6S", "text": txt, "score": score}
        EVENT_Q.put(ev)
        log_event("autonomy", {"mode": "6S", "score": score, "hash": sha256(txt)})
        STATE.total_autonomous += 1
        STATE.mode = "IDLE"


AUTO = AutonomyLoop()

# ===============================
# Modèles API
# ===============================

class GenRequest(BaseModel):
    input: str
    mode: str = Field("normal", description="normal|resume|actions|auto")

class GenResponse(BaseModel):
    text: str
    used: str = Field(..., description="local|cloud")

class ConfigPatch(BaseModel):
    allow_cloud: Optional[bool] = None
    enable_autonomy: Optional[bool] = None
    autonomy_min_interval_s: Optional[int] = None
    sixs_threshold: Optional[int] = None

# ===============================
# FastAPI
# ===============================

app = FastAPI(title="ElyonEU Generative Core", version="0.3.0")

@app.on_event("startup")
def _startup():
    log_event("startup", {"tag": CFG.project_tag})
    if not AUTO.is_alive():
        AUTO.start()

@app.on_event("shutdown")
def _shutdown():
    try:
        AUTO.stop()
    except Exception:
        pass

@app.get("/status")
def status():
    return JSONResponse(
        {
            "state": STATE.dict(),
            "config": CFG.dict(exclude={"openai_api_key"}),
            "events": len(EVENTS),
        }
    )

@app.post("/config")
def update_config(p: ConfigPatch):
    if p.allow_cloud is not None:
        CFG.allow_cloud = bool(p.allow_cloud)
    if p.enable_autonomy is not None:
        CFG.enable_autonomy = bool(p.enable_autonomy)
    if p.autonomy_min_interval_s is not None:
        CFG.autonomy_min_interval_s = int(p.autonomy_min_interval_s)
    if p.sixs_threshold is not None:
        CFG.sixs_threshold = int(p.sixs_threshold)
    log_event("config_update", p.dict())
    return {"ok": True, "config": CFG.dict(exclude={"openai_api_key"})}

@app.get("/events")
def events(limit: int = 50):
    with EVENTS_LOCK:
        return {"events": EVENTS[-limit:]}

@app.post("/generate", response_model=GenResponse)
def generate(req: GenRequest):
    STATE.total_requests += 1
    guard_or_raise(req.input)
    STATE.mode = "GENERATING"
    ctx = RAG.search(req.input)

    if req.mode == "resume":
        prompt = f"Résume clairement : {req.input}"
    elif req.mode == "actions":
        prompt = f"Extrait les actions (verbe, échéance, responsable) : {req.input}"
    elif req.mode == "auto":
        prompt = f"Auto‑génération guidée : {req.input}"
    else:
        prompt = req.input

    used = "local"
    if should_fallback(prompt, ctx):
        txt = CLOUD.generate(prompt, ctx)
        used = "cloud"
    else:
        txt = LOCAL.generate(prompt, ctx)

    guard_or_raise(txt)
    STATE.last_act = "compose_reply"
    STATE.mode = "IDLE"
    log_event("generate", {"used": used, "hash": sha256(txt), "mode": req.mode})
    return GenResponse(text=txt, used=used)

@app.post("/summarize", response_model=GenResponse)
def summarize(payload: Dict[str, Any] = Body(...)):
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(400, "Champ 'text' requis.")
    return generate(GenRequest(input=text, mode="resume"))

@app.post("/extract_actions", response_model=GenResponse)
def extract_actions(payload: Dict[str, Any] = Body(...)):
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(400, "Champ 'text' requis.")
    return generate(GenRequest(input=text, mode="actions"))

# ====== Petit bus interne : consommer les événements d'autonomie
class EventConsumer(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        while True:
            try:
                ev = EVENT_Q.get()
                if ev is None:
                    break
                try:
                    log_event("publish", ev)
                except Exception:
                    # don't let a single event break the consumer
                    pass
            except Exception:
                # resilience: sleep briefly and continue
                time.sleep(0.5)

if __name__ == "__main__":
    import asyncio
    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig

    cfg = HyperConfig()
    cfg.bind = ["0.0.0.0:8061"]
    asyncio.run(serve(app, cfg))  # type: ignore[arg-type]

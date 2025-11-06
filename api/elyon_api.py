# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import asyncio, threading, time, os, json, sys
import httpx
from pathlib import Path
from typing import Optional, TYPE_CHECKING

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from .core import memory, intent, vector_index, governance, profiles, divine  # type: ignore[import]
    from .routers import governance_profiles  # type: ignore[import]
except ImportError:
    from api.core import memory, intent, vector_index, governance, profiles, divine  # type: ignore[import]
    from api.routers import governance_profiles  # type: ignore[import]

def load_env_file(path: Optional[Path] = None) -> None:
    env_path = path or (ROOT / ".env")
    try:
        if not env_path.exists():
            return
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"')
            os.environ.setdefault(key, value)
    except Exception as exc:
        print(f"[api] Impossible de charger .env: {exc}", flush=True)

load_env_file()

APP_NAME = "ElyonEU (local)"
APP_VER  = "0.3.0"  # UI profiles + chat

# Répertoires
DATA_DIR    = ROOT / "data"
JOURNAL_DIR = ROOT / "journal"
STATIC_DIR  = Path(__file__).resolve().parent / "static"
UI_DIR      = ROOT / "ui"
WEB_UI_FILE = UI_DIR / "chat" / "index.html"
CFG_CHAT    = ROOT / "config" / "chat_backend.json"
MEMORY_DIR  = ROOT / "data" / "_memory"
VECTOR_INDEX_DIR = ROOT / "data" / "vector_index"

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

# ============================================================================
# INITIALISATION GOUVERNANCE, PROFILS ET DIVINE
# ============================================================================
try:
    # Instances des modules de gouvernance
    territorial_gov = governance.TerritorialGovernance()
    profile_mgr = profiles.UserProfileManager()
    ui_divine = divine.UIDivine(elyon_api_reference=app)

    # Initialisation du routeur de gouvernance/profils/divine
    governance_profiles.init_modules(territorial_gov, profile_mgr, ui_divine)
    app.include_router(governance_profiles.router, prefix="/v2")

    print("[api] ✓ Gouvernance, profils et divine activés (Région Grand Est 6S/6R)", flush=True)
except Exception as exc:
    print(f"[api] ⚠ Impossible d'initialiser gouvernance: {exc}", flush=True)# génération locale simplifiée (fallback)
if TYPE_CHECKING:
    from app.providers.generative_core_provider import GenerativeCoreProvider  # type: ignore[import]

_GEN_PROVIDER: Optional["GenerativeCoreProvider"] = None

def ensure_gen_provider() -> Optional["GenerativeCoreProvider"]:
    global _GEN_PROVIDER
    if _GEN_PROVIDER is not None:
        return _GEN_PROVIDER
    try:
        from app.providers.generative_core_provider import GenerativeCoreProvider  # type: ignore[import]

        _GEN_PROVIDER = GenerativeCoreProvider()
        return _GEN_PROVIDER
    except Exception as exc:
        print(f"[api] Générateur interne indisponible: {exc}", flush=True)
        return None

# génération locale simplifiée (fallback)
def local_generate(prompt: str, mode: str = "normal") -> tuple[str, str]:
    """Reponse intelligente locale avec support multi-mode et contexte educatif."""
    text = prompt.strip()
    if not text:
        return ("(mode local) Decris ta situation pour que je propose une prochaine etape alignee 6S/6R.", "gen_local")

    low = text.lower()
    
    # Detection d'intentions courantes
    if "mission" in low or "qui es-tu" in low or "c'est quoi" in low:
        return (
            "🎯 Ma mission ElyonEU\n\n"
            "Je guide les operateurs vers des actions concretes, ancrées dans les principes 6S/6R :\n"
            "✓ Surete : Protéger les donnees et les personnes\n"
            "✓ Souverainete : Rester dans la Region Grand Est\n"
            "✓ Sobriete : Efficacité maximale, ressources minimales\n"
            "✓ Simplicité : Actions claires et directes\n"
            "✓ Solidarite : Servir la communaute educative\n"
            "✓ Sens : Clarifier l'intention avant l'action",
            "gen_local",
        )
    
    if "aide" in low or "help" in low or "comment" in low or "fais quoi" in low:
        return (
            "🤝 Comment je peux t'aider\n\n"
            "1️⃣ Pose une question : Je recherche dans mes connaissances locales\n"
            "2️⃣ Demande une synthese : Mode `resume` pour une vue rapide\n"
            "3️⃣ Obtiens des actions : Mode `actions` pour des etapes concretes\n"
            "4️⃣ Consulte l'audit : Verifie les evenements et decisions passees\n\n"
            "Remarque : Mode local = zero donnees sortantes, compliance 100% Region Grand Est",
            "gen_local",
        )
    
    # Detection de mots-cles de domaine educatif
    if any(k in low for k in ["audit", "journal", "log", "compliance", "conformite"]):
        return (
            "📊 Audit & Gouvernance\n\n"
            "L'audit de conformite ElyonEU fonctionne en continu :\n"
            "✅ Tous les evenements sont loggés localement\n"
            "✅ Audit trail immutable (SHA-256)\n"
            "✅ Acces restreint au profil DIVINE uniquement\n"
            "✅ Zero donnees sortantes sauf opt-in approuvé\n\n"
            "Pour voir l'etat complet, contacte Joeffrey (profil DIVINE).",
            "gen_local",
        )
    
    if any(k in low for k in ["dlde", "delegue", "delegation", "region", "gouvernance"]):
        return (
            "🏛️ DLDE - Souverainete Region Grand Est\n\n"
            "ElyonEU est conçu pour respecter la souverainete DLDE :\n"
            "📍 Donnees strictement locales (Region Grand Est)\n"
            "👥 65 utilisateurs DLDE configures\n"
            "🔐 Roles granulaires (Divine, Admin, Chef, Enseignant, Agent, Public)\n"
            "📋 Adaptation UI par role\n\n"
            "Besoin d'un role specifique ? Adresse-toi a l'administrateur.",
            "gen_local",
        )
    
    if any(k in low for k in ["classe", "eleve", "ecole", "cours", "apprentissage", "pedagogie", "enseignant"]):
        return (
            "📚 Ressources Educatives\n\n"
            "ElyonEU offre un support contextualise pour l'education :\n"
            "📖 Corpus de reference accessibles localement\n"
            "🧠 Apprentissage adaptatif aux profils\n"
            "✨ Suggestions d'actions alignees a la pedagogie 6S/6R\n\n"
            f"Ton contexte : {text[:100]}...\n"
            "Pour plus de details, utilise le mode `actions`.",
            "gen_local",
        )
    
    # Modes specialises
    if mode == "resume":
        summary = (
            f"📋 Synthese\n\n"
            f"Objet : {text[:120]}\n\n"
            f"✅ Analyse rapide completee en mode local\n"
            f"💡 Prochaine etape : Clarifier l'intention operationnelle"
        )
        return (summary, "gen_local")
    
    elif mode == "actions":
        actions = (
            "🎯 Actions Recommandees\n\n"
            "1️⃣ Clarifier l'intention\n"
            "   → Quel est l'objectif precis ?\n\n"
            "2️⃣ Verifier les prerequis\n"
            "   → Donnees necessaires disponibles ?\n"
            "   → Autorisations presentes ?\n\n"
            "3️⃣ Executer l'action\n"
            "   → Etapes concretes alignees 6S/6R\n\n"
            "4️⃣ Documenter & Auditer\n"
            "   → Journal local auto-complete\n"
            "   → Trace immutable pour conformite"
        )
        return (actions, "gen_local")
    
    else:  # mode == "normal"
        response = (
            f"🔍 Analyse Locale\n\n"
            f"Ta demande : {text[:150]}\n\n"
            f"Approche ElyonEU :\n"
            f"✓ Traitement 100% local (Region Grand Est)\n"
            f"✓ Respect des profils de securite\n"
            f"✓ Audit trail complet\n\n"
            f"Recommandation : Precise davantage ton besoin pour une reponse plus ciblee ou utilise `mode=actions` pour des etapes concretes."
        )
        return (response, "gen_local")


# Mount local routers (if present)
try:
    from api.routers.generative import router as generative_router  # type: ignore[import]
    app.include_router(generative_router)
except Exception:
    # router optional — continue if not present
    pass


# ---------- utilitaires ----------
def ensure_dirs():
    for p in (DATA_DIR, JOURNAL_DIR, UI_DIR, STATIC_DIR, CFG_CHAT.parent, MEMORY_DIR, VECTOR_INDEX_DIR):
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

def _pick_available_model(api_key: str, base_url: str = "https://api.openai.com/v1") -> str:
    """Tente de déterminer le meilleur modèle GPT disponible selon le compte."""
    priority_models = ["gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"]
    if not api_key:
        return priority_models[0]  # défaut si pas de clé
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        endpoint = base_url.rstrip("/") + "/models"
        response = httpx.get(endpoint, headers=headers, timeout=5.0)
        if response.status_code == 200:
            available = {m["id"] for m in response.json().get("data", [])}
            print(f"[api] Modèles disponibles OpenAI: {sorted(available)[:5]}", flush=True)
            for model in priority_models:
                if model in available:
                    print(f"[api] Sélectionné : {model}", flush=True)
                    return model
        else:
            print(f"[api] /models retourna status {response.status_code}, utilisation fallback", flush=True)
    except Exception as exc:
        print(f"[api] Détection modèle échouée ({exc}), utilisation fallback", flush=True)
    print(f"[api] Fallback model: {priority_models[0]}", flush=True)
    return priority_models[0]  # fallback au premier choix

def load_chat_cfg():
    cfg = {
        "provider": "lmstudio",
        "base_url": "http://127.0.0.1:1234/v1",
        "model": "mistral-7b-instruct-v0.1",
        "api_key": "",
        "org": "",
        "policy": "local_first",
        "external_on_fallback": True,
    }
    try:
        if CFG_CHAT.exists():
            user = json.loads(CFG_CHAT.read_text(encoding="utf-8"))
            cfg.update({k:v for k,v in user.items() if v is not None})
    except Exception:
        pass
    # surcharge via variables d'environnement pour éviter les secrets en clair
    cfg["provider"] = os.getenv("ELYON_CHAT_PROVIDER", cfg["provider"]).strip() or cfg["provider"]
    cfg["base_url"] = os.getenv("ELYON_CHAT_BASE_URL", cfg["base_url"]).strip() or cfg["base_url"]
    cfg["model"] = os.getenv("ELYON_CHAT_MODEL", cfg["model"]).strip() or cfg["model"]
    api_key_env = os.getenv("ELYON_CHAT_API_KEY")
    if api_key_env:
        cfg["api_key"] = api_key_env.strip()
    else:
        backup = os.getenv("OPENAI_API_KEY", cfg["api_key"])
        cfg["api_key"] = backup.strip() if isinstance(backup, str) else ""
    cfg["org"] = os.getenv("OPENAI_ORG", cfg.get("org", "")).strip()
    policy_env = os.getenv("ELYON_CHAT_POLICY")
    cfg_policy = policy_env.strip() if policy_env else str(cfg.get("policy", "local_first"))
    cfg["policy"] = cfg_policy.strip() or "local_first"

    # Déterminer si le cloud est demandé
    allow_cloud = os.getenv("ALLOW_CLOUD", "").strip().lower()
    want_cloud = allow_cloud in {"1", "true", "yes", "on"}
    provider_raw = str(cfg.get("provider", "lmstudio"))
    provider_lower = provider_raw.lower().strip()
    has_api_key = bool(cfg.get("api_key"))
    provider_not_forced = not os.getenv("ELYON_CHAT_PROVIDER")

    # Si cloud est demandé + clé présente + provider non forcé → bascule sur OpenAI
    if want_cloud and has_api_key and provider_not_forced:
        if provider_lower in {"lmstudio", "local", "default"}:
            cfg["provider"] = "openai"
            base = (cfg.get("base_url") or "").strip()
            if not base or "127.0.0.1" in base or base.startswith("http://localhost"):
                cfg["base_url"] = "https://api.openai.com/v1"
            # Détecter le meilleur modèle disponible si pas spécifié ou si modèle invalide
            model_val = (cfg.get("model") or "").strip()
            # gpt-5 n'existe pas, forcer détection
            if not model_val or model_val == "gpt-5" or model_val.startswith("mistral"):
                # Chercher le meilleur modèle disponible sur le compte
                detected = _pick_available_model(cfg.get("api_key", ""), cfg.get("base_url", "https://api.openai.com/v1"))
                cfg["model"] = detected
                print(f"[api] Modèle OpenAI sélectionné: {detected}", flush=True)

    # Configurer external_on_fallback
    fallback_env = os.getenv("ELYON_CHAT_EXTERNAL_ON_FALLBACK")
    if fallback_env is not None:
        val = fallback_env.strip().lower()
        cfg["external_on_fallback"] = val not in {"0", "false", "no", "non", "off"}
    else:
        current = cfg.get("external_on_fallback", True)
        if isinstance(current, str):
            cfg["external_on_fallback"] = current.strip().lower() not in {"0", "false", "no", "non", "off"}
        else:
            cfg["external_on_fallback"] = bool(current)
        provider_lower = str(cfg.get("provider", "lmstudio")).lower().strip()
        base = str(cfg.get("base_url", "")).strip()
        model_val = str(cfg.get("model", "")).strip()
        if provider_lower == "lmstudio":
            endpoint = base.rstrip("/") if base else "http://127.0.0.1:1234/v1"
            if not endpoint.endswith("/chat/completions"):
                endpoint = endpoint.rstrip("/") + "/chat/completions"
            os.environ["LMSTUDIO_URL"] = endpoint
            if model_val:
                os.environ["LMSTUDIO_MODEL"] = model_val
        elif provider_lower == "openai":
            if base:
                os.environ["OPENAI_BASE_URL"] = base.rstrip("/")
            if cfg.get("api_key"):
                os.environ["OPENAI_API_KEY"] = cfg["api_key"]
            if model_val:
                os.environ["GPT5_MODEL"] = model_val
    return cfg
async def try_external_chat(cfg: dict, msgs: list[dict], data: dict) -> Optional[tuple[str, str]]:
    provider_cfg = (cfg.get("provider") or "lmstudio").lower().strip()
    base_url = (cfg.get("base_url") or "").strip()
    api_key = cfg.get("api_key") or ""

    # Valider les messages : chaque message doit avoir "role" et "content"
    validated_msgs = []
    for msg in msgs:
        if isinstance(msg, dict) and "role" in msg and "content" in msg:
            validated_msgs.append({
                "role": str(msg["role"]).lower(),
                "content": str(msg["content"])
            })
    if not validated_msgs:
        raise ValueError("Aucun message valide fourni")

    model_str = cfg.get("model", "gpt-4o-mini").strip()
    if not model_str or model_str == "gpt-5":
        model_str = "gpt-4o-mini"
        print(f"[api] Modèle vide ou gpt-5 (invalide), utilisant gpt-4o-mini", flush=True)

    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model_str,
        "messages": validated_msgs,
        "temperature": float(data.get("temperature", 0.3) or 0.3),
        "max_tokens": int(data.get("max_tokens", 512) or 512),
    }

    if provider_cfg == "openai":
        endpoint = (base_url or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("OPENAI_API_KEY manquant pour le provider openai")
        headers["Authorization"] = f"Bearer {api_key}"
        if cfg.get("org"):
            headers["OpenAI-Organization"] = cfg["org"]
        provider_label = "openai"
    else:
        if not base_url:
            raise ValueError("base_url requis pour le provider externe")
        endpoint = base_url.rstrip("/")
        if not endpoint.endswith("/chat/completions"):
            endpoint = endpoint + "/chat/completions"
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        provider_label = cfg.get("provider", provider_cfg)

    print(f"[api] Appel externe {provider_label}: endpoint={endpoint}, model={payload.get('model')}, msg_count={len(payload.get('messages', []))}, payload_size={len(str(payload))}", flush=True)
    async with httpx.AsyncClient(timeout=httpx.Timeout(8.0, connect=3.0, read=6.0)) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
    response.raise_for_status()

    body = response.json()
    choice = (body.get("choices") or [{}])[0]
    message = choice.get("message") or {}
    reply = (message.get("content") or "").strip()
    if not reply:
        raise ValueError("réponse vide du provider externe")
    return reply, provider_label


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
    Output: { "reply": "..." , "provider":"openai|lmstudio|gen_*" , "trace": {...} }
    """
    try:
        data = await req.json()
        msgs = data.get("messages") or []
        cfg = load_chat_cfg()
        print("[api] /chat reçu", len(msgs), "messages", flush=True)

        print("[api] [DEBUG 1] Chargement mémoire...", flush=True)
        memory_summary = memory.get_summary_text()
        summary_applied = bool(memory_summary)
        print(f"[api] [DEBUG 1] OK", flush=True)

        enriched_msgs = list(msgs)
        if summary_applied:
            enriched_msgs = (
                [
                    {
                        "role": "system",
                        "content": "Contexte récent (résumé) :\n" + memory_summary,
                    }
                ]
                + enriched_msgs
            )

        provider_tag = (cfg.get("provider") or "lmstudio").lower().strip()
        policy = str(cfg.get("policy", "local_first")).lower().strip() or "local_first"
        external_on_fallback = bool(cfg.get("external_on_fallback", True))

        mode = data.get("mode", "normal")
        last_user = next((m["content"] for m in reversed(msgs) if m.get("role") == "user"), "")

        print("[api] [DEBUG 2] Analyse intentions...", flush=True)
        intent_meta_raw = intent.analyze(last_user)
        intent_meta = intent_meta_raw if isinstance(intent_meta_raw, dict) else {}
        intent_value = intent_meta.get("intent") if isinstance(intent_meta.get("intent"), str) else intent_meta.get("intent")
        intent_applied = bool(intent_value and intent_value != "empty")
        keywords_raw = intent_meta.get("keywords") if intent_applied else []
        keywords_list = [str(k) for k in keywords_raw[:4]] if isinstance(keywords_raw, list) else []
        entities_raw = intent_meta.get("entities") if intent_applied else {}
        entities_map = entities_raw if isinstance(entities_raw, dict) else {}
        print(f"[api] [DEBUG 2] OK - intent={intent_value}", flush=True)

        print("[api] [DEBUG 3] Recherche RAG...", flush=True)
        rag_query_parts: list[str] = []
        if last_user:
            rag_query_parts.append(last_user)
        if keywords_list:
            rag_query_parts.extend(keywords_list)
        rag_query = " ".join(part for part in rag_query_parts if part)
        rag_hits: list[dict] = []
        if rag_query:
            try:
                rag_hits = vector_index.search(rag_query, top_k=int(data.get("rag_top_k", 3) or 3))
            except Exception as exc:
                print(f"[api] [DEBUG 3] RAG erreur: {exc}", flush=True)
                log_event("CHAT_TRACE", {"stage": "rag_error", "query": rag_query, "error": str(exc)})
                rag_hits = []
        print(f"[api] [DEBUG 3] OK - rag_hits={len(rag_hits)}", flush=True)

        rag_applied = bool(rag_hits)
        rag_lines: list[str] = []
        if rag_applied:
            for idx, hit in enumerate(rag_hits, start=1):
                doc_id = str(hit.get("doc_id", f"doc_{idx}"))
                score_raw = hit.get("score", 0.0)
                try:
                    score = float(score_raw)
                except Exception:
                    score = 0.0
                text_raw = str(hit.get("text", "")).strip().replace("\r", " ")
                snippet = " ".join(text_raw.split())
                if len(snippet) > 220:
                    snippet = snippet[:217] + "..."
                rag_lines.append(f"{idx}. [{doc_id}] score={score:.3f} -> {snippet}")
            log_event(
                "CHAT_TRACE",
                {
                    "stage": "rag",
                    "query": rag_query,
                    "count": len(rag_hits),
                    "results": [str(hit.get("doc_id", "")) for hit in rag_hits],
                },
            )
        if intent_applied:
            intent_str_parts = [
                f"Intention: {intent_meta.get('intent')}",
                f"Urgence: {'oui' if intent_meta.get('urgent') else 'non'}",
            ]
            if keywords_list:
                intent_str_parts.append("Mots-clés: " + ", ".join(keywords_list))
            if entities_map:
                ent_chunks = []
                for key, vals in entities_map.items():
                    if isinstance(vals, list) and vals:
                        safe_vals = [str(v) for v in vals[:3]]
                        ent_chunks.append(f"{key}={','.join(safe_vals)}")
                if ent_chunks:
                    intent_str_parts.append("Entités: " + "; ".join(ent_chunks))
            enriched_msgs = (
                [
                    {
                        "role": "system",
                        "content": "Analyse de l'intention utilisateur : " + " | ".join(intent_str_parts),
                    }
                ]
                + enriched_msgs
            )
        if rag_applied and rag_lines:
            enriched_msgs = (
                [
                    {
                        "role": "system",
                        "content": "Connaissances pertinentes (TF-IDF) :\n" + "\n".join(rag_lines),
                    }
                ]
                + enriched_msgs
            )
        # message d'amorçage local pour garantir une réponse
        enriched_msgs = (
            [
                {
                    "role": "system",
                    "content": (
                        "Tu es ÉlyonEU, IA locale gouvernance 6S/6R. Réponds sans nuancer inutilement,"
                        " propose une synthèse opérationnelle et termine par une prochaine étape concrète."
                    ),
                }
            ]
            + enriched_msgs
        )

        contextual_prompt = last_user or "Bonjour"
        if summary_applied:
            contextual_prompt = (
                "Contexte récent :\n" + memory_summary + "\n\nDemande utilisateur :\n" + (last_user or "Bonjour")
            )
        if intent_applied:
            contextual_prompt += (
                "\n\nAnalyse intention :"
                f"\n- intention={intent_meta.get('intent')}"
                f"\n- urgent={'oui' if intent_meta.get('urgent') else 'non'}"
            )
            if keywords_list:
                contextual_prompt += "\n- mots_clés=" + ",".join(keywords_list)
        if rag_applied and rag_lines:
            contextual_prompt += "\n\nConnaissances pertinentes :\n" + "\n".join(rag_lines)

        def run_local_generation() -> tuple[str, str]:
            gen = ensure_gen_provider()
            if gen is not None:
                try:
                    result = gen.generate(contextual_prompt, mode=mode)
                    text = (result.text or "").strip()
                    used_raw = str(getattr(result, "used", "local") or "local")
                    used_lower = used_raw.lower()
                    text_lower = text.lower()
                    placeholder = text_lower.startswith("[cloud gpt") or "(vide" in text_lower
                    if used_lower == "cloud" and (not text or placeholder):
                        raise RuntimeError("fallback cloud vide ou non autorisé")
                    if not text:
                        raise RuntimeError("réponse vide du générateur interne")
                    return text, f"gen_{used_lower or 'local'}"
                except Exception as exc:
                    print(f"[api] Générateur interne en erreur: {exc}", flush=True)
            return local_generate(contextual_prompt, mode=mode)

        print("[api] [DEBUG 4] Génération locale...", flush=True)
        try:
            reply, provider = run_local_generation()
        except Exception as exc:
            print(f"[api] Fallback vers local_generate: {exc}", flush=True)
            reply, provider = local_generate(contextual_prompt, mode=mode)
        print(f"[api] [DEBUG 4] OK - provider={provider}, len={len(reply)}", flush=True)

        local_provider = provider
        local_len = len(reply)
        log_event(
            "CHAT_TRACE",
            {
                "stage": "local",
                "provider": local_provider,
                "len": local_len,
                "policy": policy,
                "memory_applied": summary_applied,
                "intent": intent_meta,
            },
        )

        external_requested = any(bool(data.get(k)) for k in ("use_external", "external", "force_external", "prefer_external"))
        allow_external = provider_tag not in {"disabled", "none", "local"} and policy not in {"disabled", "never"}
        fallback_triggered = local_provider == "gen_local"

        should_try_external = False
        if allow_external:
            if policy in {"external_first", "always"}:
                should_try_external = True
            elif policy in {"fallback"}:
                should_try_external = fallback_triggered or external_requested
            else:  # local_first / on_request
                should_try_external = external_requested or (fallback_triggered and external_on_fallback)

        external_attempted = False
        external_success = False
        external_provider_name: Optional[str] = None
        external_error: Optional[str] = None

        if should_try_external:
            external_attempted = True
            print("[api] [DEBUG 5] Appel externe...", flush=True)
            log_event(
                "CHAT_TRACE",
                {
                    "stage": "external_attempt",
                    "provider": provider_tag,
                    "policy": policy,
                    "requested": external_requested,
                    "fallback_triggered": fallback_triggered,
                },
            )
            try:
                external_reply = await try_external_chat(cfg, enriched_msgs, data)
                if external_reply:
                    reply, external_provider_name = external_reply
                    provider = external_provider_name
                    external_success = True
                    print(f"[api] [DEBUG 5] OK - {provider}", flush=True)
                    log_event(
                        "CHAT_TRACE",
                        {
                            "stage": "external_success",
                            "provider": provider,
                            "len": len(reply),
                            "memory_applied": summary_applied,
                            "intent": intent_meta,
                        },
                    )
            except Exception as exc:
                external_error = str(exc)
                print(f"[api] [DEBUG 5] ERREUR: {exc}", flush=True)
                print(f"[api] Provider externe indisponible ({provider_tag}): {exc}", flush=True)
                log_event(
                    "CHAT_TRACE",
                    {
                        "stage": "external_error",
                        "provider": provider_tag,
                        "error": (external_error or "")[0:240],
                    },
                )

        log_event(
            "CHAT",
            {
                "provider": provider,
                "len": len(reply),
                "policy": policy,
                "external_requested": external_requested,
                "external_attempted": external_attempted,
                "external_success": external_success,
                "local_provider": local_provider,
                "memory_applied": summary_applied,
                "intent": intent_meta,
            },
        )

        trace = {
            "policy": policy,
            "local_provider": local_provider,
            "local_len": local_len,
            "external_requested": external_requested,
            "external_on_fallback": external_on_fallback,
            "external_attempted": external_attempted,
            "external_success": external_success,
            "external_provider": external_provider_name or (provider_tag if external_attempted else None),
            "memory_used": summary_applied,
            "intent": intent_meta,
        }
        if external_error:
            trace["external_error"] = external_error[0:120]

        print("[api] [DEBUG 6] Sauvegarde mémoire...", flush=True)
        memory.remember_interaction(last_user or "", reply, meta=intent_meta if intent_applied else None)
        print("[api] [DEBUG 6] OK", flush=True)

        print("[api] [DEBUG] ✓ /chat complète", flush=True)
        return JSONResponse({"reply": reply, "provider": provider, "trace": trace})

    except Exception as e:
        print(f"[api] [ERROR] Exception dans /chat: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return JSONResponse({"error": str(e), "reply": "Erreur serveur interne"}, status_code=500)
    if summary_applied:
        enriched_msgs = (
            [
                {
                    "role": "system",
                    "content": "Contexte récent (résumé) :\n" + memory_summary,
                }
            ]
            + enriched_msgs
        )

    provider_tag = (cfg.get("provider") or "lmstudio").lower().strip()
    policy = str(cfg.get("policy", "local_first")).lower().strip() or "local_first"
    external_on_fallback = bool(cfg.get("external_on_fallback", True))

    mode = data.get("mode", "normal")
    last_user = next((m["content"] for m in reversed(msgs) if m.get("role") == "user"), "")

    intent_meta_raw = intent.analyze(last_user)
    intent_meta = intent_meta_raw if isinstance(intent_meta_raw, dict) else {}
    intent_value = intent_meta.get("intent") if isinstance(intent_meta.get("intent"), str) else intent_meta.get("intent")
    intent_applied = bool(intent_value and intent_value != "empty")
    keywords_raw = intent_meta.get("keywords") if intent_applied else []
    keywords_list = [str(k) for k in keywords_raw[:4]] if isinstance(keywords_raw, list) else []
    entities_raw = intent_meta.get("entities") if intent_applied else {}
    entities_map = entities_raw if isinstance(entities_raw, dict) else {}
    rag_query_parts: list[str] = []
    if last_user:
        rag_query_parts.append(last_user)
    if keywords_list:
        rag_query_parts.extend(keywords_list)
    rag_query = " ".join(part for part in rag_query_parts if part)
    rag_hits: list[dict] = []
    if rag_query:
        try:
            rag_hits = vector_index.search(rag_query, top_k=int(data.get("rag_top_k", 3) or 3))
        except Exception as exc:
            log_event("CHAT_TRACE", {"stage": "rag_error", "query": rag_query, "error": str(exc)})
            rag_hits = []
    rag_applied = bool(rag_hits)
    rag_lines: list[str] = []
    if rag_applied:
        for idx, hit in enumerate(rag_hits, start=1):
            doc_id = str(hit.get("doc_id", f"doc_{idx}"))
            score_raw = hit.get("score", 0.0)
            try:
                score = float(score_raw)
            except Exception:
                score = 0.0
            text_raw = str(hit.get("text", "")).strip().replace("\r", " ")
            snippet = " ".join(text_raw.split())
            if len(snippet) > 220:
                snippet = snippet[:217] + "..."
            rag_lines.append(f"{idx}. [{doc_id}] score={score:.3f} -> {snippet}")
        log_event(
            "CHAT_TRACE",
            {
                "stage": "rag",
                "query": rag_query,
                "count": len(rag_hits),
                "results": [str(hit.get("doc_id", "")) for hit in rag_hits],
            },
        )
    if intent_applied:
        intent_str_parts = [
            f"Intention: {intent_meta.get('intent')}",
            f"Urgence: {'oui' if intent_meta.get('urgent') else 'non'}",
        ]
        if keywords_list:
            intent_str_parts.append("Mots-clés: " + ", ".join(keywords_list))
        if entities_map:
            ent_chunks = []
            for key, vals in entities_map.items():
                if isinstance(vals, list) and vals:
                    safe_vals = [str(v) for v in vals[:3]]
                    ent_chunks.append(f"{key}={','.join(safe_vals)}")
            if ent_chunks:
                intent_str_parts.append("Entités: " + "; ".join(ent_chunks))
        enriched_msgs = (
            [
                {
                    "role": "system",
                    "content": "Analyse de l’intention utilisateur : " + " | ".join(intent_str_parts),
                }
            ]
            + enriched_msgs
        )
    if rag_applied and rag_lines:
        enriched_msgs = (
            [
                {
                    "role": "system",
                    "content": "Connaissances pertinentes (TF-IDF) :\n" + "\n".join(rag_lines),
                }
            ]
            + enriched_msgs
        )
    # message d'amorçage local pour garantir une réponse
    enriched_msgs = (
        [
            {
                "role": "system",
                "content": (
                    "Tu es ÉlyonEU, IA locale gouvernance 6S/6R. Réponds sans nuancer inutilement,"
                    " propose une synthèse opérationnelle et termine par une prochaine étape concrète."
                ),
            }
        ]
        + enriched_msgs
    )

    contextual_prompt = last_user or "Bonjour"
    if summary_applied:
        contextual_prompt = (
            "Contexte récent :\n" + memory_summary + "\n\nDemande utilisateur :\n" + (last_user or "Bonjour")
        )
    if intent_applied:
        contextual_prompt += (
            "\n\nAnalyse intention :"
            f"\n- intention={intent_meta.get('intent')}"
            f"\n- urgent={'oui' if intent_meta.get('urgent') else 'non'}"
        )
        if keywords_list:
            contextual_prompt += "\n- mots_clés=" + ",".join(keywords_list)
    if rag_applied and rag_lines:
        contextual_prompt += "\n\nConnaissances pertinentes :\n" + "\n".join(rag_lines)

    def run_local_generation() -> tuple[str, str]:
        gen = ensure_gen_provider()
        if gen is not None:
            try:
                result = gen.generate(contextual_prompt, mode=mode)
                text = (result.text or "").strip()
                used_raw = str(getattr(result, "used", "local") or "local")
                used_lower = used_raw.lower()
                text_lower = text.lower()
                placeholder = text_lower.startswith("[cloud gpt") or "(vide" in text_lower
                if used_lower == "cloud" and (not text or placeholder):
                    raise RuntimeError("fallback cloud vide ou non autorisé")
                if not text:
                    raise RuntimeError("réponse vide du générateur interne")
                return text, f"gen_{used_lower or 'local'}"
            except Exception as exc:
                print(f"[api] Générateur interne en erreur: {exc}", flush=True)
        return local_generate(contextual_prompt, mode=mode)

    try:
        reply, provider = run_local_generation()
    except Exception as exc:
        print(f"[api] Fallback vers local_generate suite à l'erreur: {exc}", flush=True)
        reply, provider = local_generate(contextual_prompt, mode=mode)
    local_provider = provider
    local_len = len(reply)
    log_event(
        "CHAT_TRACE",
        {
            "stage": "local",
            "provider": local_provider,
            "len": local_len,
            "policy": policy,
            "memory_applied": summary_applied,
            "intent": intent_meta,
        },
    )

    external_requested = any(bool(data.get(k)) for k in ("use_external", "external", "force_external", "prefer_external"))
    allow_external = provider_tag not in {"disabled", "none", "local"} and policy not in {"disabled", "never"}
    fallback_triggered = local_provider == "gen_local"

    should_try_external = False
    if allow_external:
        if policy in {"external_first", "always"}:
            should_try_external = True
        elif policy in {"fallback"}:
            should_try_external = fallback_triggered or external_requested
        else:  # local_first / on_request
            should_try_external = external_requested or (fallback_triggered and external_on_fallback)

    external_attempted = False
    external_success = False
    external_provider_name: Optional[str] = None
    external_error: Optional[str] = None

    if should_try_external:
        external_attempted = True
        log_event(
            "CHAT_TRACE",
            {
                "stage": "external_attempt",
                "provider": provider_tag,
                "policy": policy,
                "requested": external_requested,
                "fallback_triggered": fallback_triggered,
            },
        )
        try:
            external_reply = await try_external_chat(cfg, enriched_msgs, data)
            if external_reply:
                reply, external_provider_name = external_reply
                provider = external_provider_name
                external_success = True
                log_event(
                    "CHAT_TRACE",
                    {
                        "stage": "external_success",
                        "provider": provider,
                        "len": len(reply),
                        "memory_applied": summary_applied,
                        "intent": intent_meta,
                    },
                )
        except Exception as exc:
            external_error = str(exc)
            print(f"[api] Provider externe indisponible ({provider_tag}): {exc}", flush=True)
            log_event(
                "CHAT_TRACE",
                {
                    "stage": "external_error",
                    "provider": provider_tag,
                    "error": (external_error or "")[0:240],
                },
            )

    log_event(
        "CHAT",
        {
            "provider": provider,
            "len": len(reply),
            "policy": policy,
            "external_requested": external_requested,
            "external_attempted": external_attempted,
            "external_success": external_success,
            "local_provider": local_provider,
            "memory_applied": summary_applied,
            "intent": intent_meta,
        },
    )

    trace = {
        "policy": policy,
        "local_provider": local_provider,
        "local_len": local_len,
        "external_requested": external_requested,
        "external_on_fallback": external_on_fallback,
        "external_attempted": external_attempted,
        "external_success": external_success,
        "external_provider": external_provider_name or (provider_tag if external_attempted else None),
        "memory_used": summary_applied,
        "intent": intent_meta,
    }
    if external_error:
        trace["external_error"] = external_error[0:120]

    memory.remember_interaction(last_user or "", reply, meta=intent_meta if intent_applied else None)

    return JSONResponse({"reply": reply, "provider": provider, "trace": trace})


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
    import uvicorn

    # Démarre avec uvicorn (plus fiable que hypercorn pour développement)
    try:
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n[api] Arrêt demandé (Ctrl+C)", flush=True)
    except Exception as exc:
        print(f"[api] Erreur serveur: {exc}", flush=True)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

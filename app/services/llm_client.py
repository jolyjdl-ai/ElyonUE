from __future__ import annotations
import os
try:
    import httpx
except Exception:
    httpx = None
    try:
        import requests as _requests
        requests = _requests
    except Exception:
        requests = None
from typing import List

ALLOW_CLOUD = os.getenv("ALLOW_CLOUD", "false").lower() in ("1","true","yes")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY","")
OPENAI_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
GPT5_MODEL = os.getenv("GPT5_MODEL", "gpt-5")

LM_URL   = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1/chat/completions")
LM_MODEL = os.getenv("LMSTUDIO_MODEL", "mistral-7b-instruct-v0.1")

SYSTEM_PROMPT = "Tu es Élyôn EU. Style public-secteur, clair, sobre."

def _chat_payload(model: str, prompt: str, context: List[str]):
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Contexte:\n- " + "\n- ".join(context)},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
    }

def call_local(prompt: str, context: List[str]) -> str:
    payload = _chat_payload(LM_MODEL, prompt, context)
    if httpx is not None:
        with httpx.Client(timeout=60.0) as c:
            r = c.post(LM_URL, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    if requests is not None:
        r = requests.post(LM_URL, json=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    # fallback simulé
    return "[local-simulé] " + prompt[:120]

def call_gpt5(prompt: str, context: List[str]) -> str:
    if not (ALLOW_CLOUD and OPENAI_API_KEY):
        raise RuntimeError("Cloud non autorisé ou clé absente.")
    payload = _chat_payload(GPT5_MODEL, prompt, context)
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    if httpx is not None:
        with httpx.Client(timeout=60.0) as c:
            r = c.post(f"{OPENAI_BASE}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    if requests is not None:
        r = requests.post(f"{OPENAI_BASE}/chat/completions", headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    raise RuntimeError("Aucun client HTTP disponible pour appeler le cloud.")

def generate(prompt: str, context: List[str], prefer_cloud: bool=False) -> tuple[str,str]:
    """
    Retourne (texte, source) où source = 'local' ou 'cloud'
    """
    if prefer_cloud:
        try:
            return call_gpt5(prompt, context), "cloud"
        except Exception:
            pass
    # défaut : local d’abord
    return call_local(prompt, context), "local"

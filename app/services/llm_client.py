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

DEFAULT_ALLOW_CLOUD = os.getenv("ALLOW_CLOUD", "false").lower() in ("1", "true", "yes")
DEFAULT_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DEFAULT_OPENAI_BASE = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
DEFAULT_GPT5_MODEL = os.getenv("GPT5_MODEL", "gpt-5")

DEFAULT_LM_URL = os.getenv("LMSTUDIO_URL", "http://localhost:1234/v1/chat/completions")
DEFAULT_LM_MODEL = os.getenv("LMSTUDIO_MODEL", "mistral-7b-instruct-v0.1")


def _allow_cloud() -> bool:
    env = os.getenv("ALLOW_CLOUD")
    if env is not None:
        return env.lower() in ("1", "true", "yes")
    return DEFAULT_ALLOW_CLOUD


def _openai_api_key() -> str:
    return os.getenv("OPENAI_API_KEY", DEFAULT_OPENAI_API_KEY)


def _openai_base() -> str:
    return os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE)


def _gpt5_model() -> str:
    return os.getenv("GPT5_MODEL", DEFAULT_GPT5_MODEL)


def _lm_url() -> str:
    return os.getenv("LMSTUDIO_URL", DEFAULT_LM_URL)


def _lm_model() -> str:
    return os.getenv("LMSTUDIO_MODEL", DEFAULT_LM_MODEL)

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
    lm_model = _lm_model()
    payload = _chat_payload(lm_model, prompt, context)
    lm_url = _lm_url()
    timeout_err = RuntimeError("Serveur LM Studio indisponible ou lent (timeout)")
    if httpx is not None:
        try:
            with httpx.Client(timeout=httpx.Timeout(8.0, connect=3.0, read=6.0)) as c:
                r = c.post(lm_url, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise timeout_err from exc
    if requests is not None:
        try:
            r = requests.post(lm_url, json=payload, timeout=8)
            r.raise_for_status()
            return r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except requests.Timeout as exc:  # type: ignore[attr-defined]
            raise timeout_err from exc
    # fallback simulé
    return "[local-simulé] " + prompt[:120]

def call_gpt5(prompt: str, context: List[str]) -> str:
    if not (_allow_cloud() and _openai_api_key()):
        raise RuntimeError("Cloud non autorisé ou clé absente.")
    payload = _chat_payload(_gpt5_model(), prompt, context)
    headers = {"Authorization": f"Bearer {_openai_api_key()}"}
    if httpx is not None:
        with httpx.Client(timeout=60.0) as c:
            r = c.post(f"{_openai_base().rstrip('/')}/chat/completions", headers=headers, json=payload)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    if requests is not None:
        r = requests.post(f"{_openai_base().rstrip('/')}/chat/completions", headers=headers, json=payload, timeout=30)
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

"""LLM abstraction with local-first fallback."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import httpx


@dataclass
class ChatMessage:
    role: str
    content: str


class LLMService:
    def __init__(self) -> None:
        self._lm_url = os.getenv("LMSTUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")
        self._lm_model = os.getenv("LMSTUDIO_MODEL", "mistral-7b-instruct-v0.1")
        self._timeout = float(os.getenv("LM_TIMEOUT", "30"))

    def _call_local(self, messages: Iterable[ChatMessage]) -> Tuple[str, str]:
        payload = {
            "model": self._lm_model,
            "messages": [msg.__dict__ for msg in messages],
            "temperature": 0.3,
        }
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(self._lm_url, json=payload)
                response.raise_for_status()
                data = response.json()
                choice = data.get("choices", [{}])[0]
                reply = choice.get("message", {}).get("content", "")
                if reply:
                    return reply, "lmstudio"
        except Exception:
            pass
        return self._fallback(messages)

    def _fallback(self, messages: Iterable[ChatMessage]) -> Tuple[str, str]:
        last_user = next((m.content for m in reversed(list(messages)) if m.role == "user"), "" )
        reply = (
            "[local] Réponse synthétique : "
            + (last_user[:280] if last_user else "Demande non fournie.")
            + "\n\nCadre 6S/6R : sécurité, sobriété, sens / respect, responsabilité, réversibilité."
        )
        return reply, "fallback"

    def chat(self, messages: List[ChatMessage]) -> Tuple[str, str]:
        return self._call_local(messages)

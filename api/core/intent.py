from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

_QUESTION_WORDS = {
    "qui",
    "quoi",
    "comment",
    "pourquoi",
    "où",
    "ou",
    "quand",
    "combien",
    "lequel",
    "laquelle",
    "est-ce",
    "est ce",
}

_CREATIVE_TRIGGERS = {
    "écris",
    "écrire",
    "rédige",
    "rédiger",
    "poème",
    "haïku",
    "hymne",
    "histoire",
    "discours",
    "texte",
    "scénario",
}

_SUMMARY_TRIGGERS = {
    "résume",
    "résumer",
    "synthèse",
    "bilan",
    "résumé",
}

_ACTION_TRIGGERS = {
    "plan",
    "liste",
    "tâche",
    "tâches",
    "prochaine étape",
    "actions",
    "dois-je",
    "fais",
    "faire",
    "propose",
    "priorise",
}

_URGENCY_WORDS = {
    "urgent",
    "urgence",
    "immédiat",
    "important",
    "rapidement",
    "tout de suite",
    "vite",
}

_GREETINGS = {
    "bonjour",
    "salut",
    "bonsoir",
    "coucou",
    "hello",
    "bien le bonjour",
}


def _intent_from_text(text: str) -> str:
    low = text.lower()
    if not low.strip():
        return "empty"
    if any(word in low for word in _GREETINGS):
        return "greeting"
    if any(word in low for word in _SUMMARY_TRIGGERS):
        return "summary_request"
    if any(word in low for word in _CREATIVE_TRIGGERS):
        return "creative_request"
    if any(word in low for word in _ACTION_TRIGGERS):
        return "action_request"
    if "?" in low or any(low.startswith(word) or f" {word} " in low for word in _QUESTION_WORDS):
        return "question"
    if len(low.split()) <= 3:
        return "short_prompt"
    return "statement"


def _detect_urgency(text: str) -> bool:
    low = text.lower()
    return any(word in low for word in _URGENCY_WORDS)


def _extract_keywords(text: str) -> List[str]:
    words = re.findall(r"[a-zA-ZÀ-ÖØ-öø-ÿ0-9]{3,}", text.lower())
    counter = Counter(words)
    common = [w for w, count in counter.most_common(6) if count >= 1]
    return common


def _extract_entities(text: str) -> Dict[str, List[str]]:
    entities: Dict[str, List[str]] = {
        "dates": [],
        "numbers": [],
        "refs": [],
    }
    for date in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text):
        entities["dates"].append(date)
    for date in re.findall(r"\b\d{2}/\d{2}/\d{4}\b", text):
        entities["dates"].append(date)
    for num in re.findall(r"\b\d+[\.,]?\d*\b", text):
        entities["numbers"].append(num)
    for ref in re.findall(r"\b[A-Z]{2,}-?\d{2,}\b", text):
        entities["refs"].append(ref)
    return {k: v for k, v in entities.items() if v}


def analyze(text: str) -> Dict[str, object]:
    text = (text or "").strip()
    if not text:
        return {"intent": "empty", "confidence": 0.0, "keywords": [], "entities": {}, "urgent": False}
    intent = _intent_from_text(text)
    urgency = _detect_urgency(text)
    keywords = _extract_keywords(text)
    entities = _extract_entities(text)
    confidence = 0.6 if intent not in {"statement", "short_prompt"} else 0.4
    if urgency:
        confidence = min(1.0, confidence + 0.2)
    return {
        "intent": intent,
        "confidence": round(confidence, 2),
        "keywords": keywords,
        "entities": entities,
        "urgent": urgency,
    }

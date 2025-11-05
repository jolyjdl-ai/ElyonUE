from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
MEMORY_DIR = ROOT / "data" / "_memory"
MEMORY_FILE = MEMORY_DIR / "conversation_state.json"
_MAX_HISTORY = 5
_LOCK = threading.Lock()


def _ensure_dir() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


def _load_raw() -> Dict[str, List[Dict[str, object]]]:
    _ensure_dir()
    if not MEMORY_FILE.exists():
        return {"history": []}
    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {"history": []}
        hist = data.get("history", [])
        if not isinstance(hist, list):
            return {"history": []}
        return {"history": hist}
    except Exception:
        return {"history": []}


def _save_raw(payload: Dict[str, List[Dict[str, object]]]) -> None:
    _ensure_dir()
    MEMORY_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def get_history() -> List[Dict[str, object]]:
    return _load_raw().get("history", [])


def get_summary_text(max_items: int = _MAX_HISTORY) -> str:
    history = get_history()[-max_items:]
    if not history:
        return ""
    lines: List[str] = []
    for item in history:
        user_raw = item.get("user")
        user = user_raw.strip() if isinstance(user_raw, str) else (str(user_raw).strip() if user_raw is not None else "")
        assistant_raw = item.get("assistant")
        assistant = (
            assistant_raw.strip()
            if isinstance(assistant_raw, str)
            else (str(assistant_raw).strip() if assistant_raw is not None else "")
        )
        ts = item.get("ts", "")
        meta_obj = item.get("meta")
        meta = meta_obj if isinstance(meta_obj, dict) else {}
        intent = meta.get("intent") if isinstance(meta, dict) else None
        intent_tag = f" (intent={intent})" if intent else ""
        if ts:
            lines.append(f"[{ts}] U{intent_tag}: {user}")
        else:
            lines.append(f"U{intent_tag}: {user}")
        if assistant:
            lines.append(f"A: {assistant}")
    return "\n".join([line for line in lines if line])


def remember_interaction(user_text: str, assistant_text: str, meta: Optional[Dict[str, object]] = None) -> None:
    user_text = (user_text or "").strip()
    assistant_text = (assistant_text or "").strip()
    if not user_text and not assistant_text:
        return
    with _LOCK:
        payload = _load_raw()
        history = payload.get("history", [])
        entry: Dict[str, object] = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "user": user_text,
            "assistant": assistant_text,
        }
        if meta:
            entry["meta"] = meta
        history.append(entry)
        if len(history) > _MAX_HISTORY:
            history = history[-_MAX_HISTORY:]
        payload["history"] = history
        _save_raw(payload)

"""Structured JSONL journal with 6S/6R governance hints."""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterable, Optional

from .config import get_settings


@dataclass
class JournalEntry:
    ts: str
    kind: str
    scope: str
    data: Dict[str, Any]
    safeguards: Dict[str, Iterable[str]]

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


class JournalWriter:
    """Thread-safe JSON line journal writer."""

    def __init__(self, base_dir: Optional[Path] = None) -> None:
        settings = get_settings()
        self._base = Path(base_dir or settings.journal_dir)
        self._lock = Lock()

    def _file_for_today(self) -> Path:
        today = datetime.now().strftime("%Y%m%d")
        return self._base / f"journal_{today}.jsonl"

    @staticmethod
    def _ts() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def record(
        self,
        kind: str,
        data: Dict[str, Any],
        scope: str = "system",
        safeguards: Optional[Dict[str, Iterable[str]]] = None,
    ) -> JournalEntry:
        entry = JournalEntry(
            ts=self._ts(),
            kind=kind,
            scope=scope,
            data=data,
            safeguards=safeguards or {"6S": ["sécurité", "sobriété"], "6R": ["respect", "responsabilité"]},
        )
        line = entry.to_json()
        target = self._file_for_today()
        with self._lock:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        return entry

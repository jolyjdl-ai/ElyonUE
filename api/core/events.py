"""In-memory event buffer with persistence hooks."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict
from threading import Lock
from typing import Any, Deque, Dict, Iterable, List

from .journal import JournalWriter


@dataclass
class Event:
    ts: str
    type: str
    data: Dict[str, Any]

    def asdict(self) -> Dict[str, Any]:
        return asdict(self)


class EventStore:
    """Keeps the last *n* events and mirrors them to the journal."""

    def __init__(self, capacity: int, journal: JournalWriter) -> None:
        self._capacity = capacity
        self._buffer: Deque[Event] = deque(maxlen=capacity)
        self._lock = Lock()
        self._journal = journal

    def append(self, event: Event, mirror: bool = True) -> None:
        with self._lock:
            self._buffer.append(event)
        if mirror:
            payload = {"ts": event.ts, **event.data}
            self._journal.record(kind=event.type, data=payload, scope="event")

    def snapshot(self, limit: int | None = None) -> List[Dict[str, Any]]:
        with self._lock:
            items = list(self._buffer)
        if limit is not None:
            items = items[-limit:]
        return [ev.asdict() for ev in items]

    def seed(self, events: Iterable[Event]) -> None:
        with self._lock:
            for ev in events:
                self._buffer.append(ev)

"""Service orchestrating AI-driven UI layout generation."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .config import get_settings
from .journal import JournalWriter


class UIBuilder:
    """Stores and versions generated UI layouts."""

    def __init__(self, journal: Optional[JournalWriter] = None) -> None:
        settings = get_settings()
        self._base = Path(settings.ui_layout_dir)
        self._journal = journal or JournalWriter(settings.journal_dir)
        self._latest_link = self._base / "latest.json"

    def rebuild(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        layout = {
            "generated_at": timestamp,
            "specification": specification,
            "components": specification.get("components", []),
        }
        self._base.mkdir(parents=True, exist_ok=True)
        target = self._base / f"layout_{timestamp}.json"
        with target.open("w", encoding="utf-8") as fh:
            json.dump(layout, fh, ensure_ascii=False, indent=2)
        # Update latest pointer
        with self._latest_link.open("w", encoding="utf-8") as fh:
            json.dump({"path": target.name, "layout": layout}, fh, ensure_ascii=False, indent=2)
        self._journal.record(
            kind="ui_rebuild",
            data={"layout_file": target.name, "component_count": len(layout["components"])},
            scope="ui",
            safeguards={"6S": ["sobriété", "sens"], "6R": ["responsabilité", "réversibilité"]},
        )
        return layout

    def load_latest(self) -> Optional[Dict[str, Any]]:
        if not self._latest_link.exists():
            return None
        try:
            with self._latest_link.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            layout = payload.get("layout")
            if layout:
                return layout
            # fallback read actual file
            layout_file = payload.get("path")
            if layout_file:
                target = self._base / layout_file
                with target.open("r", encoding="utf-8") as lf:
                    return json.load(lf)
        except Exception:
            return None
        return None

"""Configuration primitives for ÉlyonEU services."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Centralised configuration derived from the environment."""

    project_name: str = Field(default="ElyonEU", description="Display name for the platform")
    version: str = Field(default="0.1.0", description="Semantic version of the backend")

    # Runtime behaviour
    api_host: str = Field(default="127.0.0.1", description="Default bind host for the ASGI server")
    api_port: int = Field(default=8000, description="Default bind port for the ASGI server")

    # Journaling / events
    root_dir: Path = Field(
        default_factory=lambda: Path(
            os.getenv("ELYON_ROOT", str(Path(__file__).resolve().parents[2]))
        ).resolve(),
        description="Project root directory",
    )
    journal_dir: Optional[Path] = Field(default=None, description="Directory for JSONL journals")
    ui_layout_dir: Optional[Path] = Field(default=None, description="Directory storing UI layouts")
    events_retained: int = Field(default=500, description="Number of in-memory events to retain")

    # Identity metadata
    governance_mode: Literal["6S/6R"] = "6S/6R"
    modes: tuple[str, str, str] = ("privé", "gouvernance", "local")

    class Config:
        env_prefix = "ELYON_"
        case_sensitive = False

    def ensure_dirs(self) -> None:
        """Make sure important directories exist."""
        if self.journal_dir is None:
            self.journal_dir = (self.root_dir / "journal").resolve()
        if self.ui_layout_dir is None:
            self.ui_layout_dir = (self.root_dir / "data" / "ui_layouts").resolve()
        for target in (self.journal_dir, self.ui_layout_dir):
            Path(target).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings

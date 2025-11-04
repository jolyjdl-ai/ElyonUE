"""Identity helpers exposed through the API."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .config import get_settings


@dataclass
class Identity:
    name: str
    version: str
    governance: str
    modes: list[str]

    def asdict(self) -> Dict[str, object]:
        return {
            "identity": {
                "name": self.name,
                "version": self.version,
            },
            "governance": self.governance,
            "modes": self.modes,
        }


def get_identity() -> Identity:
    settings = get_settings()
    return Identity(
        name=settings.project_name,
        version=settings.version,
        governance=settings.governance_mode,
        modes=list(settings.modes),
    )

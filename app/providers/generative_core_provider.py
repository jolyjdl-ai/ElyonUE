from __future__ import annotations
import json
from typing import Any, Dict, List, Union
from pydantic import BaseModel
from fastapi.responses import JSONResponse

# import service module (local import)
from app.services import generative_core as service  # type: ignore[import]

JsonPayload = Union[str, bytes, bytearray, memoryview]


def _loads(body: JsonPayload) -> Dict[str, Any]:
    try:
        if isinstance(body, memoryview):
            body = body.tobytes()
        if isinstance(body, (bytes, bytearray)):
            return json.loads(body.decode("utf-8"))
        return json.loads(body)
    except Exception:
        return {}

class GenOut(BaseModel):
    text: str
    used: str

class GenerativeCoreProvider:
    name = "generative_core"

    def generate(self, text: str, mode: str = "normal") -> GenOut:
        req = service.GenRequest(input=text, mode=mode)
        res = service.generate(req)
        # res is a GenResponse Pydantic model (FastAPI returns it directly)
        return GenOut(text=res.text, used=res.used)

    def summarize(self, text: str) -> GenOut:
        return self.generate(text, mode="resume")

    def extract_actions(self, text: str) -> GenOut:
        return self.generate(text, mode="actions")

    def status(self) -> Dict[str, Any]:
        out = service.status()
        if isinstance(out, JSONResponse):
            data = _loads(out.body if hasattr(out, "body") else b"{}")
            if data:
                return data
        if hasattr(out, "body"):
            data = _loads(getattr(out, "body"))
            if data:
                return data
        return out if isinstance(out, dict) else {}

    def config(self, **kw) -> Dict[str, Any]:
        # call update_config with a ConfigPatch-like object or dict
        try:
            patch = service.ConfigPatch(**kw)
        except Exception:
            patch = service.ConfigPatch()
        out = service.update_config(patch)
        if isinstance(out, JSONResponse):
            data = _loads(out.body if hasattr(out, "body") else b"{}")
            if data:
                return data
        return out if isinstance(out, dict) else {"ok": False}

    def get_config(self) -> Dict[str, Any]:
        data = self.status()
        return data.get("config", {}) if isinstance(data, dict) else {}

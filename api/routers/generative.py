from fastapi import APIRouter, Body, HTTPException
from typing import Dict, Any
from app.providers.generative_core_provider import GenerativeCoreProvider

router = APIRouter(prefix="/gen", tags=["generative"])
prov = GenerativeCoreProvider()

@router.get("/status")
def status():
    return prov.status()

@router.post("/generate")
def generate(payload: Dict[str, Any] = Body(...)):
    text = str(payload.get("input", "")).strip()
    mode = str(payload.get("mode", "normal"))
    if not text:
        raise HTTPException(400, "Champ 'input' requis.")
    out = prov.generate(text, mode=mode)
    return out.dict()

@router.post("/summarize")
def summarize(payload: Dict[str, Any] = Body(...)):
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(400, "Champ 'text' requis.")
    return prov.summarize(text).dict()

@router.post("/extract_actions")
def extract_actions(payload: Dict[str, Any] = Body(...)):
    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(400, "Champ 'text' requis.")
    return prov.extract_actions(text).dict()


@router.get("/config")
def get_config():
    return {"config": prov.get_config()}


@router.post("/config")
def patch_config(payload: Dict[str, Any] = Body(...)):
    allowed = {"allow_cloud", "enable_autonomy", "autonomy_min_interval_s", "sixs_threshold"}
    patch = {k: v for k, v in payload.items() if k in allowed}
    if not patch:
        raise HTTPException(400, "Aucun champ valide fourni (allow_cloud, enable_autonomy, autonomy_min_interval_s, sixs_threshold).")
    return prov.config(**patch)

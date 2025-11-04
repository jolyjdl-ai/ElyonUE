from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/sensorium", tags=["Sensorium"])

class SensoriumStatus(BaseModel):
    mic: bool
    cam: bool
    pii_flag: bool
    timestamp: datetime

@router.get("/status", response_model=SensoriumStatus)
async def sensorium_status():
    return SensoriumStatus(mic=True, cam=False, pii_flag=False, timestamp=datetime.now())

@router.post("/set")
async def sensorium_set(status: SensoriumStatus):
    # appliquer la configuration au driver réel ou mock
    print(f"[Sensorium] Update received: {status}")
    return {"ok": True, "timestamp": datetime.now()}

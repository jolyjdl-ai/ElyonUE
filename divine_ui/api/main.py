from fastapi import FastAPI
from agents.sensorium.main import router as sensorium
from agents.ego.main import router as ego
from agents.superego.main import router as superego

app = FastAPI(title="Divine UI — Elyon EU")

app.include_router(sensorium)
app.include_router(ego)
app.include_router(superego)

@app.get("/")
async def root():
    return {"ElyonEU": "online", "message": "Bienvenue dans la Divine UI"}

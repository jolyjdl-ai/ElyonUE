#!/usr/bin/env python3
"""
Simple API launcher pour ÉlyonEU - évite les startup events problématiques
"""
import uvicorn
from elyon_api import app

if __name__ == "__main__":
    print("[API] Démarrage serveur sur http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

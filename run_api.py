#!/usr/bin/env python
"""Lanceur simple de l'API"""
import sys
import os

# Configuration
sys.path.insert(0, r"C:\ElyonEU")
os.chdir(r"C:\ElyonEU\api")

# Imports
from api import elyon_api
import uvicorn

# Démarrage
if __name__ == "__main__":
    print("[LAUNCHER] Starting API on http://127.0.0.1:8000", flush=True)
    uvicorn.run(
        elyon_api.app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
        access_log=True
    )

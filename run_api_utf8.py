#!/usr/bin/env python3
"""Lanceur simple de l'API ÉlyonEU - avec UTF-8 forcé"""
import sys
import os
from pathlib import Path

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configuration
root = Path(__file__).parent
sys.path.insert(0, str(root))
os.chdir(str(root))

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

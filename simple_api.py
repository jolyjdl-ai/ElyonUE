#!/usr/bin/env python3
"""Lanceur super simple de l'API pour debug"""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
root = Path(__file__).parent
sys.path.insert(0, str(root))
os.chdir(str(root))

from api import elyon_api
import uvicorn

if __name__ == "__main__":
    print("[SIMPLE_API] Démarrage...", flush=True)
    uvicorn.run(elyon_api.app, host="127.0.0.1", port=8000, log_level="info")

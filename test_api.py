#!/usr/bin/env python
"""Test simple de l'API sans imports lourds"""
import sys
sys.path.insert(0, r"C:\ElyonEU")

print("[TEST] 1. Import FastAPI...", flush=True)
from fastapi import FastAPI
print("[TEST] 2. OK FastAPI", flush=True)

print("[TEST] 3. Import modules core...", flush=True)
try:
    from api.core import memory, intent, vector_index
    print("[TEST] 4. OK modules core", flush=True)
except Exception as e:
    print(f"[TEST] ERREUR modules core: {e}", flush=True)
    sys.exit(1)

print("[TEST] 5. Import elyon_api...", flush=True)
try:
    from api import elyon_api
    print("[TEST] 6. OK elyon_api importé", flush=True)
except Exception as e:
    print(f"[TEST] ERREUR elyon_api: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[TEST] 7. Lancement API avec uvicorn...", flush=True)
import uvicorn
uvicorn.run(elyon_api.app, host="127.0.0.1", port=8000, log_level="info")

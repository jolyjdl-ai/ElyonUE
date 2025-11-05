#!/usr/bin/env python3
"""Direct API startup with governance modules."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Importer et configurer l'app
from api.elyon_api import app

if __name__ == "__main__":
    import uvicorn
    print("[API] Starting ElyonEU with governance, profiles, and divine...", flush=True)
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

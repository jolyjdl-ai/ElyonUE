#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lanceur pour ÉlyonEU Desktop Premium
Démarre l'API et l'application graphique
"""
import subprocess
import time
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
os.chdir(ROOT)

print("[launcher] === ÉlyonEU Desktop Premium ===", flush=True)
print(f"[launcher] Répertoire: {ROOT}", flush=True)

# Vérifier que l'API n'est pas déjà en cours
print("[launcher] Vérification de l'API...", flush=True)
try:
    import requests
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=2)
        print("[launcher] ✓ API déjà en cours d'exécution", flush=True)
        api_running = True
    except:
        api_running = False
except:
    api_running = False

if not api_running:
    print("[launcher] Démarrage de l'API...", flush=True)
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.elyon_api:app",
         "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("[launcher] Attente 2s pour l'API...", flush=True)
    time.sleep(2)
else:
    api_proc = None

# Démarrer l'app desktop
print("[launcher] Démarrage de l'application Premium...", flush=True)
try:
    from app.elyon_desktop_premium import main
    main()
except KeyboardInterrupt:
    print("\n[launcher] Arrêt demandé", flush=True)
except Exception as exc:
    print(f"[launcher] Erreur: {exc}", flush=True)
    import traceback
    traceback.print_exc()
finally:
    if api_proc:
        print("[launcher] Arrêt de l'API...", flush=True)
        api_proc.terminate()
        try:
            api_proc.wait(timeout=5)
        except:
            api_proc.kill()
    print("[launcher] Fermeture.", flush=True)

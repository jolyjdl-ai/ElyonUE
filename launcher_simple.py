#!/usr/bin/env python3
"""Lanceur simple - juste API + app desktop minimal"""
import subprocess
import time
import sys
import os

# Démarrer l'API
print("Démarrage de l'API...")
api_proc = subprocess.Popen([sys.executable, "simple_api.py"], cwd="C:\\ElyonEU")
time.sleep(2)

# Démarrer le desktop app
print("Démarrage du desktop app...")
try:
    os.chdir("C:\\ElyonEU")
    from app.elyon_desktop_premium import main
    main()
except KeyboardInterrupt:
    print("Arrêt...")
finally:
    api_proc.terminate()
    api_proc.wait()

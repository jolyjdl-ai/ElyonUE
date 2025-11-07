#!/usr/bin/env python3
"""
Lanceur complet ÉlyonEU - API + Desktop
Démarre tout et gère le cycle de vie
"""
import subprocess
import time
import sys
import os
from pathlib import Path

def main():
    print("="*50)
    print("ÉlyonEU - Lanceur Complet (API + Desktop)")
    print("="*50)

    root = Path(__file__).parent
    os.chdir(root)

    # Étape 1: Démarrer l'API
    print("\n[1/2] Démarrage de l'API...")
    api_proc = subprocess.Popen(
        [sys.executable, "run_api_utf8.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
    )
    print("      ⏳ Attente 5 secondes pour démarrage API...")
    time.sleep(5)

    # Vérifier que l'API démarre
    try:
        import requests
        r = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if r.status_code == 200:
            print("      ✓ API prête sur http://127.0.0.1:8000")
        else:
            print(f"      ✗ API répond mais status={r.status_code}")
    except Exception as e:
        print(f"      ⚠ API peut ne pas être prête: {e}")

    # Étape 2: Démarrer l'app desktop
    print("\n[2/2] Lancement de l'application desktop...")
    try:
        subprocess.run([sys.executable, "app/elyon_desktop_premium.py"], check=False)
    except KeyboardInterrupt:
        print("\n✓ Application fermée par l'utilisateur")
    except Exception as e:
        print(f"✗ Erreur: {e}")
    finally:
        # Arrêter l'API
        print("\n[Cleanup] Arrêt de l'API...")
        api_proc.terminate()
        try:
            api_proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            api_proc.kill()
        print("✓ API arrêtée")

    print("\n" + "="*50)
    print("ÉlyonEU - Fermeture complète")
    print("="*50)

if __name__ == "__main__":
    main()

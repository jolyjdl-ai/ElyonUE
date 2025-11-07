#!/usr/bin/env python3
"""Test d'import de tous les composants"""
import sys
from pathlib import Path

root = Path(__file__).parent
sys.path.insert(0, str(root))

print("=" * 60)
print("Test d'imports ÉlyonEU")
print("=" * 60)

# Test 1: API
try:
    from api import elyon_api
    print("✓ api.elyon_api importé")
except Exception as e:
    print(f"✗ Erreur api.elyon_api: {e}")

# Test 2: Governance
try:
    from api.core import governance
    print("✓ api.core.governance importé")
except Exception as e:
    print(f"✗ Erreur api.core.governance: {e}")

# Test 3: Desktop App
try:
    from app.elyon_desktop_premium import ElyonDesktopPremium
    print("✓ app.elyon_desktop_premium.ElyonDesktopPremium importé")
except Exception as e:
    print(f"✗ Erreur app.elyon_desktop_premium: {e}")

# Test 4: Launch Premium
try:
    from app import launch_premium
    print("✓ app.launch_premium importé")
except Exception as e:
    print(f"✗ Erreur app.launch_premium: {e}")

print("\n" + "=" * 60)
print("Tous les imports réussis !")
print("=" * 60)

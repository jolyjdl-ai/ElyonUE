#!/usr/bin/env python
import sys
import traceback

try:
    sys.path.insert(0, r"C:\ElyonEU")
    print("[DEBUG] Importing elyon_api...")
    from api import elyon_api
    print("[DEBUG] SUCCESS: elyon_api imported")
except Exception as e:
    print(f"[DEBUG] ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)

#!/usr/bin/env python
"""Teste l'endpoint /chat avec la phrase officielle"""
import requests
import json

url = "http://127.0.0.1:8000/chat"
payload = {
    "messages": [
        {
            "role": "user",
            "content": "Peux-tu me résumer le plan gouvernance 6S/6R avec urgence, et proposer une prochaine étape opérationnelle alignée à la gouvernance ?"
        }
    ]
}

print("[TEST] Envoi requête /chat...")
try:
    resp = requests.post(url, json=payload, timeout=30)
    print(f"[TEST] Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"[TEST] ✓ Provider: {data.get('provider')}")
        print(f"[TEST] Réponse (premiers 400 chars):\n{data.get('reply', '')[:400]}")
    else:
        print(f"[TEST] ✗ Erreur {resp.status_code}:")
        print(resp.text)
except Exception as e:
    print(f"[TEST] ✗ Exception: {e}")
    import traceback
    traceback.print_exc()

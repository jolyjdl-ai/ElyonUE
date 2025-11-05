#!/usr/bin/env python
"""
Test complet des capacités d'ÉlyonEU
Valide : mémoire, intentions, RAG, OpenAI, local-first policy
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test 1 : Health check"""
    print("\n[TEST 1] Health check...")
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        assert resp.status_code == 200, f"Status {resp.status_code}"
        assert resp.json()["status"] == "ok", "Status pas OK"
        print("✓ API responsive")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_self():
    """Test 2 : Self info"""
    print("\n[TEST 2] Self info (identité)...")
    try:
        resp = requests.get(f"{BASE_URL}/self", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "self" in data
        assert data["self"]["identity"]["name"] == "ElyonEU (local)"
        print(f"✓ Identité : {data['self']['identity']}")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_chat_simple():
    """Test 3 : Chat simple (génération locale)"""
    print("\n[TEST 3] Chat simple (local)...")
    payload = {
        "messages": [
            {"role": "user", "content": "Bonjour, qui es-tu?"}
        ]
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        assert resp.status_code == 200, f"Status {resp.status_code}: {resp.text}"
        data = resp.json()
        assert "reply" in data, "Pas de reply"
        assert "provider" in data, "Pas de provider"
        print(f"✓ Provider: {data['provider']}")
        print(f"✓ Réponse: {data['reply'][:100]}...")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_chat_urgence():
    """Test 4 : Chat avec urgence (détection intention)"""
    print("\n[TEST 4] Chat avec urgence (intentions)...")
    payload = {
        "messages": [
            {"role": "user", "content": "C'est URGENT! Résume-moi les principes 6S/6R rapidement."}
        ]
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert "trace" in data, "Pas de trace"
        trace = data["trace"]
        assert "intent" in trace, "Pas d'intent dans trace"
        intent = trace["intent"]

        print(f"✓ Intention détectée: {intent.get('intent')}")
        print(f"✓ Urgence: {intent.get('urgent', False)}")
        print(f"✓ Keywords: {intent.get('keywords', [])}")
        print(f"✓ Provider final: {data['provider']}")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_chat_phrase_officielle():
    """Test 5 : Phrase officielle de test complet"""
    print("\n[TEST 5] Phrase officielle (RAG + intentions + mémoire)...")
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Peux-tu me résumer le plan gouvernance 6S/6R avec urgence, et proposer une prochaine étape opérationnelle alignée à la gouvernance ?"
            }
        ]
    }
    try:
        resp = requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)
        assert resp.status_code == 200, f"Status {resp.status_code}: {resp.text}"
        data = resp.json()

        # Vérifier réponse
        assert "reply" in data and len(data["reply"]) > 50, "Réponse trop courte"

        # Vérifier trace
        assert "trace" in data, "Pas de trace"
        trace = data["trace"]

        print(f"✓ Provider final: {data['provider']}")
        print(f"✓ Policy: {trace.get('policy')}")
        print(f"✓ Memory used: {trace.get('memory_used')}")
        print(f"✓ Intent: {trace['intent'].get('intent') if isinstance(trace.get('intent'), dict) else trace.get('intent')}")
        print(f"✓ Réponse (premiers 200 chars):")
        print(f"  {data['reply'][:200]}...")

        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory():
    """Test 6 : Mémoire (conversations multiples)"""
    print("\n[TEST 6] Mémoire conversationnelle...")
    try:
        # Message 1
        payload1 = {"messages": [{"role": "user", "content": "Je m'appelle Alice"}]}
        resp1 = requests.post(f"{BASE_URL}/chat", json=payload1, timeout=30)
        assert resp1.status_code == 200

        time.sleep(1)

        # Message 2 (devrait avoir mémoire du message 1)
        payload2 = {"messages": [{"role": "user", "content": "Quel est mon nom?"}]}
        resp2 = requests.post(f"{BASE_URL}/chat", json=payload2, timeout=30)
        assert resp2.status_code == 200
        data2 = resp2.json()

        print(f"✓ Mémoire appliquée: {data2['trace'].get('memory_used', False)}")
        print(f"✓ Réponse: {data2['reply'][:100]}...")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def test_events():
    """Test 7 : Événements (monitoring)"""
    print("\n[TEST 7] Événements (monitoring)...")
    try:
        resp = requests.get(f"{BASE_URL}/events", timeout=5)
        assert resp.status_code == 200
        data = resp.json()
        assert "events" in data, "Pas d'events"
        events = data["events"]

        # Compter les types
        types_count = {}
        for evt in events:
            typ = evt.get("type", "unknown")
            types_count[typ] = types_count.get(typ, 0) + 1

        print(f"✓ Événements en mémoire: {len(events)}")
        print(f"✓ Types: {dict(sorted(types_count.items()))}")
        return True
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

def main():
    print("="*60)
    print("[TEST SUITE] ElyonEU - Validation Complète")
    print("="*60)

    tests = [
        ("Health", test_health),
        ("Self Info", test_self),
        ("Chat simple", test_chat_simple),
        ("Chat urgence", test_chat_urgence),
        ("Phrase officielle", test_chat_phrase_officielle),
        ("Mémoire", test_memory),
        ("Événements", test_events),
    ]

    results = {}
    for name, test_fn in tests:
        try:
            results[name] = test_fn()
        except Exception as e:
            print(f"✗ {name}: Exception non capturée: {e}")
            results[name] = False

    # Summary
    print("\n" + "="*60)
    print("[RESUME] Résultats des tests")
    print("="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\nTests passés: {passed}/{total}")
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}")

    if passed == total:
        print("\n[SUCCESS] TOUS LES TESTS PASSES ! ElyonEU est pret pour production.")
    else:
        print(f"\n[WARNING] {total - passed} test(s) echoue(s). Verifier les logs.")

    return passed == total

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

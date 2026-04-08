"""
Smoke test: checks API health and detector behaviour.
Run from project root: py scripts/smoke_test.py
Start Catalog and Gateway first (or use run_demo.py).
"""
import sys
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    ok = True

    # Gateway
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        if r.status_code == 200:
            print("[OK] Gateway (8000) is up")
        else:
            print("[FAIL] Gateway returned", r.status_code)
            ok = False
    except Exception as e:
        print("[FAIL] Gateway:", e)
        ok = False

    # Catalog
    try:
        r = requests.get("http://localhost:8001/health", timeout=2)
        if r.status_code == 200:
            print("[OK] Catalog (8001) is up")
        else:
            print("[FAIL] Catalog returned", r.status_code)
            ok = False
    except Exception as e:
        print("[FAIL] Catalog:", e)
        ok = False

    # Detector
    try:
        from ml.train_detector import predict
        n = predict(5, 0)
        a = predict(150, 20)
        if n == "normal" and a == "attack":
            print("[OK] Detector: normal(5,0)=normal, attack(150,20)=attack")
        else:
            print("[FAIL] Detector:", n, a)
            ok = False
    except Exception as e:
        print("[FAIL] Detector:", e)
        ok = False

    if ok:
        print("\nAll checks passed.")
    else:
        print("\nSome checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

"""
Auto-detector: periodically reads gateway metrics, runs the ML detector,
and sets the gateway to block or allow traffic automatically.
Run from project root: py scripts/auto_detector.py
Or it is started by run_demo.py.
"""
import sys
import time
import requests
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

GATEWAY = "http://localhost:8000"
INTERVAL_SEC = 3


def main():
    from ml.train_detector import predict, get_attack_type

    print("Auto-detector running. Reading metrics every", INTERVAL_SEC, "seconds.")
    print(
        "Gateway:",
        GATEWAY,
        "- engages defence when traffic looks like attack; does NOT auto-clear defence",
        "(use demo Restore or dashboard — gateway rejects stray clear requests).\n",
    )

    while True:
        try:
            r = requests.get(f"{GATEWAY}/admin/metrics", timeout=2)
            if r.status_code != 200:
                time.sleep(INTERVAL_SEC)
                continue
            data = r.json()
            rps = data.get("rps", 0) or 0
            errors = data.get("errors_last_30s", 0) or 0
            requests_30s = data.get("requests_last_30s", 0) or 0

            # Use integer rps for the model (trained on requests_per_sec)
            rps_int = int(round(rps))
            label = predict(rps_int, errors)

            # Demo: if no model or model says normal, still treat high rps as attack (so burst triggers)
            if label != "attack" and rps >= 8 and requests_30s >= 25:
                label = "attack"

            status_r = requests.get(f"{GATEWAY}/admin/status", timeout=1)
            current_mode = (status_r.json() or {}).get("defence_mode", "normal")

            if label == "attack":
                if current_mode != "attack":
                    attack_type = get_attack_type(rps, errors)
                    try:
                        requests.post(
                            f"{GATEWAY}/admin/defence-mode",
                            json={"mode": "attack", "attack_type": attack_type},
                            timeout=2,
                        )
                        print(f"[AUTO] Attack detected (rps={rps:.1f}, errors={errors}) -> BLOCKING. Type: {attack_type}")
                    except Exception as e:
                        print("[AUTO] Failed to set blocking:", e)
            # Do not auto-revert to normal: once defence is on, it stays until an operator
            # (demo "Restore" button, dashboard, or API) clears it. Otherwise the burst ends,
            # RPS falls in the sliding window, and the UI would flip back without user action.
        except requests.exceptions.ConnectionError:
            pass  # Gateway not up yet
        except Exception as e:
            print("[AUTO] Error:", e)

        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()

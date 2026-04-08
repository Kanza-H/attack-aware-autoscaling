"""
Collect metrics while sending traffic - writes CSV for ML dataset.
Usage:
  python collect_metrics.py normal   # Steady traffic, label=normal
  python collect_metrics.py attack   # Burst traffic, label=attack
Run each for 1-2 minutes, then combine the CSV for training.
"""
import time
import requests
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

API_URL = "http://localhost:8000"
CSV_PATH = Path(__file__).parent.parent / "data" / "metrics.csv"

def run_normal(window_sec=60, req_per_sec=5):
    """Steady load for window_sec, record requests per second and success rate."""
    label = "normal"
    interval = 1.0 / req_per_sec
    start = time.time()
    rows = []

    while time.time() - start < window_sec:
        window_start = time.time()
        count, errors = 0, 0
        while time.time() - window_start < 1.0:
            t0 = time.perf_counter()
            try:
                r = requests.get(f"{API_URL}/products", timeout=2)
                count += 1 if r.status_code == 200 else 0
                if r.status_code != 200:
                    errors += 1
            except Exception:
                errors += 1
            time.sleep(max(0, interval - (time.perf_counter() - t0)))

        rows.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requests_per_sec": count,
            "errors": errors,
            "label": label,
        })

    return rows

def run_attack(window_sec=60, burst_size=200, workers=30):
    """Burst load for window_sec, record requests per second and success rate."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    label = "attack"

    def one():
        try:
            r = requests.get(f"{API_URL}/products", timeout=5)
            return 1 if r.status_code == 200 else 0
        except Exception:
            return 0

    start = time.time()
    rows = []
    while time.time() - start < window_sec:
        window_start = time.time()
        ok = 0
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(one) for _ in range(burst_size)]
            ok = sum(f.result() for f in as_completed(futures))
        rows.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "requests_per_sec": ok,
            "errors": burst_size - ok,
            "label": label,
        })
        # One burst per second
        while time.time() - window_start < 1.0:
            time.sleep(0.1)

    return rows

def main():
    mode = (sys.argv[1] or "normal").lower()
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = CSV_PATH.exists()

    if mode == "normal":
        rows = run_normal(window_sec=60, req_per_sec=5)
    elif mode == "attack":
        rows = run_attack(window_sec=60, burst_size=200, workers=30)
    else:
        print("Usage: python collect_metrics.py normal | attack")
        sys.exit(1)

    with open(CSV_PATH, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp", "requests_per_sec", "errors", "label"])
        if not file_exists:
            w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows to {CSV_PATH} (label={mode})")

if __name__ == "__main__":
    main()

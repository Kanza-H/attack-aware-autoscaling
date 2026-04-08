"""
Attack traffic generator: burst of many concurrent requests (DDoS simulation).
Run with: python traffic_attack.py
Make sure the API is running first: docker compose up -d (from project root).
"""
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

API_URL = "http://localhost:8000"
CONCURRENT_WORKERS = 50   # Many parallel requests
REQUESTS_PER_BURST = 500  # Total requests per burst
DURATION_SECONDS = 20     # Run attack for 20 seconds

def one_request():
    try:
        r = requests.get(f"{API_URL}/products", timeout=5)
        return r.status_code
    except Exception:
        return None

def main():
    print(f"Attack traffic: {CONCURRENT_WORKERS} workers, {REQUESTS_PER_BURST} requests per burst, {DURATION_SECONDS}s -> {API_URL}")
    start = time.time()
    total_ok = 0
    total_err = 0

    while time.time() - start < DURATION_SECONDS:
        with ThreadPoolExecutor(max_workers=CONCURRENT_WORKERS) as ex:
            futures = [ex.submit(one_request) for _ in range(REQUESTS_PER_BURST)]
            for f in as_completed(futures):
                code = f.result()
                if code == 200:
                    total_ok += 1
                else:
                    total_err += 1

    elapsed = time.time() - start
    total = total_ok + total_err
    print(f"Done. Requests: {total}, OK: {total_ok}, Errors: {total_err}, Time: {elapsed:.1f}s, Rate: {total/elapsed:.0f} req/s")

if __name__ == "__main__":
    main()

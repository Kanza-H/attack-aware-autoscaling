"""
Normal traffic generator: steady, low rate of requests.
Run with: python traffic_normal.py
Make sure the API is running first: docker compose up -d (from project root).
"""
import time
import requests

API_URL = "http://localhost:8000"
REQUESTS_PER_SECOND = 5
DURATION_SECONDS = 30  # Run for 30 seconds (change as needed)

def main():
    print(f"Normal traffic: {REQUESTS_PER_SECOND} req/s for {DURATION_SECONDS}s -> {API_URL}")
    start = time.time()
    count = 0
    errors = 0
    interval = 1.0 / REQUESTS_PER_SECOND

    while time.time() - start < DURATION_SECONDS:
        t0 = time.perf_counter()
        try:
            r = requests.get(f"{API_URL}/products", timeout=2)
            if r.status_code == 200:
                count += 1
            else:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"  Error: {e}")
        elapsed = time.perf_counter() - t0
        sleep_time = max(0, interval - elapsed)
        time.sleep(sleep_time)

    total = time.time() - start
    print(f"Done. Requests: {count}, Errors: {errors}, Time: {total:.1f}s, Rate: {count/total:.1f} req/s")

if __name__ == "__main__":
    main()

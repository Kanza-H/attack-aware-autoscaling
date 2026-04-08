"""
One-command demo: starts Catalog, Gateway, then Dashboard.
Run from project root: py run_demo.py
Press Ctrl+C to stop — child processes are terminated via atexit.
"""
import atexit
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

HEALTH_URL = "http://127.0.0.1:8000/health"


def _wait_for_gateway(timeout_sec: float = 25.0) -> bool:
    """Give uvicorn a moment to bind before we print URLs (avoids 'refused connection' if you click too fast)."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=1.5) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, OSError, TimeoutError):
            pass
        time.sleep(0.4)
    return False


def main():
    catalog_dir = PROJECT_ROOT / "services" / "catalog"
    gateway_dir = PROJECT_ROOT / "services" / "api"
    procs = []

    def kill_children():
        for p in procs:
            try:
                p.terminate()
                p.wait(timeout=3)
            except Exception:
                p.kill()
    atexit.register(kill_children)

    print("Starting Catalog (port 8001)...")
    p1 = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd=catalog_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    procs.append(p1)

    print("Starting Gateway (port 8000)...")
    p2 = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=gateway_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    procs.append(p2)

    website_dir = PROJECT_ROOT / "website"
    print("Starting Website (port 3000)...")
    p_web = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3000"],
        cwd=website_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    procs.append(p_web)

    time.sleep(1.5)
    print("Waiting for gateway health check…")
    if _wait_for_gateway():
        print("  -> Gateway is up (http://localhost:8000)")
    else:
        print("  -> Warning: gateway did not respond in time — open http://localhost:3000/demo.html after a few seconds.")

    print("Starting Auto-detector (can engage defence; clearing requires demo/dashboard — sticky gateway policy)...")
    p_auto = subprocess.Popen(
        [sys.executable, "scripts/auto_detector.py"],
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    procs.append(p_auto)

    time.sleep(1)
    print("Starting Dashboard (port 8501)...")
    print()
    print("  Open in browser (same machine):")
    print("    Live demo:        http://localhost:3000/demo.html")
    print("    Fair / hall mode: http://localhost:3000/demo.html?showcase=1  (big impact #, hook line, R/N keys)")
    print("    Shop (iframe): http://localhost:3000/index.html")
    print("    Dashboard:     http://localhost:8501")
    print("    Gateway API:   http://localhost:8000/health")
    print()
    print("  Press Ctrl+C in this window to stop all services.\n")

    p3 = subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "dashboard/streamlit_app.py", "--server.headless", "true"],
        cwd=PROJECT_ROOT,
    )
    sys.exit(p3.returncode)


if __name__ == "__main__":
    main()

# Run without Docker (if Docker isn't installed)

If `docker` is not recognized, you can still run the API and scripts with Python.

---

## Step 1: Install Python

1. If you don't have Python: https://www.python.org/downloads/ — download and install **Python 3.9+**.
2. During install, tick **"Add Python to PATH"**.
3. Open a **new** Command Prompt and check:
   ```bash
   python --version
   ```
   (On Windows you may need `py --version`.)

---

## Step 2: Run the API with Python (no Docker)

1. Open Command Prompt and go to your dissertation folder:
   ```bash
   cd OneDrive\Documents\attack-aware-autoscaling
   ```
2. Go into the API folder and install dependencies:
   ```bash
   cd services\api
   pip install fastapi uvicorn
   ```
   (If `pip` fails, try: `py -m pip install fastapi uvicorn`.)
3. Start the API:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Leave this window open. In your browser open:
   - http://localhost:8000
   - http://localhost:8000/docs

**Done when:** Both pages load.

---

## Step 3: Send traffic (in a second Command Prompt)

1. Open a **new** Command Prompt.
2. Go to the project root (not services\api):
   ```bash
   cd OneDrive\Documents\attack-aware-autoscaling
   pip install requests
   python scripts\traffic_normal.py
   ```
3. Then try attack traffic:
   ```bash
   python scripts\traffic_attack.py
   ```

---

## Step 4: Collect metrics for ML

With the API still running (first window):

```bash
cd OneDrive\Documents\attack-aware-autoscaling
python scripts\collect_metrics.py normal
python scripts\collect_metrics.py attack
```

Check that `data\metrics.csv` was created.

---

**Later:** When you install Docker, you can use `docker compose up -d` instead and follow the main README / STEP_BY_STEP.

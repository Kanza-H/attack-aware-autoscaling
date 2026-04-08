# Step-by-step: what to do and in what order

**This is your Final Year (Year 3) dissertation project.** Do one step at a time.

---

## Step 1: Get the microservice running (do this first)

**Goal:** You see the API in your browser.

1. Open a terminal (PowerShell or Command Prompt).
2. Go to your **dissertation project folder** (not the accessibility folder):
   ```bash
   cd OneDrive\Documents\attack-aware-autoscaling
   ```
   Or if you're in `Documents` already:
   ```bash
   cd attack-aware-autoscaling
   ```
3. Start the service:
   ```bash
   docker compose up -d
   ```
4. Open your browser:
   - http://localhost:8000  → short message, "service": "api"
   - http://localhost:8000/docs  → API docs (Swagger)

**Done when:** Both URLs load.

**If you get "docker is not recognized":** Docker isn't installed (or not on your PATH). You can either:
- **Install Docker Desktop:** https://www.docker.com/products/docker-desktop/ then run `docker compose up -d` again, or
- **Run without Docker:** open **RUN_WITHOUT_DOCKER.md** in this folder and follow those steps (run the API with Python instead).

---

## Step 2: Send "normal" traffic

1. API still running. In a **new** terminal:
   ```bash
   cd OneDrive\Documents\attack-aware-autoscaling
   python scripts/traffic_normal.py
   ```
   (Windows: try `py scripts/traffic_normal.py` if `python` fails.)

**Done when:** Script runs and prints request count.

---

## Step 3: Send "attack" traffic

1. In terminal:
   ```bash
   cd OneDrive\Documents\attack-aware-autoscaling
   python scripts/traffic_attack.py
   ```

**Done when:** You see a high req/s rate (attack = much higher than normal).

---

## Step 4: Collect data for ML

1. Run (about 1 min each):
   ```bash
   python scripts/collect_metrics.py normal
   python scripts/collect_metrics.py attack
   ```
2. Check `data/metrics.csv` has rows with label "normal" and "attack".

**Done when:** CSV exists with both labels.

---

## Step 5: Train the detector (ML)

**Goal:** Train a classifier from your CSV and save the model.

1. In the same terminal (in `attack-aware-autoscaling`):
   ```powershell
   py -m pip install scikit-learn
   py ml/train_detector.py
   ```
2. You should see "Model accuracy ..." and "Model saved to ... ml/model.joblib".
3. The model is now saved; the scaler (Step 6) will use it to decide "normal" vs "attack".

---

## Step 6: Smart scaling (demo)

**Goal:** Show that when the detector says "attack", we don't scale up.

1. From `attack-aware-autoscaling` run:
   ```powershell
   py scripts\scaler_demo.py 5 0
   ```
   You should see: Detector says "normal", Scaler decision: allow scale up.

2. Then run:
   ```powershell
   py scripts\scaler_demo.py 150 20
   ```
   You should see: Detector says "attack", Scaler decision: do NOT scale up.

This is the core idea: attack-aware scaling.

---

## Step 7: Dashboard

**Goal:** One page showing traffic, Attack Yes/No, and scaler decision.

1. From `attack-aware-autoscaling`:
   ```powershell
   py -m pip install streamlit pandas
   py -m streamlit run dashboard/streamlit_app.py
   ```
2. Browser opens to the dashboard. Enter requests/sec and errors, click "Get detector & scaler decision" to see Normal vs Attack.
3. Use this page in your presentation to show the system live.

---

## Step 8: Polish and practice for the presentation

**Goal:** One command to run, 3–5 min demo, practice talk.

---

Start with **Step 1** in the folder **attack-aware-autoscaling** (in Documents), not inside accessibility-project.

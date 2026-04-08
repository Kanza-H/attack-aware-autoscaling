# Attack-Aware Autoscaling for Microservices

**Final Year Project (Year 3)** – When servers get full with **normal** traffic we add servers; when an **attack** is detected we block it and do **not** add servers (save cost, protect service).

> **Student quick start:** open **`FYP_START_HERE.md`** (in Cursor: **Ctrl+P** → type `fyp`) or **`HOW_TO_RUN.md`** (type `how`). If search is awkward, click the file in the left **Explorer** list.

---

## Architecture (microservices)

```
                    ┌─────────────────┐
                    │   Dashboard     │  (Streamlit, port 8501)
                    │   Monitor + UI  │
                    └────────┬────────┘
                             │ HTTP
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
    │   Gateway   │  │   Detector  │  │   Scripts   │
    │  (FastAPI)  │  │  (ML model) │  │ traffic, ML │
    │  port 8000  │  │  (in-memory)│  │   (Python)  │
    └──────┬──────┘  └─────────────┘  └─────────────┘
           │
           │ HTTP (get products)
           ▼
    ┌─────────────┐
    │   Catalog   │  (FastAPI, port 8001)
    │   Products  │
    └─────────────┘
```

- **Catalog** – Microservice that serves product data.
- **Gateway** – Entry point for all traffic. Forwards to Catalog when traffic is normal; under attack returns 429 (block) instead of scaling.
- **Dashboard** – Shows status, traffic snapshot, detector/scaler decision, and API defence (block/normal).
- **Detector** – ML model (normal vs attack). Used by dashboard and scaler demo.

---

## One-command run (for presentation)

**Prerequisites (once):** Install dependencies and train the model.

```powershell
cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling
py -m pip install fastapi uvicorn requests streamlit pandas scikit-learn
py scripts\collect_metrics.py normal
py scripts\collect_metrics.py attack
py ml\train_detector.py
```

**Run the full demo (Catalog + Gateway + Dashboard):**

```powershell
cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling
py run_demo.py
```

Then open **http://localhost:8501** in your browser (Streamlit may open it automatically). Press **Ctrl+C** in the terminal to stop.

---

## Run manually (3 terminals)

If you prefer to see each service in its own terminal:

**Terminal 1 – Catalog**
```powershell
cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling\services\catalog
py -m pip install fastapi uvicorn
py -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**Terminal 2 – Gateway**
```powershell
cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling\services\api
py -m pip install fastapi uvicorn requests
py -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 3 – Dashboard**
```powershell
cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling
py -m pip install streamlit pandas
py -m streamlit run dashboard\streamlit_app.py
```

---

## Presentation demo flow (3–5 min)

1. **Problem:** Autoscaling can’t tell real users from attack, so it scales during DDoS and wastes money.
2. **Solution:** We detect attack vs normal with ML; we only add servers when traffic is normal; under attack we block instead of scaling.
3. **Show architecture:** Point to the diagram above (or a slide).
4. **One command:** Run `py run_demo.py`, open http://localhost:8501.
5. **Dashboard – Normal:** Enter 5 req/s, 0 errors → Get decision → “Normal” → “Add new servers when full.”
6. **Dashboard – Attack:** Enter 150 req/s, 20 errors → Get decision → “ATTACK” → “Do NOT add servers. Block attack traffic.” → Click **“Apply: block attack traffic on API”**.
7. **Show blocking:** In another terminal run `py scripts\traffic_attack.py` – many 429s. Say: “Attack traffic is now blocked; we didn’t add servers.”
8. **Back to normal:** In dashboard click “Set API: Normal (allow all)”. Run `py scripts\traffic_normal.py` – requests succeed.

---

## Smoke test

With Catalog and Gateway running:

```powershell
py scripts\smoke_test.py
```

Checks: Gateway up, Catalog up, Detector (normal/attack) behaviour.

---

## Demo website (show Normal vs Blocking on a real page)

A simple **storefront** that calls the Gateway so you can show blocking on an actual site:

1. Start backend (e.g. `py run_demo.py`).
2. In a **new** terminal:
   ```powershell
   cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling\website
   py -m http.server 3000
   ```
3. Open **http://localhost:3000** in your browser — you see the catalog (products).
4. In the **dashboard** click "Set API: Blocking". Refresh **http://localhost:3000** — the page shows **429 Rate limited** and "Attack defence active".
5. Click "Set API: Normal" in the dashboard and refresh the website — products load again.

So: **website (3000) → Gateway (8000) → Catalog (8001)**. The site is the “microservice website”; the dashboard is the control panel.

---

## Project structure

```
attack-aware-autoscaling/
├── run_demo.py           # One-command start (Catalog + Gateway + Dashboard)
├── website/              # Demo storefront (http.server 3000) — shows Normal vs Blocking
├── services/
│   ├── api/              # Gateway (FastAPI, 8000) – defence, calls Catalog
│   └── catalog/          # Catalog (FastAPI, 8001) – products
├── scripts/              # Traffic, collect_metrics, scaler_demo, smoke_test
├── data/                 # metrics.csv for ML
├── ml/                   # Detector (train + predict)
├── dashboard/            # Streamlit dashboard
├── README.md
├── STEP_BY_STEP.md
└── RUN_WITHOUT_DOCKER.md
```

---

## Requirements

- Python 3.9+

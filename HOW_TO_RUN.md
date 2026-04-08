# Step-by-step: How to run the demo

Do these steps **in order**. Use one PowerShell or Command Prompt window.

---

## Step 1: Open a terminal

- Press **Win + R**, type `powershell`, press Enter.  
  **Or** in VS Code / Cursor: **Terminal → New Terminal**.

---

## Step 2: Go to the project folder

Copy and paste this (then press Enter):

```powershell
cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling
```

You must be in the folder that **contains** `run_demo.py` and the `website` folder.  
To check: type `dir` and press Enter. You should see `run_demo.py`, `website`, `dashboard`, `services`, etc.

---

## Step 3: Start everything with one command

Copy and paste this (then press Enter):

```powershell
py run_demo.py
```

Wait a few seconds. You should see something like:

- Starting Catalog (port 8001)...
- Starting Gateway (port 8000)...
- Starting Website (port 3000)...
- Starting Dashboard (port 8501)...
- Live demo: **http://localhost:3000/demo.html**
- Shop (catalog UI): **http://localhost:3000/index.html**
- Dashboard: **http://localhost:8501**
- Gateway check: **http://localhost:8000/health**

**Leave this window open.** Do not close it and do not press Ctrl+C yet. If you do, everything stops.

---

## Step 4: Open the demo in your browser

1. Open **Chrome** or **Edge** (or any browser).
2. In the address bar type: **http://localhost:3000/demo.html**
3. Press Enter.

You should see:
- The demo page with **Run live scenario** and **Restore normal ops**
- The live shop iframe below
- The pipeline (Shop → Gateway → Catalog)

If you opened the page before starting the stack, wait until the terminal shows the gateway is up, then refresh — or follow the amber banner at the top of the demo page.

---

## Step 5: Try the demo

1. Click **“Run live scenario”**.  
   - After a few seconds, defence should engage: red strip, gateway shows **Blocking**, shop iframe shows the **429 / defence** message (or errors if the stack is not running).
2. Click **“Restore normal ops”**.  
   - Gateway returns to normal; the shop iframe loads the catalog again after it refreshes.

---

## When you’re done

- Go back to the terminal where `py run_demo.py` is running.
- Press **Ctrl+C** to stop everything.

---

## If something goes wrong

| Problem | What to do |
|--------|------------|
| “can't open file 'run_demo.py'” | You’re in the wrong folder. Do **Step 2** again and make sure you’re in `attack-aware-autoscaling` (not inside `website`). |
| “localhost refused to connect” | Make sure **Step 3** is still running (terminal open, no Ctrl+C). Wait 5–10 seconds after starting, then try the link again. |
| Port already in use | Something else is using 3000, 8000, 8001, or 8501. Close other terminals or apps using those ports, then run **Step 3** again. |

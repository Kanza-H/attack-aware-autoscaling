# Quick Open (Ctrl+P) shows nothing — fix checklist

If you type in the search box and **no files appear**, try these in order.

---

## 1) Confirm you are using the right shortcut

- **Quick Open (files):** `Ctrl+P`
- **Command Palette (commands):** `Ctrl+Shift+P`

If you use **Ctrl+Shift+P**, you will see **commands**, not your project files.  
For file names, use **`Ctrl+P`**.

---

## 2) Check the Explorer (this tells us what is wrong)

Click the **Explorer** icon on the left (top icon — two pages).

- **If the file list is empty or almost empty:** Cursor does not see your project files (wrong folder, or OneDrive not downloaded — see §5).
- **If you see `run_demo.py`, `README.md`, folders…** your files are there; Quick Open may be bugged or blocked by a setting (see §4).

**You do not need Quick Open:** you can **click any file** in the Explorer to open it.

---

## 3) Reload the window

`Ctrl+Shift+P` → type **Reload Window** → run **Developer: Reload Window**.

Then try **`Ctrl+P`** again and type **`how`** (for `HOW_TO_RUN.md`).

---

## 4) User settings might be hiding all files

Sometimes **`files.exclude`** in **user** settings is set too aggressively (e.g. hiding everything).

1. `Ctrl+,` (Settings)
2. Search: **`files exclude`**
3. Look at **Files: Exclude** — remove any rule that looks like `**/*` or blocks your whole project.

Also search **`search exclude`** and check **Search: Exclude** the same way.

---

## 5) OneDrive “Files On-Demand”

If the project is under **OneDrive\Documents**, files might be **online-only** until opened once.

- In **File Explorer**, go to  
  `C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling`
- Right‑click the folder → **Always keep on this device** (if available).
- Open **`HOW_TO_RUN.md`** once with double‑click (downloads the file).

---

## 6) Open a file without Quick Open

- **File → Open File…** → browse to  
  `C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling\HOW_TO_RUN.md`

Or drag **`HOW_TO_RUN.md`** from File Explorer into Cursor.

---

## 7) Still broken?

Note: Does **Explorer** show your files? (Yes / No)  
And: does **`Ctrl+Shift+P`** → **Reload Window** help?

Tell whoever is helping you those two answers — it narrows it down fast.

# Screenshots — add to existing slides only (no new slides)

You have **6 images** and **no extra slides**. Put them on **3 slides only**: 15, 16, and 18. Two images per slide, small so the slide text still fits.

---

## Slide 15 — What I built (overview)

**Add 2 images** (side by side or one above the other).

| Image | File / what it is | One-line caption to put under it |
|-------|-------------------|-----------------------------------|
| **Code: demo.html** | VS Code with `website/demo.html` (pipeline, status, buttons) | *Frontend: demo page (pipeline, Simulate attack / Restore normal) — same gateway as dashboard.* |
| **Code: streamlit_app.py** | VS Code with `fetch_backend_status()`, GATEWAY_URL, retries | *Dashboard: fetches gateway state (no cache, retries) so it matches the demo.* |

**What to say (same as now, then point at pics):**  
“I built the backend, dashboard, and demo website. Here’s the demo page code and the dashboard code that keeps the state in sync.”

---

## Slide 16 — What you'll see in the demo

**Add 2 images** (side by side or stacked).

| Image | File / what it is | One-line caption to put under it |
|-------|-------------------|-----------------------------------|
| **Demo page — defence on** | Red “Defence active” banner, pipeline (Shop → Gateway → Catalog), Blocked count | *Demo page: defence active, gateway blocking (429), blocked count visible.* |
| **Shop in defence** | Shop with “We're protecting the system” and “Defence active” pill | *Shop when blocking: users see this until we click Restore normal.* |

**What to say (same as now, then point at pics):**  
“You’ll see the demo page and the shop. When I click Simulate attack, the gateway goes red and the shop shows this — we’re protecting the system. Then Restore normal and the shop is back.”

---

## Slide 18 — What the demo showed

**Add 2 images** (side by side or stacked).

| Image | File / what it is | One-line caption to put under it |
|-------|-------------------|-----------------------------------|
| **Dashboard — BLOCKING** | Red banner “BLOCKING”, Gateway: Blocking, attack type, blocked count | *Dashboard: same gateway — shows BLOCKING and attack type when we’re in defence.* |
| **Live metrics + history** | 884 blocked, Defence History table (normal ↔ attack, attack types) | *Live metrics and defence history — blocked count and when we switched to block.* |

**What to say (same as now, then point at pics):**  
“The demo showed classification, blocking with 429, and the same state on shop and dashboard. Here’s the dashboard in blocking mode and the live metrics and history.”

---

## Quick reference — which image on which slide

| Slide | Images (2 per slide) |
|-------|----------------------|
| **15** | demo.html code + streamlit_app.py code |
| **16** | Demo page (red defence) + Shop (“We're protecting the system”) |
| **18** | Dashboard (BLOCKING) + Live metrics & defence history |

No new slides. Resize images so the slide title and your bullets still fit (e.g. half width each or 40% each with a gap). Use the one-line captions in the table under each image.

# Exemplary 20-slide build (for strict marker)

**Marker cares about:** the idea, design, clarity, and a working demo — not implementation detail.  
**Design rule:** One idea per slide. Same theme on every slide (white/light background, black text). No walls of text.

Use this in PowerPoint: copy each slide’s content exactly. Follow the **Design** line so it looks professional.

---

## Slide 1 — Title

**Title:** Attack-Aware Autoscaling for Microservices
**Subtitle:** Final Year Project  
**Line 3:** [Your name] · [Course] · [Date]

**Design:** Title large and centred. Subtitle and your name smaller. No bullets. Plenty of white space.

---

## Slide 2 — What I'm going to cover

**Title:** What I'm going to cover

**Bullets:**
- Problem: autoscaling can't tell real users from attack
- Solution: classify traffic with ML; scale when normal, block when attack
- Microservices context: Gateway + Catalog
- Live demo

**Design:** Four bullets only. Same font as rest of deck. No images needed.

---

## Slide 3 — The problem (1)

**Title:** Why normal autoscaling is a problem

**Bullets:**
- When traffic spikes, systems often scale up (add servers) to handle the load
- They don't distinguish between real users and attackers — both look like "high traffic"
- So the same scaling logic applies to legitimate demand and to attack traffic

**Design:** Three bullets. One idea: “autoscaling can’t tell friend from foe.”

---

## Slide 4 — The problem (2)

**Title:** What goes wrong during an attack

**Bullets:**
- During a DDoS or brute force, traffic looks like high load — the system can't tell the difference
- Autoscaler adds more servers → you pay for attack traffic (infrastructure cost scales with the attack)
- Real users can still suffer (e.g. timeouts, slow responses); cost goes up with no benefit
- In practice: you're scaling on the wrong thing

**Design:** Four bullets. Optional: small icon (e.g. server with £ or $) to suggest cost — don’t clutter.

---

## Slide 5 — What we want instead

**Title:** What we want instead

**Bullets:**
- **Normal traffic** + high load → scale up (add servers) so real users get the capacity they need
- **Attack traffic** → do not scale; block it instead (e.g. return 429) so we don't pay for it
- Real users get capacity back when we restore; we only scale when it's legitimate demand

**Subtext (smaller):** "Attack-aware" means we are aware it's attack and change behaviour accordingly.

**Design:** Three bullets + subtext. Optional: two columns (Normal | Attack). Keep it clear.

---

## Slide 6 — The idea in one sentence

**Title:** The idea in one sentence

**Body (one sentence, centred or near-full width):**  
We use ML to classify traffic as normal or attack; we only scale when it's normal, and we block attack traffic so we don't pay to scale on it.

**Design:** This sentence is the core of your dissertation. Centre it. Make it the only main text (title + this line). No bullets.

---

## Slide 7 — Why microservices?

**Title:** Why microservices?

**Bullets:**
- Modern systems are built as many small services (e.g. one for products, one for payments), each doing one job
- Traffic hits an entry point (a gateway or API gateway) before reaching those services
- We put attack-aware logic at the gateway so the rest of the system doesn't scale on attack
- The gateway can block or allow before requests reach the backend — one place to enforce the decision

**Design:** Four bullets. Optional: tiny sketch “User → Gateway → Services” (no need to be fancy).

---

## Slide 8 — What is a microservice?

**Title:** What is a microservice?

**Bullets:**
- A small, focused part of a bigger system that does one job (single responsibility)
- Services talk to each other over the network (e.g. HTTP); they can be developed and deployed separately
- In this project: **Catalog** = one service (serves product data); **Gateway** = another (entry point + defence)
- Together they form a minimal but real microservices setup

**Design:** Four bullets. Definition + concrete example. Shows you understand the concept.

---

## Slide 9 — How we do it (high level)

**Title:** How we do it (high level)

**Bullets:**
- **1.** Collect or observe traffic metrics at the gateway (e.g. requests per second, error rate)
- **2.** Use ML to classify: normal vs attack (and optionally the attack type, e.g. DDoS, brute force)
- **3.** If attack → gateway blocks (e.g. return 429); if normal → allow and forward to backend
- The detector runs periodically so the system can switch automatically without manual intervention

**Design:** Four bullets. Numbered 1–2–3 plus one on automation. No code. High level only.

---

## Slide 10 — Design (critical for strict marker)

**Title:** Design

**Intro line:** To design and explain the system, I used:

**Bullets:**
- **System Architecture Diagram:** Overall structure (Shop → Gateway → Catalog)
- **Use case / flow:** How traffic is classified and how the gateway switches between allow and block
- **Flowchart:** Steps from "traffic arrives" to "block" or "allow"

**Design:** Like the A-grade examples: put the bullets in a **light green or light teal rounded rectangle** (one content block). Same font. Optional: small “UML” or “diagram” label if you want — don’t overdo it.

---

## Slide 11 — The ML part

**Title:** The ML part (without the maths)

**Bullets:**
- Train a classifier on labelled data (normal vs attack)
- **Input:** e.g. requests per second, error count
- **Output:** "normal" or "attack" (and type: DDoS, brute force, etc.)
- Gateway (or detector) uses this to decide: allow or block

**Design:** Input → model → output. No equations. One idea: “ML decides allow vs block.”

---

## Slide 12 — System architecture

**Title:** System architecture

**Visual:** Draw or insert a simple diagram:
- Three boxes in a row: **Shop / User** → **Gateway (8000)** → **Catalog (8001)**
- Arrows between them (→) for request flow
- Optional: small boxes or labels for "Dashboard (8501)" and "Detector" pointing to the Gateway

**Caption (below diagram):** The Shop sends requests through the Gateway; the Gateway forwards to the Catalog when traffic is allowed. The Dashboard and detector talk to the Gateway for status, metrics, and to set block/normal mode.

**Design:** One clear diagram. Use PowerPoint shapes (rectangles + arrows) or a simple image. Same colours as your theme. Labels on each box. 

---

## Slide 13 — The two microservices

**Title:** The two microservices in this project

**Bullets:**
- **Gateway:** Entry point for all traffic. When mode is normal it forwards requests to the Catalog; when mode is attack it returns 429 (rate limited) and does not call the Catalog — so we don't scale on that traffic
- **Catalog:** Serves product data (e.g. list of products). It does not decide normal vs attack; it just responds when the Gateway calls it
- They communicate over HTTP; the Gateway is the single place where the allow/block decision is enforced

**Subtext:** Together they form a minimal but real microservices system where we demonstrate attack-aware behaviour.

**Design:** Three bullets + subtext. Keep it visual; you can use two boxes (Gateway | Catalog) with a short line each.

---

## Slide 14 — What runs automatically

**Title:** What runs automatically

**Bullets:**
- A detector process runs in the background and periodically (e.g. every few seconds) reads live metrics from the Gateway (requests per second, errors in a time window)
- It runs the ML model on those metrics; if the output is "attack" it tells the Gateway to switch to block mode (and can set the attack type for display)
- When the metrics look normal again, it tells the Gateway to switch back to allow — so the system recovers without manual intervention
- We can also override manually from the dashboard (e.g. for the demo buttons "Simulate attack" / "Restore normal")

**Subtext:** So the system can switch to defence and back without someone clicking buttons.

**Design:** Four bullets. Emphasise “automatic.”

---

## Slide 15 — What I built (overview)

**Title:** What I built — overview

**Bullets:**
- **Backend:** Gateway and Catalog as separate microservices (FastAPI), plus a detector script that runs the ML model and sets the Gateway mode
- **Dashboard:** Control panel (Streamlit) to see status, blocked count, defence history, and to set Normal or Blocking manually
- **Demo website:** A shop that calls the Gateway for products, and a demo page with "Simulate attack" / "Restore normal" so we can show the behaviour in one place
- One command starts everything: `py run_demo.py` — so the whole system is easy to run for the demo

**Design:** Four bullets. Light on implementation (just one tech name per bullet if you want). Shows scope clearly.

---

## Slide 16 — What you'll see in the demo

**Title:** What you'll see in the demo

**Bullets:**
- **1.** Open the demo page — you'll see the pipeline (Shop → Gateway → Catalog) and two big buttons
- **2.** Click "Simulate attack" → the Gateway box goes red, blocked count goes up, the shop shows "We're protecting the system" (and optionally the attack type, e.g. brute force)
- **3.** Click "Restore normal" → the Gateway goes back to green, the shop loads products again
- **4.** (Optional) The dashboard shows the same state — defence history, blocked count — so everything is in sync

**Design:** Numbered 1–4. Sets expectation for the next slide. Slightly more detail on what the user actually sees.

---

## Slide 17 — Live demo

**Title:** Live demo

**Body:**
- **URL:** http://localhost:3000/demo.html
- Run `py run_demo.py` then open the link. Simulate attack → Restore normal.

**Design:** Minimal text. Optional: add a **screenshot** of your demo page (pipeline + two buttons + shop) so the marker “sees” it even before you show it live. Then you say: “I’ll show this live now” and switch to the browser.

---

## Slide 18 — What the demo showed

**Title:** What the demo showed

**Bullets:**
- We classified traffic (normal vs attack) and reacted at the gateway — the system went into defence mode when we simulated attack
- We blocked attack traffic (429) instead of scaling on it — so we didn't add servers for that traffic
- The shop (front-end) and the dashboard both reflect the same Gateway state, so the idea is visible end to end
- When we restored normal, the gateway allowed traffic again and the shop worked — showing the full cycle

**Design:** Four bullets. Reinforces “the idea” for the marker.

---

## Slide 19 — Limitations and future work

**Title:** Limitations and future work

**Bullets:**
- **Limitations:** One gateway, one backend service (Catalog); real systems have many more services and richer metrics. The ML model is trained on a limited dataset (requests per second, errors). We don't actually scale replicas here — we demonstrate the block/allow decision.
- **Future work:** More attack types and more training data; integration with real orchestrators (e.g. Kubernetes) so that "don't scale" actually controls scaling; and possibly more features (e.g. per-IP or per-path rules).

**Design:** Two short bullets. Shows you’re aware it’s a prototype.

---

## Slide 20 — Conclusion & thank you

**Title:** Conclusion

**Bullets:**
- **Problem:** Autoscaling that can't tell real users from attack wastes cost and can hurt users
- **Approach:** Classify traffic with ML; at the gateway, allow when normal, block when attack
- **What I did:** Implemented a small microservices system (Gateway + Catalog), ML classifier, auto-detector, dashboard, and demo — and showed it working

**Closing line:** Thank you — Questions?  
**Line under:** [Your name] · Attack-Aware Autoscaling for Microservices

**Design:** Three bullets then thank you. Same title font as Slide 1. Clean and closed.

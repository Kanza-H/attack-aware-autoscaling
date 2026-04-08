# Exhibition day — stand out in a crowded hall

Your build already has a **dedicated showcase URL**. Use it on the projector:

**http://localhost:3000/demo.html?showcase=1**

## What `?showcase=1` does (built-in)

- **One-line hook** at the top visitors read in 3 seconds (why this isn’t “just autoscale”).
- **Giant impact number** — blocked `/products` forwards (same metric as the small line; readable from metres away).
- **Hides long intro paragraphs** so the **live metrics, pipeline, and shop iframe** dominate the screen.
- **Larger** status strip + metric numbers + taller shop iframe.
- **Presenter keys:** `R` = Run live scenario, `N` = Restore normal (works when focus is not in a form field).

## 30-second script (memorise)

1. “Naive autoscaling pays for attack traffic with more servers and database load.”
2. “This gateway uses **live** stress signals and a classifier to **stop forwarding** abusive `/products` — **HTTP 429** — before the catalog.”
3. “Everything you see is **one real route**: the shop iframe and dashboard hit the **same** API path — not a fake demo endpoint.”
4. Press **Run live scenario** — watch mode flip and the **shop** show the defence screen. **Restore normal** — back to live SKUs.
5. Point at the **big green number**: requests we didn’t waste on the catalog this session.

## Physical booth (5 minutes to prepare)

- **Big text on a card:** project title + `?showcase=1` URL + your name.
- **QR code** to your GitHub or PDF (optional) — for localhost demos, judges must be at your machine anyway; the QR is for *after* if you deploy or host slides.

## If “theirs looks the same as mine”

Judges remember **clarity + live proof + one sentence**. Your differentiation is **enforcement on the real route + operator restore + persisted trail** — say that explicitly.

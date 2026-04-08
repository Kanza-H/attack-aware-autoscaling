# Start here — presentation in 2 days (strict marker)

Your second marker cares about **the idea, design, and a working demo** — not implementation. Everything in this folder is set up so you can give an exemplary presentation.

---

## Do this first (today)

1. **Open**  
   `C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling\presentation\2_DAY_PLAN.md`  
   Read it once so you know what to do today vs tomorrow.

2. **Build your 20 slides in PowerPoint**  
   Open **EXEMPLARY_SLIDES_BUILD.md** (same folder).  
   For each slide (1–20), copy the **Title** and **Bullets** into a new slide in PowerPoint. Follow the **Design** line under each slide (one idea per slide, same theme, light background).  
   On **Slide 12** add a simple diagram: three boxes with arrows — **Shop** → **Gateway** → **Catalog**.  
   On **Slide 1** and **Slide 20** add your name and course/date.

3. **Learn what to say**  
   Open **PRESENTATION_SCRIPT.md**. You don’t need to memorise it. Use it as a guide so you stay on the idea and don’t drift into implementation.  
   Learn the **one sentence** (Slide 6) by heart: *“We use ML to classify traffic as normal or attack; we only scale when it’s normal, and we block attack traffic so we don’t pay to scale on it.”*

4. **Test the demo once**  
   In a terminal:  
   `cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling`  
   `py run_demo.py`  
   Open http://localhost:3000/demo.html  
   Click **Simulate attack** then **Restore normal**. If it works, you’re set for the live demo.

---

## Files in this folder

| File | Use it for |
|------|------------|
| **START_HERE.md** | This file — what to do first |
| **2_DAY_PLAN.md** | Day 1 vs Day 2 schedule and checklist |
| **EXEMPLARY_SLIDES_BUILD.md** | Exact wording + design notes for all 20 slides — build PowerPoint from this |
| **PRESENTATION_SCRIPT.md** | What to say on each slide (idea-focused, no implementation deep-dive) |
| **slides.html** | Browser version of the slides (optional; you can present from PowerPoint) |
| **POWERPOINT_BUILD.txt** | Shorter copy-paste version if you prefer plain text |

---

## Strict-marker checklist

- [ ] All 20 slides use the **same theme** (white/light background, black text).
- [ ] **Slide 10 (Design)** has the design artefacts listed (architecture diagram, flow, flowchart).
- [ ] **Slide 12** has a simple **diagram**: Shop → Gateway → Catalog.
- [ ] **Slide 17** is “Live demo” and you actually run the demo (Simulate attack → Restore normal).
- [ ] You know the **one-sentence idea** (Slide 6).
- [ ] Demo works: `py run_demo.py` → demo page → both buttons work.

Start with **2_DAY_PLAN.md**, then **EXEMPLARY_SLIDES_BUILD.md** to build the slides. You’ve got this.

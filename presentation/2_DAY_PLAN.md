# 2-day plan — presentation in 2 days

Your second marker is strict and cares about **the idea, design, and a working demo** — not implementation detail. This plan gets you to an exemplary presentation without panic.

---

## Day 1 (today): Build slides + one full run-through

### Morning / afternoon (2–3 hours)

1. **Open PowerPoint** (or Google Slides). Pick a **simple, professional theme**: white or very light grey background, black text, one accent colour (e.g. dark green or blue). Use it on every slide.

2. **Build all 20 slides** using **EXEMPLARY_SLIDES_BUILD.md** in this folder:
   - Copy the exact title and bullets for each slide.
   - Follow the **Design notes** (one idea per slide, no walls of text).
   - On **Slide 12 (System architecture)** add a simple diagram: three boxes with arrows: **Shop** → **Gateway** → **Catalog**. You can use PowerPoint’s Insert → Shapes (rectangles + arrows).
   - On **Slide 17 (Live demo)** you can add a screenshot of your demo page later, or leave it as the URL and one line of text.

3. **Slide 1:** Add your name, course, and date.  
   **Slide 20:** Add your name again under “Thank you — Questions?”

4. **Save the file** (e.g. `Attack-Aware-Autoscaling-Presentation.pptx`).

### Evening (30–45 min)

5. **Read PRESENTATION_SCRIPT.md** once. You don’t need to memorise it — it’s there so you know what to say for each slide and stay focused on **the idea**.

6. **One dry run:** Open your slides, go through slides 1–20 and say something for each (even in your head). Note any slide where you get stuck and re-read that part of the script.

7. **Test the demo** once:
   - Open terminal in project folder: `cd C:\Users\kanza\OneDrive\Documents\attack-aware-autoscaling`
   - Run: `py run_demo.py`
   - Open http://localhost:3000/demo.html in the browser
   - Click **Simulate attack** — gateway goes red, shop shows “We’re protecting the system”
   - Click **Restore normal** — shop works again  
   If anything fails, fix it today (e.g. ports, missing model).

**End of Day 1:** You have 20 slides built, one rehearsal done, and a working demo.

---

## Day 2 (tomorrow): Rehearse + buffer

### Morning

8. **Second run-through** with the script. Time yourself (aim for about 3–5 minutes per slide for 20 slides = ~5–10 min total if you keep it concise, or up to 15 min if you speak a bit more). Adjust: if you’re too long, shorten; if too short, add one sentence per slide from the script.

9. **Optional:** Add one screenshot to **Slide 17** (e.g. demo page with “Simulate attack” / “Restore normal” and the pipeline). That way the marker “sees” the demo even before you show it live.

10. **Know your one sentence** (Slide 6) by heart:  
    *“We use ML to classify traffic as normal or attack; we only scale when it’s normal, and we block attack traffic so we don’t pay to scale on it.”*  
    If the marker asks “what’s your project about?”, that’s your answer.

### Before you present

11. **Laptop:** Charged. Close other tabs and apps. Have only: (1) PowerPoint in presentation mode, (2) browser tab with http://localhost:3000/demo.html (or open it when you get to Slide 17).

12. **Start the demo before you present** (or at the start of the session): run `py run_demo.py` and leave it running so when you get to “Live demo” you just switch to the browser and click the buttons.

13. **If the marker asks about implementation:** Keep it short. Say something like: “The gateway and catalog are separate services; the detector runs the ML model and tells the gateway to block or allow. I’m happy to show the demo / walk through the architecture if you’d like.” Then show the demo or point to the diagram.

---

## Checklist (strict marker)

- [ ] All 20 slides use the **same theme** (white/light background, black text).
- [ ] **No slide** has more than about 5 bullets or a wall of text.
- [ ] **Slide 10 (Design)** clearly lists design artefacts (architecture diagram, flow, etc.).
- [ ] **Slide 12** has a simple **architecture diagram** (Shop → Gateway → Catalog).
- [ ] **Slide 17** says “Live demo” and you actually run the demo (Simulate attack → Restore normal).
- [ ] You know the **one-sentence idea** (Slide 6) by heart.
- [ ] Demo works: `py run_demo.py` → demo page → both buttons work.

You’ve got this. Day 1 = build + one run + demo test. Day 2 = rehearse + polish + present.

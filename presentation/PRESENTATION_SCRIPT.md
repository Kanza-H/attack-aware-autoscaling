# What to say — slide by slide (strict marker)

Use this so you stay focused on **the idea** and don’t drift into implementation. You don’t need to memorise it word for word; use it as a guide. Keep each slide to **2–4 sentences** so you don’t run long.

---

## Slide 1 — Title

*[Just show the slide. If you need to speak:]*  
“My project is Attack-Aware Autoscaling for Microservices — I’ll explain the problem, the idea, and show a short demo.”

---

## Slide 2 — What I'm going to cover

“I’ll cover four things: the problem with normal autoscaling, our solution using ML to classify traffic, how it fits into a microservices setup, and a live demo at the end.”

---

## Slide 3 — Why normal autoscaling is a problem

“When traffic spikes, systems usually scale up — they add more servers. The problem is they don’t distinguish between real users and attackers. So they treat everyone the same.”

---

## Slide 4 — What goes wrong during an attack

“During something like a DDoS or brute force, the traffic looks like high load. So the autoscaler adds more servers — and you end up paying for attack traffic. Real users can still suffer, and your cost goes up with no real benefit.”

---

## Slide 5 — What we want instead

“What we want is different behaviour for normal vs attack. Normal traffic plus high load — we scale up. Attack traffic — we do not scale; we block it instead. So ‘attack-aware’ means we’re aware it’s attack and we change our behaviour.”

---

## Slide 6 — The idea in one sentence

*[Read the sentence, or say:]*  
“We use ML to classify traffic as normal or attack. We only scale when it’s normal, and we block attack traffic so we don’t pay to scale on it.”  
*[If the marker asks “what’s your project in one sentence?” — this is it.]*

---

## Slide 7 — Why microservices?

“Modern systems are built as many small services — for example one for products, one for payments. Traffic hits an entry point, a gateway, before reaching those services. Our work sits at that gateway: we put the attack-aware logic there so the rest of the system doesn’t scale on attack.”

---

## Slide 8 — What is a microservice?

“A microservice is a small, focused part of a bigger system that does one job. They talk to each other over the network — HTTP. In this project, the Catalog is one service — it serves product data. The Gateway is another — it’s the entry point and it does the defence.”

---

## Slide 9 — How we do it (high level)

“At a high level we do three things. One: we collect or observe traffic metrics — requests per second, errors. Two: we use ML to classify that as normal or attack, and optionally the attack type. Three: if it’s attack we tell the gateway to block — for example return 429 — and if it’s normal we allow. No implementation detail needed here.”

---

## Slide 10 — Design

“To design and explain the system I used a system architecture diagram for the overall structure — Shop, Gateway, Catalog. I used a use case or flow to show how traffic is classified and how the gateway switches between allow and block. And a flowchart for the steps from traffic arriving to block or allow.”

---

## Slide 11 — The ML part

“We train a classifier on labelled data — normal vs attack traffic. The input is things like requests per second and error count. The output is ‘normal’ or ‘attack,’ and we can label the type — DDoS, brute force, and so on. The gateway or a detector process uses that to decide: allow or block. I’m not going into the maths — the idea is that the decision is data-driven.”

---

## Slide 12 — System architecture

*[Point at the diagram.]*  
“Traffic from the shop or user hits the Gateway on port 8000. The Gateway talks to the Catalog on 8001 for product data. The dashboard and the detector also talk to the Gateway — for status, metrics, and to set block or normal mode.”

---

## Slide 13 — The two microservices

“In this project there are two microservices. The Gateway is the entry point — when traffic is normal it forwards to the Catalog; when we’re in attack mode it returns 429 and blocks. The Catalog just serves product data; it doesn’t decide normal vs attack. Together they’re a minimal microservices system where we demonstrate attack-aware behaviour.”

---

## Slide 14 — What runs automatically

“A detector runs in the background. It periodically reads live metrics from the Gateway, runs the ML model, and if it sees attack-like traffic it tells the Gateway to block. When traffic looks normal again it tells the Gateway to allow. So the system can switch to defence and back without anyone clicking buttons — though we can also control it manually from the dashboard.”

---

## Slide 15 — What I built (overview)

“I built a backend with the Gateway and Catalog microservices, a detector script, and the ML model. A dashboard to see status, blocked count, defence history, and to set Normal or Blocking. And a demo website with a shop and a demo page with two buttons — Simulate attack and Restore normal. One command starts everything.”

---

## Slide 16 — What you'll see in the demo

“In the demo you’ll see the demo page with the pipeline — Shop, Gateway, Catalog. I’ll click Simulate attack — the gateway will go red and the shop will show ‘We’re protecting the system.’ Then I’ll click Restore normal and the shop will show products again. I can also show the dashboard with the same state and defence history if there’s time.”

---

## Slide 17 — Live demo

*[Switch to the browser. Have http://localhost:3000/demo.html open and run_demo.py already running.]*  
“This is the live demo. I’ll click Simulate attack now.” *[Click.]* “You can see the gateway has gone red and the shop is showing that we’re protecting the system. And I’ll click Restore normal.” *[Click.]* “And the shop is back. So we’re blocking attack traffic instead of scaling on it.”

---

## Slide 18 — What the demo showed

“The demo showed three things. We classified traffic as normal or attack and reacted at the gateway. We blocked attack traffic with 429 instead of scaling on it. And the shop and the dashboard both reflect the same Gateway state — so the idea is visible end to end.”

---

## Slide 19 — Limitations and future work

“The limitations are that we have one gateway and one backend service — real systems would have more services and more metrics. Future work could include more attack types, more data, and integration with real orchestrators like Kubernetes.”

---

## Slide 20 — Conclusion & thank you

“To conclude: the problem is that autoscaling that can’t tell real users from attack wastes cost and can hurt users. Our approach is to classify traffic with ML and at the gateway allow when it’s normal and block when it’s attack. I implemented a small microservices system with the Gateway and Catalog, the ML classifier, an auto-detector, a dashboard, and a demo — and showed it working. Thank you — I’m happy to take questions.”

---

## If the marker asks…

- **“How does the ML work?”**  
  “We train a classifier on labelled data — requests per second and errors — and it outputs normal or attack. The detector runs it periodically and tells the gateway to block or allow. I can go into more detail if you’d like.”

- **“Why microservices?”**  
  “So we can show the idea at the gateway in front of a real service — the Catalog. In a bigger system you’d have more services behind the same gateway.”

- **“Show me the demo again.”**  
  Switch to the browser and run through Simulate attack and Restore normal again.

- **“What did you implement?”**  
  “The Gateway and Catalog as separate services, the ML model and detector script, the dashboard, and the demo website. The demo is one command — run_demo.py — and then the demo page in the browser.”

Keep answers short and point back to the idea: we classify traffic, we block instead of scaling on attack, and we showed it working.

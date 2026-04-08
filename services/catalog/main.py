"""
Catalog microservice – product data only.
Gateway (API) calls this when serving legitimate traffic.
Richer SKUs (ratings, fulfilment copy, image_url) — forwarded as JSON by the gateway unchanged.
"""
from fastapi import FastAPI

app = FastAPI(
    title="Catalog Service",
    description="Product data microservice",
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "catalog"}


def _products():
    """Illustrative SKUs for the Meridian storefront (gateway → catalog path)."""
    # image_url: stable Unsplash crops (HTTPS); shop falls back to gradient if offline.
    return [
        {
            "id": 1,
            "name": "API Gateway tier — Pro",
            "price": 9.99,
            "list_price": 14.99,
            "category": "Edge & ingress",
            "description": "Route, authenticate, and rate-limit traffic before it hits your services. In this FYP stack, your browser never talks to the catalog directly — the gateway is the only ingress.",
            "rating": 4.6,
            "review_count": 1284,
            "fulfillment": "Arrives digitally · Licence key after checkout (prototype)",
            "badge": "Meridian's Choice",
            "highlights": [
                "Single entry point for microservice traffic",
                "Pairs with defence mode (429) demos",
                "Same path as the live shop iframe",
            ],
            "image_url": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 2,
            "name": "Catalog read replica add-on",
            "price": 14.99,
            "list_price": 19.99,
            "category": "Data & storage",
            "description": "Read scaling for product lookups. Demonstrates why naive autoscaling still burns capacity if abusive traffic reaches the database — edge defence matters.",
            "rating": 4.4,
            "review_count": 892,
            "fulfillment": "Provisioned next sync window (illustrative)",
            "badge": "Frequently bought together",
            "highlights": [
                "Served only via gateway in this prototype",
                "SQLite / export story in dissertation",
                "Contrasts with “scale replicas for DDoS” anti-pattern",
            ],
            "image_url": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 3,
            "name": "Observability & metrics pack",
            "price": 19.99,
            "list_price": 24.99,
            "category": "Operations",
            "description": "Sliding-window RPS, error counts, and persisted snapshots — the same signals your ML detector and dashboard consume.",
            "rating": 4.7,
            "review_count": 2103,
            "fulfillment": "Instant · Ties to gateway_events.db (demo)",
            "badge": "Best seller in Ops",
            "highlights": [
                "Feeds Streamlit + policy chips",
                "Explains “instrumented” vs canned demo",
                "Export JSON from dashboard",
            ],
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 4,
            "name": "ML detector training bundle",
            "price": 29.00,
            "list_price": 34.99,
            "category": "Security & ML",
            "description": "sklearn classifier boundary: normal vs attack-shaped load. Includes scripts to collect metrics and retrain from labelled windows.",
            "rating": 4.5,
            "review_count": 456,
            "fulfillment": "Download · scripts/ml in repo",
            "badge": None,
            "highlights": [
                "Same model as auto_detector.py",
                "Dashboard “Run model” sandbox",
                "Discuss precision/recall in write-up",
            ],
            "image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 5,
            "name": "Sticky defence policy module",
            "price": 12.50,
            "list_price": None,
            "category": "Security & ML",
            "description": "Operator-only restore path so automated clients cannot clear attack mode — matches enterprise break-glass patterns.",
            "rating": 4.8,
            "review_count": 367,
            "fulfillment": "Configured on gateway (prototype)",
            "badge": "Small business favourite",
            "highlights": [
                "X-Manual-Restore semantics",
                "SQLite audit trail of mode changes",
                "Stops silent flapping in demos",
            ],
            "image_url": "https://images.unsplash.com/photo-1563013545-824ae1b704d3?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 6,
            "name": "Streamlit control plane skin",
            "price": 7.99,
            "list_price": 11.99,
            "category": "Operations",
            "description": "Operator-facing panel: gateway client, latency probes, JSON export — looks like a real NOC slice for your presentation.",
            "rating": 4.3,
            "review_count": 156,
            "fulfillment": "Ships with dashboard/ (this repo)",
            "badge": None,
            "highlights": [
                "Typed HTTP client layer",
                "Explains demo vs dashboard sync",
                "Presentation mode for viva",
            ],
            "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 7,
            "name": "Meridian storefront theme",
            "price": 0.00,
            "list_price": 4.99,
            "category": "Edge & ingress",
            "description": "Dark retail UI you are browsing now — loads catalog only through GET /products on the gateway (no bundled mock JSON).",
            "rating": 4.2,
            "review_count": 89,
            "fulfillment": "Included · website/ in repo",
            "badge": "Free add-on",
            "highlights": [
                "429 defence screen when gateway blocks",
                "Cart stored in browser (prototype)",
                "Comparable layout to major retailers (simplified)",
            ],
            "image_url": "https://images.unsplash.com/photo-1441986300917-64674a600a31?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 8,
            "name": "Policy comparison lab (naive vs edge)",
            "price": 22.00,
            "list_price": 27.50,
            "category": "Security & ML",
            "description": "Narrative + chips that contrast naive autoscaling with attack-aware blocking — ties dissertation story to live metrics.",
            "rating": 4.6,
            "review_count": 512,
            "fulfillment": "Runs in demo.html + /admin/stats",
            "badge": "Meridian's Choice",
            "highlights": [
                "Verdict copy from gateway policy object",
                "Explain “why not just scale” to examiners",
                "Uses same RPS window as classifier",
            ],
            "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 9,
            "name": "Health-check & synthetic probe kit",
            "price": 5.49,
            "list_price": None,
            "category": "Operations",
            "description": "curl-friendly /health on gateway and catalog — for diagrams and failure-mode discussion.",
            "rating": 4.1,
            "review_count": 74,
            "fulfillment": "Immediate",
            "badge": None,
            "highlights": [
                "run_demo.py brings full stack up",
                "Port matrix in HOW_TO_RUN",
                "Supports “single pane of glass” story",
            ],
            "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=720&h=540&fit=crop&auto=format&q=82",
        },
        {
            "id": 10,
            "name": "Dissertation export pack (JSON)",
            "price": 3.00,
            "list_price": 5.00,
            "category": "Data & storage",
            "description": "Session snapshot from the dashboard — gateway URL, defence history, counters — for appendices and reproducibility.",
            "rating": 4.9,
            "review_count": 42,
            "fulfillment": "Download button in Streamlit",
            "badge": "Students & researchers",
            "highlights": [
                "One-click evidence bundle",
                "Pairs with SQLite file path",
                "Shows engineering hygiene",
            ],
            "image_url": "https://images.unsplash.com/photo-1507925921958-8a62f3d1a50d?w=720&h=540&fit=crop&auto=format&q=82",
        },
    ]


@app.get("/products")
def products():
    """Returns product list. Called by the gateway."""
    return {"products": _products()}

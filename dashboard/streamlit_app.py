"""
Attack-Aware Autoscaling — Control panel and live demo.
Run from project root: streamlit run dashboard/streamlit_app.py
"""
import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st
import pandas as pd

from dashboard.gateway_client import GatewayClient

st.set_page_config(
    page_title="Meridian · Gateway control",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Activity log so the page feels alive
if "activity_log" not in st.session_state:
    st.session_state.activity_log = []


def log(msg):
    st.session_state.activity_log = [f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"] + st.session_state.activity_log[:7]


def _format_post_failure(r):
    """Turn gateway error bodies (e.g. FastAPI JSON) into a short string."""
    if r.ok:
        return None
    raw = (r.error or "").strip()
    if not raw:
        return f"HTTP {r.status_code}" if r.status_code else "Connection failed (is the gateway running on :8000?)"
    try:
        j = json.loads(raw)
        if isinstance(j, dict) and "detail" in j:
            d = j["detail"]
            return d if isinstance(d, str) else str(d)
    except (json.JSONDecodeError, TypeError):
        pass
    return raw[:500]


def _feedback_after_post(r):
    """User-visible result; survives the next st.rerun() via session_state."""
    if r.ok and r.data:
        dm = (r.data.get("defence_mode") or "").lower()
        if dm == "normal":
            return (
                "ok",
                "**Allow traffic** is now active. The gateway **forwards** `GET /products` to the catalog. "
                "Watch the **green** bar at the top of this page.",
            )
        if dm == "attack":
            return (
                "ok",
                "**Blocking** is now active. The gateway answers `GET /products` with **HTTP 429** (shop cannot load products). "
                "Watch the **red** bar at the top.",
            )
        return ("ok", f"Gateway acknowledged mode: **{dm}**.")
    return ("err", f"**Could not change mode.** {_format_post_failure(r)}")


# Shared client: keep-alive connections, measured latency — same gateway the demo page uses.
_gateway = GatewayClient()


def load_backend_status():
    """Live gateway + catalog snapshot (not cached — must match demo)."""
    out, latency_ms = _gateway.fetch_backend_status()
    return out, latency_ms


@st.cache_data(ttl=1)
def fetch_stats():
    """Aggregated counters / policy snapshot (short TTL)."""
    r = _gateway.admin_stats()
    if r.ok and r.data:
        return r.data
    return {"requests_total": 0, "blocked_total": 0, "defence_mode": "normal"}


@st.cache_data(ttl=1)
def fetch_defence_history():
    r = _gateway.admin_history()
    if r.ok and r.data:
        return (r.data or {}).get("events") or []
    return []


@st.cache_data(ttl=2)
def fetch_metrics_history(limit=120):
    r = _gateway.admin_metrics_history(limit=limit)
    if r.ok and r.data:
        return (r.data or {}).get("items") or []
    return []


@st.cache_data(ttl=1)
def fetch_backend_overview():
    r = _gateway.admin_overview()
    if r.ok and r.data:
        return r.data
    return {}


@st.cache_data(ttl=1)
def fetch_db_diagnostics():
    r = _gateway.admin_db()
    if r.ok and r.data:
        return r.data
    return {}


def _fmt_uptime(sec: int) -> str:
    """Human-readable uptime instead of a raw second count."""
    try:
        s = int(sec)
    except (TypeError, ValueError):
        return "—"
    if s < 60:
        return f"{s}s"
    m, s = divmod(s, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    if h < 48:
        return f"{h}h {m}m"
    d, h = divmod(h, 24)
    return f"{d}d {h}h"


# ----- CSS: aligned with Meridian shop / demo (dark, blue accent, Inter) -----
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet">
<style>
    html, body, [data-testid="stApp"] {
        font-family: 'Inter', system-ui, sans-serif !important;
    }
    .stApp {
        background: linear-gradient(180deg, #0b0d12 0%, #11141c 50%, #0b0d12 100%) !important;
        color: #e4e4e7 !important;
    }
    /* Safe top padding — do NOT use negative margins (they slide content under Streamlit's fixed header). */
    section.main .block-container,
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1200px !important;
    }
    section[data-testid="stMain"] {
        overflow-x: hidden;
    }
    header[data-testid="stHeader"] {
        background: rgba(11, 13, 18, 0.97) !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        backdrop-filter: blur(10px);
        z-index: 100 !important;
    }
    /* Deploy / menu row: keep visible, match Meridian bar */
    [data-testid="stDecoration"] { background: transparent !important; }

    .meridian-status-wrap {
        margin: 0 0 1rem 0;
        width: 100%;
        position: relative;
        z-index: 1;
    }
    /* Status strip — full rounded card (no edge bleed into header) */
    .status-strip {
        margin: 0 !important;
        padding: 0.75rem 1.25rem;
        font-size: 0.84rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        display: flex;
        align-items: center;
        gap: 0.55rem;
        border-radius: 12px;
        box-sizing: border-box;
        width: 100%;
    }
    .status-strip.normal {
        background: linear-gradient(90deg, #064e3b 0%, #059669 55%, #10b981 100%);
        color: #ecfdf5;
        box-shadow: 0 4px 24px rgba(16, 185, 129, 0.15);
    }
    .status-strip.blocking {
        background: linear-gradient(90deg, #7f1d1d 0%, #b91c1c 50%, #dc2626 100%);
        color: #fef2f2;
        box-shadow: 0 4px 28px rgba(220, 38, 38, 0.2);
    }
    .status-strip.unknown {
        background: linear-gradient(90deg, #78350f 0%, #b45309 100%);
        color: #fffbeb;
    }
    .status-strip .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: currentColor;
        box-shadow: 0 0 12px currentColor;
        animation: meridian-pulse 2s ease-in-out infinite;
    }
    @keyframes meridian-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.55; } }
    
    .hero {
        background: linear-gradient(155deg, #141a24 0%, #1a2230 45%, #121820 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.75rem 2rem;
        margin-bottom: 1.35rem;
        box-shadow: 0 12px 40px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
    }
    .hero h1 {
        font-size: clamp(1.5rem, 3vw, 1.85rem);
        font-weight: 700;
        color: #f4f4f5;
        margin: 0 0 0.5rem 0;
        letter-spacing: -0.03em;
    }
    .hero .tagline { font-size: 0.98rem; color: #a1a1aa; margin: 0; line-height: 1.55; max-width: 52rem; }
    .hero .badge {
        display: inline-block;
        margin-top: 0.9rem;
        padding: 0.35rem 0.8rem;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        background: rgba(59, 130, 246, 0.12);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.25);
    }

    .demo-callout {
        background: linear-gradient(165deg, #161b26 0%, #121820 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1.35rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.25);
    }
    .demo-callout h3 {
        font-size: 1.05rem;
        font-weight: 600;
        color: #f4f4f5;
        margin: 0 0 0.45rem 0;
        letter-spacing: -0.02em;
    }
    .demo-callout p { font-size: 0.88rem; color: #a1a1aa; margin: 0 0 0.85rem 0; line-height: 1.55; }
    .demo-callout .pipeline-mini {
        display: flex; align-items: center; justify-content: center; gap: 0.45rem;
        flex-wrap: wrap; margin: 0.85rem 0 1rem;
    }
    .demo-callout .pipe-node {
        padding: 0.45rem 0.85rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .demo-callout .pipe-node.shop { background: rgba(59,130,246,0.12); color: #93c5fd; }
    .demo-callout .pipe-node.gateway { background: rgba(34,197,94,0.12); color: #86efac; }
    .demo-callout .pipe-node.gateway.blocking { background: rgba(239,68,68,0.15); color: #fca5a5; border-color: rgba(239,68,68,0.25); }
    .demo-callout .pipe-node.catalog { background: rgba(59,130,246,0.1); color: #7dd3fc; }
    .demo-callout .pipe-arrow { color: #71717a; font-size: 1rem; }
    .demo-callout a { color: #60a5fa !important; text-decoration: none !important; font-weight: 500; }
    .demo-callout a:hover { text-decoration: underline !important; }
    
    .section {
        font-size: 0.68rem;
        font-weight: 700;
        color: #71717a;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin: 1.85rem 0 0.65rem 0;
        padding-left: 0.65rem;
        border-left: 3px solid #3b82f6;
    }
    
    [data-testid="stMetric"] {
        background: #161b26 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    [data-testid="stMetricValue"] {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        color: #fafafa !important;
        font-variant-numeric: tabular-nums;
    }
    [data-testid="stMetricLabel"] {
        color: #a1a1aa !important;
        font-size: 0.76rem !important;
        font-weight: 500 !important;
    }
    
    .decision {
        border-radius: 12px;
        padding: 1.1rem 1.35rem;
        margin: 0.55rem 0;
        font-size: 0.95rem;
        font-weight: 500;
        border-left: 4px solid;
        line-height: 1.5;
    }
    .decision-normal { background: rgba(34, 197, 94, 0.08); border-left-color: #22c55e; color: #bbf7d0; }
    .decision-attack { background: rgba(239, 68, 68, 0.1); border-left-color: #ef4444; color: #fecaca; }
    .decision strong { font-weight: 600; }
    
    .live-blocking {
        background: linear-gradient(145deg, rgba(127, 29, 29, 0.35) 0%, rgba(24, 24, 27, 0.95) 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
        border-radius: 14px;
        padding: 1.5rem 1.75rem;
        margin: 1rem 0;
        box-shadow: 0 0 40px rgba(239, 68, 68, 0.08);
    }
    .live-blocking .big-number {
        font-family: 'IBM Plex Mono', ui-monospace, monospace;
        font-size: clamp(2.5rem, 6vw, 3.25rem);
        font-weight: 700;
        color: #fca5a5;
        letter-spacing: -0.03em;
        line-height: 1;
    }
    .live-blocking .label { font-size: 0.88rem; color: #d4d4d8; margin-top: 0.5rem; line-height: 1.45; }
    
    .activity-box {
        background: #0c0e14;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        font-family: 'IBM Plex Mono', ui-monospace, monospace;
        font-size: 0.78rem;
        color: #a1a1aa;
        max-height: 170px;
        overflow-y: auto;
    }
    .activity-box div { padding: 0.2rem 0; border-bottom: 1px solid rgba(255,255,255,0.04); }
    .activity-box div:last-child { border-bottom: none; }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        border-radius: 10px !important;
        border-color: rgba(255,255,255,0.12) !important;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c0e14 0%, #11141c 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] .stMarkdown { color: #a1a1aa !important; }
    [data-testid="stSidebar"] h3 { color: #e4e4e7 !important; font-size: 0.95rem !important; }
    
    [data-testid="stExpander"] {
        background: #161b26 !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 12px !important;
    }

    /* Caption + info under status — never clipped */
    [data-testid="stCaptionContainer"] {
        margin-top: 0.35rem !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stCaptionContainer"] p {
        color: #a1a1aa !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stAlert"],
    div.stAlert {
        margin-top: 0.35rem !important;
        margin-bottom: 0.85rem !important;
        border-radius: 12px !important;
        padding: 0.85rem 1rem !important;
        border: 1px solid rgba(59, 130, 246, 0.28) !important;
        background: linear-gradient(165deg, rgba(30, 58, 138, 0.45) 0%, rgba(23, 37, 84, 0.35) 100%) !important;
    }
    div[data-testid="stAlert"] p,
    div.stAlert p {
        color: #e0e7ff !important;
        font-size: 0.9rem !important;
        line-height: 1.55 !important;
    }
    div[data-testid="stAlert"] code,
    div.stAlert code {
        background: rgba(0,0,0,0.25) !important;
        padding: 0.1em 0.35em !important;
        border-radius: 4px !important;
        font-size: 0.88em !important;
    }
</style>
""", unsafe_allow_html=True)

# ----- Fetch backend state (no cache; same gateway as demo) -----
status, status_latency_ms = load_backend_status()
api_status = status["api_status"]
catalog_status = status["catalog_status"]
replicas = status["replicas"]
defence_mode = status["defence_mode"] or "normal"
last_attack_type = status.get("last_attack_type") or ""
demo_traffic_origin = status.get("demo_traffic_origin") or ""
demo_origin_disclaimer = status.get("demo_origin_disclaimer") or ""
gateway_reachable = status.get("gateway_reachable", True)

csv_path = PROJECT_ROOT / "data" / "metrics.csv"
n_rows = 0
if csv_path.exists():
    try:
        n_rows = len(pd.read_csv(csv_path))
    except Exception:
        pass

# ----- Status strip (top) – matches gateway at 127.0.0.1:8000 -----
if not gateway_reachable:
    strip_class = "unknown"
    strip_text = "Could not reach gateway — click Refresh status or check that the gateway is running on port 8000"
else:
    strip_class = "blocking" if defence_mode == "attack" else "normal"
    strip_text = "BLOCKING — Attack traffic blocked (429)" if defence_mode == "attack" else "NORMAL — Traffic allowed; scale when needed"
    if last_attack_type:
        strip_text += f" · {last_attack_type}"
    if demo_traffic_origin:
        strip_text += f" · {demo_traffic_origin}"
st.markdown(
    f'<div class="meridian-status-wrap"><div class="status-strip {strip_class}">'
    f'<span class="dot" aria-hidden="true"></span><span>{strip_text}</span></div></div>',
    unsafe_allow_html=True,
)

# Survives st.rerun() so operators see confirmation (st.success alone is wiped on rerun)
fb = st.session_state.pop("dashboard_feedback", None)
if fb:
    kind, text = fb
    if kind == "ok":
        st.success(text)
    else:
        st.error(text)

if not gateway_reachable:
    st.warning("Dashboard could not reach the gateway at localhost:8000. Ensure the gateway is running (run_demo.py) and click **Refresh status**.")
    if st.button("Refresh status", key="sync_top_offline", type="primary", use_container_width=True):
        try:
            fetch_stats.clear()
            fetch_defence_history.clear()
            fetch_metrics_history.clear()
            fetch_backend_overview.clear()
            fetch_db_diagnostics.clear()
        except Exception:
            pass
        st.rerun()
else:
    top_a, top_b = st.columns([4, 1])
    with top_a:
        st.caption(
            f"Gateway **{_gateway.gateway_url}** · last probe **{status_latency_ms:.0f} ms**."
        )
    with top_b:
        refresh_top = st.button(
            "Refresh status",
            key="sync_top",
            type="primary",
            use_container_width=True,
            help="Reload gateway state and clear short-lived caches (match the live demo).",
        )
    if refresh_top:
        try:
            fetch_stats.clear()
            fetch_defence_history.clear()
            fetch_metrics_history.clear()
            fetch_backend_overview.clear()
            fetch_db_diagnostics.clear()
        except Exception:
            pass
        st.rerun()
    st.info(
        "**Same live gateway as the browser demo** (`demo.html`). The demo page polls automatically; use **Refresh status** if this panel looks behind."
    )

# ----- Hero -----
st.markdown("""
<div class="hero">
    <h1>Meridian · Gateway control</h1>
    <p class="tagline">Attack-aware autoscaling: classify stress, block abusive <code style="font-size:0.92em;color:#93c5fd;">/products</code> traffic at the edge, and keep the catalog off the critical path when defence is justified.</p>
    <span class="badge">Live API · ML policy · SQLite audit</span>
</div>
""", unsafe_allow_html=True)

# ----- Live demo -----
d = fetch_stats()
blocked = d.get("blocked_total", 0)
gateway_class = "blocking" if defence_mode == "attack" else ""
gateway_label = "Blocking" if defence_mode == "attack" else "Normal"
st.markdown(f"""
<div class="demo-callout">
    <h3>Live browser demo</h3>
    <p>Full-screen pipeline, metrics, and Meridian shop iframe — same gateway APIs as this panel. Use <strong>Run live scenario</strong> / <strong>Restore normal ops</strong> there, or the buttons below.</p>
    <div class="pipeline-mini">
        <span class="pipe-node shop">Shop</span>
        <span class="pipe-arrow">→</span>
        <span class="pipe-node gateway {gateway_class}">Gateway: {gateway_label}</span>
        <span class="pipe-arrow">→</span>
        <span class="pipe-node catalog">Catalog</span>
    </div>
    <p style="margin-bottom:0;">Blocked this session: <strong style="font-family:IBM Plex Mono,monospace;">{blocked}</strong> · Pattern: <strong>{last_attack_type or "—"}</strong></p>
    <p style="margin-top:0.65rem;margin-bottom:0;font-size:0.86rem;">
        <a href="http://localhost:3000/demo.html" target="_blank" rel="noopener">Open demo</a>
        · <a href="http://localhost:3000/demo.html?showcase=1" target="_blank" rel="noopener">Showcase mode</a> (fair / projector)
        · <a href="http://localhost:3000/index.html" target="_blank" rel="noopener">Shop only</a>
    </p>
    <p style="margin-top:0.4rem;margin-bottom:0;font-size:0.82rem;color:#a1a1aa;">Context: <strong>{demo_traffic_origin or "—"}</strong></p>
    <p style="margin-top:0.2rem;margin-bottom:0;font-size:0.75rem;color:#71717a;">{demo_origin_disclaimer or ""}</p>
</div>
""", unsafe_allow_html=True)

# ----- Sidebar -----
with st.sidebar:
    presentation_mode = st.checkbox(
        "Presentation mode (clean view)",
        value=False,
        help="Hides classifier / export / charts — use for a short live demo. Turn off to see the full panel.",
    )
    st.caption(
        "Updates when you interact or click **Refresh status** — no background timer (stays fast and stable)."
    )
    st.markdown("### How it works")
    st.markdown("""
    **Normal traffic** → Scale when needed.

    **Attack detected** → Do not scale; block at gateway (429).
    """)
    st.markdown("---")
    st.markdown("**Components**")
    st.markdown("- Gateway (FastAPI)")
    st.markdown("- Catalog service")
    st.markdown("- ML traffic classifier")
    st.markdown("- This control panel")
    st.caption(
        f"API client → `{_gateway.gateway_url}` · override with env `GATEWAY_URL` "
        "(same pattern as production config maps)."
    )

# ----- Operational status -----
# Note: st.metric(label, value, delta) — the 3rd arg is a *change* (↑/↓), not a subtitle.
# We only use two args here so ports and statuses are not mistaken for trends.
st.markdown('<p class="section">1 · Service health</p>', unsafe_allow_html=True)
st.caption(
    "Green strip at top = live gateway mode. "
    "Tiles below are **current state** (no fake “up” arrows — those only appear when we pass a real delta)."
)
h1, h2, h3, h4 = st.columns(4)
with h1:
    st.metric(
        "API gateway",
        api_status,
        help="FastAPI process on port 8000 — same service as the demo page.",
    )
with h2:
    st.metric(
        "Catalog service",
        catalog_status,
        help="Product API behind the gateway (port 8001).",
    )
with h3:
    st.metric(
        "Defence mode",
        "Blocking" if defence_mode == "attack" else "Normal",
        help="Attack = gateway returns 429 on /products until operator restore.",
    )
with h4:
    st.metric(
        "Classifier",
        "Ready",
        help="sklearn model used by scripts and policy view.",
    )
h5, h6, _ = st.columns([1, 1, 2])
with h5:
    st.metric("Catalog replicas (demo)", str(replicas), help="Prototype keeps 1 instance; policy text can recommend scale-out.")
with h6:
    st.metric("Rows in metrics.csv", str(n_rows), help="Training / export data for the detector (see data/metrics.csv).")

# ----- Backend operations center -----
st.markdown('<p class="section">2 · Gateway counters & SQLite</p>', unsafe_allow_html=True)
overview = fetch_backend_overview()
db_diag = fetch_db_diagnostics()
if overview and db_diag:
    uptime_sec = int(overview.get("uptime_sec") or 0)
    req_total_ov = (overview.get("counters") or {}).get("requests_total", 0)
    st.caption(
        "Persisted in **gateway_events.db** on disk. "
        "Uptime is gateway process lifetime since last start."
    )
    ops1, ops2, ops3, ops4 = st.columns(4)
    with ops1:
        st.metric(
            "Gateway uptime",
            _fmt_uptime(uptime_sec),
            help=f"Exact: {uptime_sec:,} seconds since this gateway process started.",
        )
    with ops2:
        st.metric(
            "Requests (lifetime)",
            f"{int(req_total_ov):,}",
            help="Total HTTP requests seen by this gateway process.",
        )
    with ops3:
        st.metric(
            "Defence events in DB",
            f"{int(db_diag.get('defence_history_rows') or 0):,}",
            help="Rows in defence history table (mode transitions).",
        )
    with ops4:
        st.metric(
            "Metric snapshots in DB",
            f"{int(db_diag.get('metrics_snapshots_rows') or 0):,}",
            help="Rolling snapshots written for dashboard / export (capped in gateway).",
        )

    with st.expander("Advanced: raw JSON from the gateway REST API", expanded=False):
        t_ov, t_db = st.tabs(["GET /admin/overview", "GET /admin/db"])
        with t_ov:
            st.json(overview)
        with t_db:
            st.json(db_diag)
        st.caption("Other endpoints you can call directly: `/admin/history`, `/admin/metrics-history`.")
else:
    st.caption("Backend diagnostics unavailable. Start the gateway and click **Refresh status**.")

# ----- Presentation mode -----
if False and presentation_mode:
    st.markdown('<p class="section">Operator — gateway defence mode</p>', unsafe_allow_html=True)
    st.info(
        "**What you are looking at:** one running **API gateway** (port 8000) between the shop and the catalog.\n\n"
        "- **Allow traffic** — gateway forwards product requests → catalog loads in the shop. **Green** status bar above.\n"
        "- **Block product API** — gateway stops forwarding and returns **HTTP 429** on `/products` → shop shows the shield screen. **Red** bar above.\n\n"
        "**Proof it worked:** the wide **green or red bar at the very top** of this page must switch. "
        "That is live state from the same gateway as **http://localhost:3000/demo.html**."
    )
    mode_label = "BLOCKING (429 on /products)" if defence_mode == "attack" else "NORMAL (forwarding to catalog)"
    st.markdown(f"### Current mode: **{mode_label}**")
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        if st.button("Allow traffic", key="event_set_normal", use_container_width=True, help="POST /admin/defence-mode normal — clears sticky defence"):
            r = _gateway.post_defence_mode("normal", manual_restore=True)
            st.session_state.dashboard_feedback = _feedback_after_post(r)
            st.rerun()
    with c2:
        if st.button("Block /products (defence)", key="event_set_blocking", use_container_width=True, type="primary", help="POST /admin/defence-mode attack"):
            r = _gateway.post_defence_mode("attack")
            st.session_state.dashboard_feedback = _feedback_after_post(r)
            st.rerun()
    with c3:
        st.caption(
            "Tip: if the bar does not move, the gateway is not running — start **`py run_demo.py`** then click **Refresh status**."
        )

    st.markdown('<p class="section">Recent defence events</p>', unsafe_allow_html=True)
    p_history = fetch_defence_history()
    if p_history:
        p_rows = []
        for e in reversed(p_history[-8:]):
            p_rows.append(
                {
                    "Time": e.get("at", "")[:19].replace("T", " "),
                    "From": e.get("from_mode", ""),
                    "To": e.get("to_mode", ""),
                    "Attack type": e.get("attack_type") or "—",
                }
            )
        st.dataframe(pd.DataFrame(p_rows), use_container_width=True, hide_index=True)
    else:
        st.caption("No defence events yet.")

    st.caption("Presentation mode active. Turn it off in sidebar for full diagnostics.")
    st.stop()

# ----- Traffic classifier (offline ML sandbox) -----
st.markdown('<p class="section">3 · ML classifier (offline sandbox)</p>', unsafe_allow_html=True)
st.info(
    "**What this is:** the same **sklearn model** as the auto-detector, run **in this dashboard** on numbers you choose. "
    "It does **not** automatically mirror live traffic — it answers: “if the window looked like *this* RPS and *this* error count, what label would the model output?”\n\n"
    "**Contrast:** the **gateway** uses live `/admin/metrics` every few seconds. Use **Load live metrics** below to copy those values here, then click **Run model**."
)
# Apply values from a previous "Load live metrics" click *before* number_input mounts (Streamlit forbids
# assigning session_state.classifier_* after those widgets exist on the same run).
if "_classifier_pending" in st.session_state:
    _p = st.session_state.pop("_classifier_pending")
    st.session_state["classifier_rps"] = _p["rps"]
    st.session_state["classifier_errors"] = _p["errors"]

col_a, col_b = st.columns([1, 2])
with col_a:
    rps = st.number_input("Requests per second (synthetic input)", min_value=0, value=5, step=1, key="classifier_rps")
    errors = st.number_input("Errors in window (synthetic input)", min_value=0, value=0, step=1, key="classifier_errors")
    b1, b2 = st.columns(2)
    with b1:
        load_live = st.button("Load live metrics", use_container_width=True, help="Pull current RPS + errors from GET /admin/metrics")
    with b2:
        get_decision = st.button("Run model", type="primary", use_container_width=True, help="Run sklearn predict() on the two numbers above")
    if load_live:
        mr = _gateway.admin_metrics()
        if mr.ok and mr.data:
            live_rps = float(mr.data.get("rps") or 0)
            live_err = int(mr.data.get("errors_last_30s") or 0)
            st.session_state["_classifier_pending"] = {
                "rps": int(round(live_rps)),
                "errors": live_err,
            }
            st.session_state.dashboard_feedback = (
                "ok",
                f"Loaded **live** window: ~**{live_rps:.1f}** RPS, **{live_err}** errors (last 30s). Click **Run model**.",
            )
            st.rerun()
        else:
            st.session_state.dashboard_feedback = ("err", f"Could not read /admin/metrics: {_format_post_failure(mr)}")
            st.rerun()

with col_b:
    if get_decision:
        from ml.train_detector import predict

        label = predict(int(rps), int(errors))
        st.caption(f"Input: RPS={int(rps)}, errors={int(errors)} → model output label: **{label}**")
        if label == "attack":
            log("Detector: ATTACK")
            st.markdown(
                '<div class="decision decision-attack">'
                "<strong>Interpretation:</strong> model says <strong>attack</strong> — policy would favour blocking / not scaling into this load.</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="decision decision-attack">'
                "<strong>Scaling hint:</strong> do <strong>not</strong> add replicas for this pattern; contain at the edge.</div>",
                unsafe_allow_html=True,
            )
            if api_status == "Operational":
                if st.button("Push this to gateway: Blocking", type="primary", key="block_btn"):
                    r = _gateway.post_defence_mode("attack")
                    st.session_state.dashboard_feedback = _feedback_after_post(r)
                    st.rerun()
        else:
            log("Detector: Normal")
            st.markdown(
                '<div class="decision decision-normal">'
                "<strong>Interpretation:</strong> model says <strong>normal</strong> — traffic treated as legitimate-shaped.</div>",
                unsafe_allow_html=True,
            )
            high_load = rps >= 20
            if high_load:
                st.markdown(
                    '<div class="decision decision-normal">'
                    "<strong>Scaling hint:</strong> high load + normal label → a naive autoscaler would often <strong>scale out</strong>.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div class="decision decision-normal">'
                    "<strong>Scaling hint:</strong> load modest — hold or scale only if other signals say so.</div>",
                    unsafe_allow_html=True,
                )
    else:
        st.markdown(
            "Use **Load live metrics** to copy the gateway window, or type your own scenario, then **Run model**."
        )

# ----- Gateway control & activity -----
st.markdown('<p class="section">Gateway control & activity</p>', unsafe_allow_html=True)
def_col, activity_col = st.columns([1, 1])
with def_col:
    st.caption("Set gateway to allow traffic (Normal) or block with 429 (Blocking).")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Set gateway: Normal", key="set_normal"):
            r = _gateway.post_defence_mode("normal", manual_restore=True)
            if r.ok:
                log("Defence set to Normal")
                st.success("Normal")
                st.rerun()
            else:
                st.warning(r.error or "Start Gateway first.")
    with c2:
        if st.button("Set gateway: Blocking", key="set_attack"):
            r = _gateway.post_defence_mode("attack")
            if r.ok:
                log("Defence set to Blocking")
                st.success("Blocking")
                st.rerun()
            else:
                st.warning(r.error or "Start Gateway first.")

with activity_col:
    st.caption("Recent activity")
    lines = st.session_state.activity_log if st.session_state.activity_log else ["No activity yet."]
    html = "<div class='activity-box'>" + "".join(f"<div>{line}</div>" for line in lines) + "</div>"
    st.markdown(html, unsafe_allow_html=True)

# ----- Live defence metrics -----
st.markdown('<p class="section">Live defence metrics</p>', unsafe_allow_html=True)
d = fetch_stats()
req_total = d.get("requests_total", 0)
blocked_total = d.get("blocked_total", 0)
if defence_mode == "attack":
    st.markdown(f'''
    <div class="live-blocking">
        <div class="big-number">{blocked_total}</div>
        <div class="label"><strong>Blocked</strong> — <code style="font-size:0.9em;">GET /products</code> returned HTTP 429 this session · Total gateway requests: {req_total}</div>
        <div class="label">Run a scenario on the demo page, then <strong>Refresh status</strong> here to sync.</div>
    </div>
    ''', unsafe_allow_html=True)
else:
    st.caption("Gateway is in Normal mode. Switch to Blocking via the demo or the buttons above to see live blocked counts.")
if st.button("Refresh stats", key="refresh_stats"):
    log("Stats refreshed")
    st.rerun()

# ----- Defence history -----
st.markdown('<p class="section">Defence history (this session)</p>', unsafe_allow_html=True)
history = fetch_defence_history()
if history:
    rows = []
    for e in reversed(history[-15:]):
        rows.append({
            "Time": e.get("at", "")[:19].replace("T", " "),
            "From": e.get("from_mode", ""),
            "To": e.get("to_mode", ""),
            "Attack type": e.get("attack_type") or "—",
            "Demo source": e.get("demo_traffic_origin") or "—",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.caption("No mode changes yet. Use the demo or Gateway control above to switch Normal ↔ Blocking.")

# ----- Export -----
st.markdown('<p class="section">Export session data</p>', unsafe_allow_html=True)
export = {
    "exported_at": datetime.utcnow().isoformat() + "Z",
    "gateway_base_url": _gateway.gateway_url,
    "last_status_probe_ms": round(float(status_latency_ms), 2),
    "status": {
        "defence_mode": defence_mode,
        "last_attack_type": last_attack_type or None,
        "demo_traffic_origin": demo_traffic_origin or None,
        "demo_origin_disclaimer": demo_origin_disclaimer or None,
        "gateway": api_status,
        "catalog": catalog_status,
    },
    "stats": {"requests_total": req_total, "blocked_total": blocked_total},
    "defence_history": fetch_defence_history(),
}
export_json = json.dumps(export, indent=2)
st.download_button("Download session (JSON)", data=export_json, file_name=f"attack-aware-session-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json", mime="application/json", key="export_json")

# ----- Metrics over time -----
st.markdown('<p class="section">Metrics over time</p>', unsafe_allow_html=True)
if csv_path.exists():
    df = pd.read_csv(csv_path)
    if len(df) > 0:
        df = df.tail(30).iloc[::-1].reset_index(drop=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        if df["timestamp"].notna().any():
            chart_df = df[["timestamp", "requests_per_sec", "label"]].dropna()
            if len(chart_df) > 0:
                st.line_chart(chart_df.set_index("timestamp")["requests_per_sec"])
        display_df = df[["timestamp", "requests_per_sec", "errors", "label"]].tail(15).copy()
        display_df["timestamp"] = display_df["timestamp"].astype(str).str[:19]
        display_df["requests_per_sec"] = display_df["requests_per_sec"].fillna(0).astype(int)
        st.dataframe(display_df, use_container_width=True, hide_index=True, column_config={
            "timestamp": "Time", "requests_per_sec": "Req/s", "errors": "Errors", "label": "Label",
        })
    else:
        st.info("No rows yet. Run collect_metrics.py normal and attack.")
else:
    st.info("No data yet. Run traffic and collect_metrics scripts.")

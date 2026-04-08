"""
Gateway microservice – entry point for traffic.
- Calls Catalog service for product data when traffic is normal.
- Under attack: blocks requests (429) instead of scaling.
- Keeps a sliding window of request outcomes for ML-based auto-detection.
"""
import json
import os
import sys
import time
import sqlite3
import requests
from collections import deque
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Header

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
from attack_patterns import (  # noqa: E402
    DEMO_ORIGIN_DISCLAIMER,
    get_attack_type,
    pick_demo_traffic_origin,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, Literal
from pydantic import BaseModel, Field

app = FastAPI(
    title="Attack-Aware Autoscaling Gateway",
    description="Gateway: scale when normal, block when attack",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CATALOG_URL = os.getenv("CATALOG_URL", "http://localhost:8001")
DB_PATH = os.getenv("GATEWAY_DB_PATH", str(_PROJECT_ROOT / "data" / "gateway_events.db"))
DB_MAX_DEFENCE_EVENTS = 5000
DB_MAX_METRIC_SNAPSHOTS = 10000
# When true, POST {"mode":"normal"} is rejected while in attack unless X-Manual-Restore: 1 is sent.
# Stops old auto-detector processes or scripts from clearing defence during demos.
STICKY_DEFENCE = os.getenv("GATEWAY_STICKY_DEFENCE", "1").strip().lower() in ("1", "true", "yes")

DEFENCE_MODE = "normal"
REPLICAS = 1
REQUEST_COUNT = 0
BLOCKED_COUNT = 0
LAST_ATTACK_TYPE = ""
LAST_DEMO_ORIGIN = ""
START_TS = time.time()

# Defence-mode change history (for dashboard + export): last 50 events
DEFENCE_HISTORY: list[dict] = []
DEFENCE_HISTORY_MAX = 50

# Sliding window: (timestamp, status_code), last 60 seconds max 2000 entries
METRICS_WINDOW_SEC = 30
_request_log: deque = deque(maxlen=2000)


class DefenceModeBody(BaseModel):
    mode: Literal["normal", "attack"]
    attack_type: Optional[str] = Field(default=None, max_length=120)
    # Optional illustrative "source" for demo UI only (not real geo-IP)
    traffic_origin: Optional[str] = Field(default=None, max_length=120)


def _db_connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    with _db_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS defence_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                at TEXT NOT NULL,
                from_mode TEXT NOT NULL,
                to_mode TEXT NOT NULL,
                attack_type TEXT,
                demo_traffic_origin TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                at TEXT NOT NULL,
                requests_last_30s INTEGER NOT NULL,
                errors_last_30s INTEGER NOT NULL,
                rps REAL NOT NULL
            )
            """
        )
        conn.commit()


def _insert_defence_event(event: dict):
    with _db_connect() as conn:
        conn.execute(
            """
            INSERT INTO defence_history (at, from_mode, to_mode, attack_type, demo_traffic_origin)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                event["at"],
                event["from_mode"],
                event["to_mode"],
                event["attack_type"],
                event["demo_traffic_origin"],
            ),
        )
        conn.execute(
            """
            DELETE FROM defence_history
            WHERE id NOT IN (
                SELECT id FROM defence_history
                ORDER BY id DESC
                LIMIT ?
            )
            """,
            (DB_MAX_DEFENCE_EVENTS,),
        )
        conn.commit()


def _load_recent_defence_events(limit: int = DEFENCE_HISTORY_MAX):
    with _db_connect() as conn:
        rows = conn.execute(
            """
            SELECT at, from_mode, to_mode, attack_type, demo_traffic_origin
            FROM defence_history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    events = [dict(r) for r in rows]
    events.reverse()
    return events


def _insert_metrics_snapshot(requests_n: int, errors_n: int, rps: float):
    with _db_connect() as conn:
        conn.execute(
            """
            INSERT INTO metrics_snapshots (at, requests_last_30s, errors_last_30s, rps)
            VALUES (?, ?, ?, ?)
            """,
            (datetime.utcnow().isoformat() + "Z", int(requests_n), int(errors_n), float(rps)),
        )
        conn.execute(
            """
            DELETE FROM metrics_snapshots
            WHERE id NOT IN (
                SELECT id FROM metrics_snapshots
                ORDER BY id DESC
                LIMIT ?
            )
            """,
            (DB_MAX_METRIC_SNAPSHOTS,),
        )
        conn.commit()


def _load_recent_metrics_snapshots(limit: int = 60):
    with _db_connect() as conn:
        rows = conn.execute(
            """
            SELECT at, requests_last_30s, errors_last_30s, rps
            FROM metrics_snapshots
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    items = [dict(r) for r in rows]
    items.reverse()
    return items


def _db_stats():
    with _db_connect() as conn:
        defence_rows = conn.execute("SELECT COUNT(*) AS c FROM defence_history").fetchone()["c"]
        metrics_rows = conn.execute("SELECT COUNT(*) AS c FROM metrics_snapshots").fetchone()["c"]
        latest_defence = conn.execute(
            "SELECT at FROM defence_history ORDER BY id DESC LIMIT 1"
        ).fetchone()
        latest_metrics = conn.execute(
            "SELECT at FROM metrics_snapshots ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return {
        "db_path": DB_PATH,
        "defence_history_rows": int(defence_rows),
        "metrics_snapshots_rows": int(metrics_rows),
        "latest_defence_event_at": latest_defence["at"] if latest_defence else None,
        "latest_metrics_snapshot_at": latest_metrics["at"] if latest_metrics else None,
        "retention": {
            "max_defence_events": DB_MAX_DEFENCE_EVENTS,
            "max_metric_snapshots": DB_MAX_METRIC_SNAPSHOTS,
        },
    }


def _restore_defence_state_from_db():
    """Align in-memory defence mode with the last row in defence_history (survives gateway restarts)."""
    global DEFENCE_MODE, LAST_ATTACK_TYPE, LAST_DEMO_ORIGIN
    try:
        with _db_connect() as conn:
            row = conn.execute(
                """
                SELECT to_mode, attack_type, demo_traffic_origin
                FROM defence_history
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
        if not row:
            return
        to_mode = (row["to_mode"] or "").strip()
        if to_mode == "attack":
            DEFENCE_MODE = "attack"
            LAST_ATTACK_TYPE = (row["attack_type"] or "").strip()
            LAST_DEMO_ORIGIN = (row["demo_traffic_origin"] or "").strip()
        elif to_mode == "normal":
            DEFENCE_MODE = "normal"
            LAST_ATTACK_TYPE = ""
            LAST_DEMO_ORIGIN = ""
    except Exception:
        pass


_init_db()
_restore_defence_state_from_db()


@app.get("/")
def root():
    return {"service": "gateway", "message": "Attack-Aware Autoscaling", "time": datetime.utcnow().isoformat()}


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


def _ensure_attack_labels():
    """
    If we're in defence but labels were never set (e.g. old process, edge case),
    infer pattern from the live window and assign an illustrative origin once.
    """
    global LAST_ATTACK_TYPE, LAST_DEMO_ORIGIN
    if DEFENCE_MODE != "attack":
        return
    if not (LAST_ATTACK_TYPE or "").strip():
        rps, err = _window_rps_errors()
        LAST_ATTACK_TYPE = get_attack_type(float(rps), int(err))
    if not (LAST_DEMO_ORIGIN or "").strip():
        LAST_DEMO_ORIGIN = pick_demo_traffic_origin()


@app.get("/admin/status")
def admin_status():
    _ensure_attack_labels()
    return {
        "defence_mode": DEFENCE_MODE,
        "replicas": REPLICAS,
        "last_attack_type": LAST_ATTACK_TYPE or None,
        "demo_traffic_origin": LAST_DEMO_ORIGIN or None,
        "demo_origin_disclaimer": DEMO_ORIGIN_DISCLAIMER if DEFENCE_MODE == "attack" else None,
    }


@app.get("/admin/history")
def admin_history():
    """Last N defence-mode changes (timestamp, from, to, attack_type). For dashboard and export."""
    events = _load_recent_defence_events(DEFENCE_HISTORY_MAX)
    return {"events": events}


@app.get("/admin/db")
def admin_db():
    """Database diagnostics for demos and operations."""
    return _db_stats()


def _model_metrics_path():
    """Path to ml/model_metrics.json (project root = parent of services)."""
    return Path(__file__).resolve().parent.parent.parent / "ml" / "model_metrics.json"


@app.get("/admin/model-info")
def admin_model_info():
    """ML model metrics (e.g. accuracy) for demo/dashboard badge. Optional file."""
    p = _model_metrics_path()
    if not p.exists():
        return {"accuracy": None}
    try:
        with open(p) as f:
            data = json.load(f)
        return {"accuracy": data.get("accuracy")}
    except Exception:
        return {"accuracy": None}


def _trim_window():
    global _request_log
    now = time.time()
    while _request_log and _request_log[0][0] < now - METRICS_WINDOW_SEC:
        _request_log.popleft()


def _window_rps_errors():
    """Current sliding-window request rate and error count (same basis as /admin/metrics)."""
    _trim_window()
    if not _request_log:
        return 0.0, 0
    requests_n = len(_request_log)
    errors_n = sum(1 for _, status in _request_log if status >= 429 or status >= 500)
    rps = requests_n / METRICS_WINDOW_SEC
    return round(rps, 2), errors_n


def _policy_view_from_window(rps: float, errors_n: int, requests_n: int) -> dict:
    """
    Explain traffic shape vs actions for demos: ML + same heuristic as auto_detector,
    contrast naive autoscaling (scale on load) with attack-aware policy (scale only if not attack-like).
    """
    rps_int = int(round(rps))
    model_label = "normal"
    try:
        from ml.train_detector import predict

        model_label = str(predict(rps_int, errors_n))
    except Exception:
        pass

    stress_attack_like = model_label == "attack"
    if not stress_attack_like and rps >= 8 and requests_n >= 25:
        stress_attack_like = True

    high_load = rps >= 6.0 or requests_n >= 12
    naive_would_scale = high_load
    attack_aware_would_scale = high_load and not stress_attack_like
    defence_on = DEFENCE_MODE == "attack"

    if requests_n < 2 and rps < 0.5:
        traffic_verdict = "Quiet window — looks like idle or a single light user."
    elif stress_attack_like:
        traffic_verdict = (
            "Window treated as attack-like stress (model + demo rules): "
            "not the same as one normal shopper refreshing slowly."
        )
    elif high_load:
        traffic_verdict = (
            "Busy but legitimate-shaped traffic in the window — similar to flash-sale load "
            "(classifier did not label it attack-like)."
        )
    else:
        traffic_verdict = "Normal browsing-level activity in the sliding window."

    if defence_on:
        edge_behaviour = "blocking"
        our_story = (
            "Defence ON: /products returns 429 at the gateway — catalog is not proxying these requests. "
            "No amount of extra catalog replicas would fix abuse; you refuse it at the edge."
        )
        naive_story = (
            "Naive RPS/CPU autoscaler would often still spin up catalog pods under this load — "
            "paying to serve traffic you should block."
        )
    else:
        edge_behaviour = "forwarding"
        if stress_attack_like:
            our_story = (
                "Gateway still forwarding — detector may flip defence next tick. "
                "Attack-aware stance: do NOT scale catalog for attack-shaped windows; block instead when mode switches."
            )
            naive_story = "Naive autoscaler: high load → add servers (even if load is abusive)."
        elif attack_aware_would_scale:
            our_story = (
                "Forwarding to catalog. Attack-aware stance: this load looks legitimate — "
                "in a full platform you would scale catalog replicas here (prototype keeps 1 instance)."
            )
            naive_story = "Naive autoscaler: high load → add servers (same recommendation for this window)."
        else:
            our_story = "Forwarding to catalog. Load below scaling threshold — hold steady."
            naive_story = "Naive autoscaler: hold steady — load is modest."

    return {
        "model_label": model_label,
        "stress_treated_as": "attack_like" if stress_attack_like else "legitimate_like",
        "high_load": high_load,
        "naive_autoscaling_would": "spin_up_more_servers" if naive_would_scale else "hold_steady",
        "attack_aware_scaling_would": "spin_up_more_servers" if attack_aware_would_scale else "hold_steady",
        "edge_behaviour": edge_behaviour,
        "defence_mode": DEFENCE_MODE,
        "catalog_instances_configured": REPLICAS,
        "prototype_note": "Single catalog process in this demo — scaling actions are recommendations, not live K8s events.",
        "lines": {
            "traffic_verdict": traffic_verdict,
            "naive_autoscaling": naive_story,
            "attack_aware": our_story,
        },
    }


@app.get("/admin/metrics")
def admin_metrics():
    """Live metrics for the last N seconds so the auto-detector can call the ML model."""
    rps, errors_n = _window_rps_errors()
    requests_n = len(_request_log)
    _insert_metrics_snapshot(requests_n, errors_n, rps)
    return {
        "requests_last_30s": requests_n,
        "errors_last_30s": errors_n,
        "rps": float(rps),
    }


@app.get("/admin/metrics-history")
def admin_metrics_history(limit: int = 60):
    """Recent persisted metrics snapshots for dashboard/export."""
    safe_limit = max(1, min(int(limit), 500))
    return {"items": _load_recent_metrics_snapshots(safe_limit)}


@app.get("/admin/stats")
def admin_stats():
    """Live counts: total requests and how many were blocked (429). Dashboard can show this."""
    rps, errors_n = _window_rps_errors()
    requests_n = len(_request_log)
    return {
        "defence_mode": DEFENCE_MODE,
        "requests_total": REQUEST_COUNT,
        "blocked_total": BLOCKED_COUNT,
        "policy": _policy_view_from_window(rps, errors_n, requests_n),
    }


@app.get("/admin/overview")
def admin_overview():
    """
    One-call backend overview for live demos:
    mode, traffic window metrics, counters, DB state, and uptime.
    """
    rps, errors_n = _window_rps_errors()
    requests_n = len(_request_log)
    uptime_sec = int(time.time() - START_TS)
    return {
        "service": "gateway",
        "defence_mode": DEFENCE_MODE,
        "last_attack_type": LAST_ATTACK_TYPE or None,
        "demo_traffic_origin": LAST_DEMO_ORIGIN or None,
        "sticky_defence": STICKY_DEFENCE,
        "uptime_sec": uptime_sec,
        "window_metrics": {
            "requests_last_30s": requests_n,
            "errors_last_30s": errors_n,
            "rps": float(rps),
        },
        "counters": {
            "requests_total": REQUEST_COUNT,
            "blocked_total": BLOCKED_COUNT,
        },
        "policy": _policy_view_from_window(rps, errors_n, requests_n),
        "database": _db_stats(),
    }


@app.get("/admin/defence-mode")
def get_defence_mode():
    return {"defence_mode": DEFENCE_MODE}


@app.post("/admin/defence-mode")
def set_defence_mode(
    body: DefenceModeBody,
    x_manual_restore: Optional[str] = Header(None, alias="X-Manual-Restore"),
):
    global DEFENCE_MODE, LAST_ATTACK_TYPE, LAST_DEMO_ORIGIN, DEFENCE_HISTORY
    if STICKY_DEFENCE and body.mode == "normal" and DEFENCE_MODE == "attack":
        token = (x_manual_restore or "").strip().lower()
        if token not in ("1", "true", "yes"):
            return JSONResponse(
                status_code=409,
                content={
                    "detail": "Sticky defence active: only an operator UI can clear attack mode. "
                    "Send header X-Manual-Restore: 1 (demo and dashboard do this automatically)."
                },
            )

    prev = DEFENCE_MODE
    # Already blocking: update illustrative labels only (no new defence_history row).
    # Allows the scenario profile to refresh gateway copy after auto-detect without a duplicate mode transition.
    if (
        body.mode == "attack"
        and prev == "attack"
        and (body.attack_type is not None or body.traffic_origin is not None)
    ):
        if body.attack_type is not None:
            LAST_ATTACK_TYPE = body.attack_type
        if body.traffic_origin is not None:
            LAST_DEMO_ORIGIN = body.traffic_origin
        return {
            "defence_mode": DEFENCE_MODE,
            "last_attack_type": LAST_ATTACK_TYPE or None,
            "demo_traffic_origin": LAST_DEMO_ORIGIN or None,
            "relabel_only": True,
        }

    DEFENCE_MODE = body.mode
    if body.mode == "normal":
        LAST_ATTACK_TYPE = ""
        LAST_DEMO_ORIGIN = ""
    else:
        # Infer pattern label from live window if caller did not specify
        if body.attack_type:
            LAST_ATTACK_TYPE = body.attack_type
        else:
            rps, err = _window_rps_errors()
            LAST_ATTACK_TYPE = get_attack_type(float(rps), int(err))
        if body.traffic_origin:
            LAST_DEMO_ORIGIN = body.traffic_origin
        else:
            LAST_DEMO_ORIGIN = pick_demo_traffic_origin()
    event = {
        "at": datetime.utcnow().isoformat() + "Z",
        "from_mode": prev,
        "to_mode": DEFENCE_MODE,
        "attack_type": (LAST_ATTACK_TYPE or None) if body.mode == "attack" else None,
        "demo_traffic_origin": (LAST_DEMO_ORIGIN or None) if body.mode == "attack" else None,
    }
    DEFENCE_HISTORY.append(event)
    if len(DEFENCE_HISTORY) > DEFENCE_HISTORY_MAX:
        DEFENCE_HISTORY.pop(0)
    _insert_defence_event(event)
    return {
        "defence_mode": DEFENCE_MODE,
        "last_attack_type": LAST_ATTACK_TYPE or None,
        "demo_traffic_origin": LAST_DEMO_ORIGIN or None,
    }


def _record_request(status_code: int):
    _request_log.append((time.time(), status_code))


@app.get("/products")
def products():
    """
    When defence_mode is "attack": block all requests (429).
    When normal: forward to Catalog microservice.
    Records each request for the metrics window (for ML auto-detection).
    """
    global DEFENCE_MODE, REQUEST_COUNT, BLOCKED_COUNT
    REQUEST_COUNT += 1
    if DEFENCE_MODE == "attack":
        BLOCKED_COUNT += 1
        _record_request(429)
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limited (attack defence active)"},
        )
    try:
        r = requests.get(f"{CATALOG_URL}/products", timeout=2)
        if r.status_code == 200:
            _record_request(200)
            return r.json()
    except Exception:
        pass
    _record_request(503)
    return JSONResponse(
        status_code=503,
        content={"detail": "Catalog unavailable"},
    )

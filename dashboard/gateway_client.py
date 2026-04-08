"""
Typed HTTP client for the Attack-Aware Autoscaling gateway API.

Separates transport from the Streamlit UI: retries, latency tracking, connection reuse,
and configurable base URLs — the kind of structure you'd use before a real service mesh.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

import requests

T = TypeVar("T")


@dataclass(frozen=True)
class ApiResult(Generic[T]):
    """One round-trip to the gateway: payload or failure, always with timing."""

    ok: bool
    data: Optional[T]
    latency_ms: float
    status_code: Optional[int] = None
    error: Optional[str] = None


class GatewayClient:
    """
    Session-backed client (HTTP keep-alive) with explicit timeouts and JSON helpers.
    Set GATEWAY_URL / CATALOG_URL in the environment for non-local deployments.
    """

    def __init__(
        self,
        gateway_url: Optional[str] = None,
        catalog_url: Optional[str] = None,
        timeout: float = 5.0,
    ) -> None:
        self.gateway_url = (gateway_url or os.environ.get("GATEWAY_URL", "http://localhost:8000")).rstrip(
            "/"
        )
        self.catalog_url = (catalog_url or os.environ.get("CATALOG_URL", "http://localhost:8001")).rstrip(
            "/"
        )
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json", "User-Agent": "attack-aware-dashboard/1.0"})

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json_body: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> ApiResult[Any]:
        url = f"{self.gateway_url}{path}"
        t0 = time.perf_counter()
        try:
            r = self._session.request(
                method,
                url,
                params=params,
                json=json_body,
                headers=headers,
                timeout=self.timeout,
            )
            ms = (time.perf_counter() - t0) * 1000
            if r.status_code == 200:
                try:
                    return ApiResult(True, r.json(), ms, r.status_code, None)
                except Exception as ex:
                    return ApiResult(False, None, ms, r.status_code, f"Invalid JSON: {ex}")
            err = (r.text or "")[:300]
            return ApiResult(False, None, ms, r.status_code, err or f"HTTP {r.status_code}")
        except Exception as ex:
            ms = (time.perf_counter() - t0) * 1000
            return ApiResult(False, None, ms, None, str(ex))

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> ApiResult[Any]:
        return self._request("GET", path, params=params)

    def post(
        self,
        path: str,
        json_body: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> ApiResult[Any]:
        return self._request("POST", path, json_body=json_body, headers=headers)

    def health(self) -> ApiResult[Any]:
        return self.get("/health")

    def admin_status(self) -> ApiResult[Any]:
        return self.get("/admin/status")

    def admin_stats(self) -> ApiResult[Any]:
        return self.get("/admin/stats")

    def admin_metrics(self) -> ApiResult[Any]:
        """Live sliding-window metrics (RPS, errors) — same feed as the auto-detector."""
        return self.get("/admin/metrics")

    def admin_history(self) -> ApiResult[Any]:
        return self.get("/admin/history")

    def admin_metrics_history(self, limit: int = 120) -> ApiResult[Any]:
        return self.get("/admin/metrics-history", params={"limit": limit})

    def admin_overview(self) -> ApiResult[Any]:
        return self.get("/admin/overview")

    def admin_db(self) -> ApiResult[Any]:
        return self.get("/admin/db")

    def post_defence_mode(
        self,
        mode: str,
        *,
        attack_type: Optional[str] = None,
        traffic_origin: Optional[str] = None,
        manual_restore: bool = False,
    ) -> ApiResult[Any]:
        body: dict[str, Any] = {"mode": mode}
        if attack_type is not None:
            body["attack_type"] = attack_type
        if traffic_origin is not None:
            body["traffic_origin"] = traffic_origin
        headers: dict[str, str] = {}
        if manual_restore:
            headers["X-Manual-Restore"] = "1"
        hdr = headers if headers else None
        return self.post("/admin/defence-mode", json_body=body, headers=hdr)

    def catalog_health(self) -> ApiResult[Any]:
        t0 = time.perf_counter()
        try:
            r = self._session.get(f"{self.catalog_url}/health", timeout=min(self.timeout, 3.0))
            ms = (time.perf_counter() - t0) * 1000
            if r.status_code == 200:
                try:
                    return ApiResult(True, r.json(), ms, r.status_code, None)
                except Exception:
                    return ApiResult(True, {}, ms, r.status_code, None)
            return ApiResult(False, None, ms, r.status_code, r.text[:200])
        except Exception as ex:
            ms = (time.perf_counter() - t0) * 1000
            return ApiResult(False, None, ms, None, str(ex))

    def fetch_backend_status(self, status_retries: int = 3) -> tuple[dict[str, Any], float]:
        """
        Aggregate gateway + catalog reachability. Returns (status_dict, last_latency_ms).
        Mirrors the previous dashboard behaviour (retries on transient failure).
        """
        out: dict[str, Any] = {
            "api_status": "Unreachable",
            "catalog_status": "Unreachable",
            "replicas": 1,
            "defence_mode": None,
            "last_attack_type": "",
            "demo_traffic_origin": "",
            "demo_origin_disclaimer": "",
            "gateway_reachable": False,
        }
        last_ms = 0.0
        for _ in range(max(1, status_retries)):
            h = self.health()
            last_ms = h.latency_ms
            if h.ok:
                out["api_status"] = "Operational"
            elif h.status_code is not None:
                out["api_status"] = "Degraded"
            if h.ok and h.data is not None:
                s = self.admin_status()
                last_ms = s.latency_ms
                if s.ok and s.data:
                    d = s.data
                    out["replicas"] = d.get("replicas", 1)
                    out["defence_mode"] = d.get("defence_mode") or "normal"
                    out["last_attack_type"] = d.get("last_attack_type") or ""
                    out["demo_traffic_origin"] = d.get("demo_traffic_origin") or ""
                    out["demo_origin_disclaimer"] = d.get("demo_origin_disclaimer") or ""
                    out["gateway_reachable"] = True
                    break
            time.sleep(0.3)

        if not out["gateway_reachable"]:
            out["defence_mode"] = "normal"

        ch = self.catalog_health()
        last_ms = ch.latency_ms
        if ch.ok:
            out["catalog_status"] = "Operational"
        elif ch.status_code is not None:
            out["catalog_status"] = "Degraded"

        return out, last_ms

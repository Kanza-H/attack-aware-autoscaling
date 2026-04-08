"""
Heuristic attack labels + illustrative demo-only "origin" lines.

Used by the gateway and ML auto-detector. Labels are inferred from
request rate and error counts in the sliding window — not from real
client geo-IP (this prototype does not capture that).
"""
from __future__ import annotations

import random


def get_attack_type(requests_per_sec: float, errors: int) -> str:
    """
    Classify attack *pattern* for display when defence mode is attack.
    Same inputs as before (RPS + errors in window); expanded taxonomy.
    """
    rps = float(requests_per_sec)
    err = int(errors)

    if rps >= 45 and err >= 25:
        return "Layer-7 flood (volume + error storm)"
    if rps >= 50 and err < 15:
        return "Volumetric burst / aggressive API scrape"
    if rps >= 40 and err >= 10:
        return "Mixed application-layer DDoS"
    if rps >= 35:
        return "High-RPS application flood"
    if err >= 20 and rps >= 6:
        return "Credential stuffing / brute-force pattern"
    if err >= 15:
        return "Auth endpoint hammering (error-heavy)"
    if rps >= 22 and err <= 5:
        return "Stealthy high-rate scrape"
    if rps >= 14:
        return "Sustained traffic spike"
    if err >= 8:
        return "Client error surge (possible abuse)"
    return "Anomalous traffic (weak signal)"


DEMO_ORIGIN_CHOICES = [
    "Illustrative label: multi-region mix (EU + Americas)",
    "Illustrative label: single-ASN burst cluster",
    "Illustrative label: VPN / anonymiser exit pool",
    "Illustrative label: major cloud provider IP range",
    "Illustrative label: mobile CGNAT sweep",
    "Illustrative label: datacentre scraper farm",
]


def pick_demo_traffic_origin() -> str:
    """Randomised *demo narrative* only — not derived from real IP/geo data."""
    return random.choice(DEMO_ORIGIN_CHOICES)


DEMO_ORIGIN_DISCLAIMER = (
    "Prototype: traffic is from your machine (localhost). "
    "Source lines are illustrative demo labels, not real geo-IP."
)

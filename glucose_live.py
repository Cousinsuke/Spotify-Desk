"""Local-only Nightscout / Gluroo live glucose reader.

Reads Nightscout-compatible CGM entries via HTTPS; never touches Abbott auth.
Secrets are provided via process environment (never browser/Git/Flask logs).
Medical data remains in-memory and is NEVER served to LAN clients by app route.
This is a secondary informational display, not a source for insulin decisions.
"""
from __future__ import annotations

import ipaddress
import math
import os
import re
import threading
import time
from urllib.parse import urlsplit

import requests

POLL_SECONDS = 150  # Gluroo recommends no more frequently than 2 minutes.
STALE_SECONDS = 600  # Distinguish stale from live without hiding sample time.
MAX_READINGS = 730
ALLOWED_DIRECTIONS = frozenset({
    "DoubleUp", "SingleUp", "FortyFiveUp", "Flat",
    "FortyFiveDown", "SingleDown", "DoubleDown"
})


def validate_url(value: str) -> str:
    """Validate an operator-provided remote API base URL (not browser input)."""
    parsed = urlsplit((value or "").strip())
    host = parsed.hostname or ""
    if (parsed.scheme != "https" or not host or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.query or parsed.fragment
            or parsed.path not in ("", "/") or len(host) > 250):
        raise ValueError("Glucose source must be an HTTPS base URL without paths, ports or credentials.")
    if not re.fullmatch(r"[A-Za-z0-9.-]+", host) or "." not in host or ".." in host:
        raise ValueError("Glucose source hostname is invalid.")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("Glucose source must use a DNS hostname, not an IP address.")
    return "https://" + host.lower()


def normalise_entries(raw: object, now: float) -> list[dict]:
    if not isinstance(raw, list):
        raise ValueError("Glucose source did not return an array.")
    readings = {}
    for item in raw[:MAX_READINGS]:
        if not isinstance(item, dict) or item.get("type", "sgv") != "sgv":
            continue
        value = item.get("sgv")
        timestamp = item.get("date", item.get("mills"))
        if (type(value) not in (int, float) or not math.isfinite(value)
                or type(timestamp) not in (int, float) or not math.isfinite(timestamp)):
            continue
        value = float(value) / 18.0182
        stamp = int(timestamp)
        # API uses epoch ms. Refuse wildly future-dated readings and old history.
        if not (0.5 <= value <= 40 and now * 1000 - 24 * 3600000 <= stamp <= now * 1000 + 120000):
            continue
        direction = item.get("direction")
        direction = direction if direction in ALLOWED_DIRECTIONS else None
        readings[stamp] = {
            "timestamp": stamp,
            "mmol": round(value, 2),
            "direction": direction,
        }
    return [readings[k] for k in sorted(readings)]


class LiveGlucose:
    def __init__(self, url: str = "", api_secret_sha1: str = "", http_get=None, clock=None):
        self._clock = clock or time.time
        self._get = http_get or requests.get
        self._lock = threading.RLock()
        self.config_error = False
        self.url = ""
        self.secret_hash = ""
        if url or api_secret_sha1:
            try:
                self.url = validate_url(url)
                sha = api_secret_sha1.strip().lower()
                if not re.fullmatch(r"[0-9a-f]{40}", sha):
                    raise ValueError("Expected 40-character SHA-1 API credential.")
                self.secret_hash = sha
            except (ValueError, TypeError):
                self.config_error = True
        self.entries: list[dict] = []
        self.last_success = 0.0
        self.next_fetch = 0.0
        self.failure = False

    @classmethod
    def from_environment(cls):
        return cls(
            os.getenv("DESK_GLUCOSE_URL", ""),
            os.getenv("DESK_GLUCOSE_API_SECRET_SHA1", ""),
        )

    def state(self) -> dict:
        """Cache requests across tabs; never return a fabricated reading."""
        if self.config_error:
            return {"status": "configuration_error", "readings": []}
        if not self.url:
            return {"status": "not_configured", "readings": []}
        with self._lock:
            now = self._clock()
            if now >= self.next_fetch:
                self.next_fetch = now + POLL_SECONDS
                try:
                    response = self._get(
                        self.url + "/api/v1/entries/sgv.json",
                        params={"count": MAX_READINGS},
                        headers={"api-secret": self.secret_hash, "Accept": "application/json"},
                        timeout=(4, 9),
                        allow_redirects=False,
                    )
                    if response.status_code == 429:
                        # Gluroo request budget resets 00:00 UTC; avoid retry storm.
                        self.next_fetch = (int(now // 86400) + 1) * 86400
                        raise ValueError("Rate limited")
                    if response.status_code in (401, 403):
                        raise ValueError("Not authorised")
                    if response.status_code != 200:
                        raise ValueError("Source unavailable")
                    if len(response.content) > 250_000:
                        raise ValueError("Response too large")
                    entries = normalise_entries(response.json(), now)
                    if not entries:
                        raise ValueError("No recent readings")
                    self.entries = entries
                    self.last_success = now
                    self.failure = False
                except (requests.RequestException, ValueError, TypeError):
                    # Never expose upstream URL, credentials or server traceback.
                    self.failure = True
            latest = self.entries[-1] if self.entries else None
            if not latest:
                return {"status": "unavailable", "readings": [], "retry_seconds": max(0, round(self.next_fetch - now))}
            age = max(0, int(now - latest["timestamp"] / 1000))
            healthy = not self.failure and age < STALE_SECONDS
            return {
                "status": "live" if healthy else "stale",
                "latest": latest,
                "readings": self.entries,
                "age_seconds": age,
                "last_contact_seconds": max(0, int(now - self.last_success)),
                "retry_seconds": max(0, round(self.next_fetch - now)),
            }

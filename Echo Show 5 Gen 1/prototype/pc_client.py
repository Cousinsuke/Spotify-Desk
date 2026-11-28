"""Read-only PC connection via fixed Pi loopback SSH tunnel."""
import json
import os
import stat
from pathlib import Path
import re
import requests

TOKEN_PATH = Path.home() / ".spotify-desk" / "pc-agent-token"
URL = "http://127.0.0.1:8877/state"
LIMIT = 16384


def read_token():
    with os.fdopen(os.open(TOKEN_PATH, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK), "r", encoding="ascii") as f:
        info = os.fstat(f.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > 128:
            raise ValueError("Unsafe PC token file")
        token = f.read(128).strip()
    if not re.fullmatch(r"[0-9a-f]{64}", token):
        raise ValueError("Invalid PC token")
    return token


def normalize(data):
    if not isinstance(data, dict) or data.get("ok") is not True or type(data.get("hasPlayback")) is not bool:
        raise ValueError("Invalid PC state")
    active = data["hasPlayback"]
    def text(key):
        value = data.get(key)
        return value[:240] if isinstance(value, str) else ""
    def ms(key):
        value = data.get(key)
        return min(value, 86400000) if type(value) is int and value >= 0 else 0
    duration, position = ms("durationMs"), ms("positionMs")
    volume = data.get("volume")
    return {"connected": True, "hasPlayback": active,
            "title": text("title") if active else "", "artist": text("artist") if active else "",
            "playing": active and data.get("playing") is True,
            "durationMs": duration if active else 0,
            "positionMs": min(position, duration) if duration and active else position if active else 0,
            "volume": volume if active and type(volume) is int and 0 <= volume <= 100 else None}


def snapshot():
    try:
        token = read_token()
    except (OSError, ValueError, UnicodeError):
        return {"connected": False, "error": "PC companion not configured"}
    try:
        with requests.Session() as session:
            session.trust_env = False
            with session.get(URL, headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                             timeout=(1, 4), allow_redirects=False, stream=True) as response:
                if response.status_code != 200 or not response.headers.get("Content-Type", "").lower().startswith("application/json"):
                    raise ValueError("PC response rejected")
                raw = bytearray()
                for chunk in response.iter_content(4096):
                    raw.extend(chunk)
                    if len(raw) > LIMIT:
                        raise ValueError("PC response too large")
                return normalize(json.loads(raw))
    except (requests.RequestException, ValueError, OSError):
        return {"connected": False, "error": "PC companion unavailable"}

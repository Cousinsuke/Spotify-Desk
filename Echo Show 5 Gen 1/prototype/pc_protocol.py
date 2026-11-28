"""Shared PC command and artwork validation. No network or OS access."""
import hashlib
import re

ACTIONS = frozenset(("play", "pause", "next", "previous", "shuffle", "repeat", "volume", "save"))


def track_key(value):
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest() if isinstance(value, str) and value else ""


def valid_key(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def command_body(data):
    if not isinstance(data, dict) or not isinstance(data.get("action"), str) or data["action"] not in ACTIONS or not valid_key(data.get("trackKey")):
        raise ValueError("Invalid PC command")
    a = data["action"]
    if set(data) != ({"action", "trackKey", "value"} if a in ("shuffle", "repeat", "volume", "save") else {"action", "trackKey"}):
        raise ValueError("Invalid PC fields")
    v = data.get("value")
    if a in ("shuffle", "save") and type(v) is not bool:
        raise ValueError("Explicit boolean required")
    if a == "repeat" and v not in ("None", "Playlist", "Track"):
        raise ValueError("Invalid repeat mode")
    if a == "volume" and (type(v) is not int or v not in (-5, 5)):
        raise ValueError("Invalid volume step")
    return data

def spotify_uri(value):
    return value if isinstance(value, str) and re.fullmatch(r"spotify:track:[A-Za-z0-9]{22}", value) else ""

def native_track_uri(raw):
    # Only exact native Spotify MPRIS track identity, never title matching.
    if raw.get("device_id") != "spotify":
        return ""
    key = raw.get("track_key")
    if not isinstance(key, str):
        return ""
    parts = key.split("|", 2)
    if len(parts) != 3 or parts[0] != "spotify":
        return ""
    match = re.fullmatch(r"/com/spotify/track/([A-Za-z0-9]{22})", parts[1])
    return "spotify:track:" + match.group(1) if match else spotify_uri(parts[1])



def approved_art(value):
    if isinstance(value, str) and len(value) <= 2048 and re.fullmatch(r"https://(?:i\.scdn\.co|image-cdn-ak\.spotifycdn\.com|image-cdn-fa\.spotifycdn\.com)/[A-Za-z0-9_./%?=&+~:-]+", value):
        return value
    return ""

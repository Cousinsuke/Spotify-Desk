"""Shared PC command and artwork validation. No network or OS access."""
import hashlib
import re

ACTIONS = frozenset(("play", "pause", "next", "previous"))


def track_key(value):
    return hashlib.sha256(value.encode("utf-8", "replace")).hexdigest() if isinstance(value, str) and value else ""


def valid_key(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def command_body(data):
    if not isinstance(data, dict) or set(data) != {"action", "trackKey"} or not isinstance(data["action"], str) or data["action"] not in ACTIONS or not valid_key(data["trackKey"]):
        raise ValueError("Invalid PC command")
    return data


def approved_art(value):
    if isinstance(value, str) and len(value) <= 2048 and re.fullmatch(r"https://(?:i\.scdn\.co|image-cdn-ak\.spotifycdn\.com|image-cdn-fa\.spotifycdn\.com)/[A-Za-z0-9_./%?=&+~:-]+", value):
        return value
    return ""

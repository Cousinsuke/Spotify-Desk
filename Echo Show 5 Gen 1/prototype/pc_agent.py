"""PC media agent. Loopback HTTP, bearer authenticated, SSH tunnel only."""
import argparse
import hmac
import json
import os
from pathlib import Path
import secrets
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import URLError
import re
import shlex
from pc_protocol import approved_art, command_body, track_key, native_track_uri

PORT = 8877
TOKEN_FILE = Path.home() / ".spotify-desk" / "pc-agent-token"
MAX_BODY = 16384


def valid_token(value):
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def token_file(create=False):
    if create and not TOKEN_FILE.exists():
        TOKEN_FILE.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        try:
            with os.fdopen(os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as f:
                f.write(secrets.token_hex(32) + "\n")
        except FileExistsError:
            pass
    if os.name == "posix" and TOKEN_FILE.stat().st_mode & 0o077:
        raise ValueError("Token file permissions must be 0600")
    token = TOKEN_FILE.read_text(encoding="ascii").strip()
    if not valid_token(token):
        raise ValueError("Invalid PC agent token")
    return token


def make_adapter():
    # Reuse the existing, unchanged desktop adapters from the same checkout.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    if sys.platform == "linux":
        from linux_companion import LinuxCompanion
        class EchoLinuxCompanion(LinuxCompanion):
            def _property(self, name, prop):
                try:
                    return shlex.split(self._run("busctl", "--user", "get-property", "org.mpris.MediaPlayer2." + name,
                        "/org/mpris/MediaPlayer2", "org.mpris.MediaPlayer2.Player", prop))
                except Exception:
                    return []

            def capabilities(self, raw):
                name = raw.get("device_id")
                if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", name):
                    return {}
                shuffle = self._property(name, "Shuffle")
                loop = self._property(name, "LoopStatus")
                return {"shuffle": shuffle == ["b", "true"] if shuffle in (["b", "true"], ["b", "false"]) else None,
                        "repeat": loop[1] if len(loop) == 2 and loop[0] == "s" and loop[1] in ("None", "Playlist", "Track") else None}

            def command_for(self, action, expected, value=None):
                # Re-read the selected session, then call the exact MPRIS bus
                # name. Never reselect another player or fall back to Connect.
                with self._guard:
                    raw = self.status(force=True)
                    name = raw.get("device_id")
                    if raw.get("ok") is not True or raw.get("has_playback") is not True or track_key(raw.get("track_key")) != expected:
                        return False
                    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*", name):
                        return False
                    bus = "org.mpris.MediaPlayer2." + name
                    path = "/org/mpris/MediaPlayer2"
                    interface = "org.mpris.MediaPlayer2.Player"
                    if action == "volume":
                        level = self._volume()
                        if type(level) is not int:
                            return False
                        return self.command("volume", max(0, min(100, level + value)))
                    if action in ("shuffle", "repeat"):
                        caps = self.capabilities(raw)
                        if caps.get(action) is None:
                            return False
                        prop, sig, val = ("Shuffle", "b", str(value).lower()) if action == "shuffle" else ("LoopStatus", "s", value)
                        self._run("busctl", "--user", "set-property", bus, path, interface, prop, sig, val)
                    else:
                        method = {"play": "Play", "pause": "Pause", "next": "Next", "previous": "Previous"}[action]
                        self._run("busctl", "--user", "call", bus, path, interface, method)
                    self._cached = None
                    return True

        return EchoLinuxCompanion()
    if sys.platform == "win32":
        from windows_companion import WindowsCompanion
        return WindowsCompanion()
    raise RuntimeError("Unsupported PC platform")


def snapshot(adapter, controls=False):
    try:
        raw = adapter.status()
        if raw.get("ok") is not True:
            raise RuntimeError("Adapter unavailable")
        def bounded(value):
            return str(value or "")[:240]
        def millis(value):
            return min(value, 86400000) if type(value) is int and value >= 0 else 0
        playing = raw.get("has_playback") is True
        volume = raw.get("volume")
        volume = volume if type(volume) is int and 0 <= volume <= 100 else None
        caps = adapter.capabilities(raw) if playing and callable(getattr(adapter, "capabilities", None)) else {}
        return {"ok": True, "hasPlayback": playing,
                "shuffle": caps.get("shuffle"), "repeat": caps.get("repeat"),
                "spotifyUri": native_track_uri(raw) if playing else "",
                "title": bounded(raw.get("title")) if playing else "",
                "artist": bounded(raw.get("artist")) if playing else "",
                "trackKey": track_key(raw.get("track_key")) if playing else "",
                "canControl": bool(controls and playing and raw.get("track_key") and callable(getattr(adapter, "command_for", None))),
                "art": approved_art(raw.get("artwork")) if playing else "",
                "playing": playing and raw.get("playing") is True,
                "durationMs": millis(raw.get("duration_ms")) if playing else 0,
                "positionMs": millis(raw.get("progress_ms")) if playing else 0,
                "volume": volume if playing else None}
    except Exception:
        return {"ok": False, "error": "PC media adapter unavailable"}


def handler_for(adapter, token, controls=False):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            self.request.settimeout(5)
            super().setup()

        def log_message(self, *args):
            pass

        def reply(self, code, data):
            body = json.dumps(data, ensure_ascii=True).encode("ascii")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            auth = self.headers.get("Authorization", "")
            if not hmac.compare_digest(auth.encode("utf-8"), ("Bearer " + token).encode("ascii")):
                self.reply(401, {"ok": False})
                return
            if self.path != "/state":
                self.reply(404, {"ok": False})
                return
            state = snapshot(adapter, controls)
            self.reply(200 if state["ok"] else 503, state)

        def do_POST(self):
            auth = self.headers.get("Authorization", "")
            if not hmac.compare_digest(auth.encode("utf-8"), ("Bearer " + token).encode("ascii")):
                self.reply(401, {"ok": False})
                return
            if not controls or self.path != "/command" or not callable(getattr(adapter, "command_for", None)):
                self.reply(405, {"ok": False})
                return
            if self.headers.get_content_type() != "application/json":
                self.reply(415, {"ok": False})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if not 1 <= length <= 512:
                    raise ValueError("Invalid length")
                data = command_body(json.loads(self.rfile.read(length)))
            except (ValueError, OSError):
                self.reply(400, {"ok": False})
                return
            try:
                if data["action"] == "save":
                    self.reply(405, {"ok": False})
                    return
                args = (data["action"], data["trackKey"])
                accepted = adapter.command_for(*args, data["value"]) if "value" in data else adapter.command_for(*args)
            except Exception:
                self.reply(503, {"ok": False})
                return
            self.reply(200 if accepted is True else 409, {"ok": accepted is True})

    return Handler


def check(token):
    request = Request(f"http://127.0.0.1:{PORT}/state", headers={"Authorization": "Bearer " + token})
    # Do not use environment HTTP proxies for local credentials.
    with build_opener(ProxyHandler({})).open(request, timeout=15) as response:
        data = response.read(MAX_BODY + 1)
        if len(data) > MAX_BODY:
            raise ValueError("Oversized PC state")
        state = json.loads(data)
    return state


def report(state):
    # Only capability flags are printed, never track names, IDs or tokens.
    print(json.dumps({"ok": state.get("ok") is True,
                      "hasPlayback": state.get("hasPlayback") is True,
                      "playing": state.get("playing") is True,
                      "titleAvailable": bool(state.get("title")),
                      "artistAvailable": bool(state.get("artist")),
                      "durationAvailable": bool(state.get("durationMs")),
                      "positionAvailable": state.get("positionMs", 0) > 0,
                      "volumeAvailable": state.get("volume") is not None,
                      "artworkAvailable": bool(state.get("art")),
                      "controlsAvailable": state.get("canControl") is True,
                      "shuffleAvailable": type(state.get("shuffle")) is bool,
                      "repeatAvailable": state.get("repeat") in ("None", "Playlist", "Track"),
                      "spotifyTrackIdentified": bool(state.get("spotifyUri"))}, indent=2))
    return 0 if state.get("ok") is True else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("probe", "serve", "check"))
    parser.add_argument("--controls", action="store_true", help="enable tested Linux media commands when serving")
    parser.add_argument("--token-stdin", action="store_true", help="check only; read token from stdin")
    args = parser.parse_args()
    if args.controls and args.action != "serve":
        parser.error("--controls requires serve")
    if args.token_stdin and args.action != "check":
        parser.error("--token-stdin requires check")
    try:
        if args.action == "probe":
            return report(snapshot(make_adapter()))
        if args.action == "check":
            token = sys.stdin.read(256).strip() if args.token_stdin else token_file()
            if not valid_token(token):
                raise ValueError("Invalid token")
            return report(check(token))
        token = token_file(create=True)
        with HTTPServer(("127.0.0.1", PORT), handler_for(make_adapter(), token, args.controls)) as server:
            print(("PC agent (controls requested)" if args.controls else "Read-only PC agent") + " listening on 127.0.0.1:8877. Ctrl+C to stop.", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, RuntimeError, URLError, ImportError):
        print("PC agent unavailable; check adapter dependencies, token and tunnel.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Spotify Desk Thing — local desktop touchscreen prototype.

Runs on Windows 11 or Omarchy/Arch. LAN device endpoints require --lan.
"""

import io
import argparse
import json
import os
import secrets
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import spotipy
from flask import Flask, Response, jsonify, redirect, render_template, request, session, url_for, send_file
from spotipy.cache_handler import CacheFileHandler
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyPKCE
from device_bridge import install_device_bridge

# One shared Flask interface; select only the platform-specific local adapter.
if sys.platform == 'win32':
    from windows_companion import windows as local_companion
    DESKTOP_PLATFORM = 'windows'
elif sys.platform == 'linux':
    from linux_companion import linux as local_companion
    DESKTOP_PLATFORM = 'linux'
else:
    raise SystemExit('Local PC mode is currently supported on Windows and Linux only.')

BASE = Path(__file__).resolve().parent
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPES = "user-read-playback-state user-modify-playback-state"
CONFIG_PATH = BASE / '.desk_config.json'


def saved_client_id():
    try:
        value = json.loads(CONFIG_PATH.read_text('utf-8')).get('spotify_client_id', '')
        return value.strip() if isinstance(value, str) else ''
    except (OSError, ValueError, TypeError, AttributeError):
        return ''


def configure():
    print('Enter the Client ID from your Spotify developer app (not a Client Secret).')
    value = input('Spotify Client ID: ').strip()
    if len(value) != 32 or not value.isascii() or not value.isalnum():
        raise SystemExit('Invalid Client ID format. Expected 32 letters/digits.')
    temp = CONFIG_PATH.with_suffix('.json.tmp')
    temp.write_text(json.dumps({'spotify_client_id': value}, indent=2) + '\n', 'utf-8')
    if os.name == 'posix':
        os.chmod(temp, 0o600)
    os.replace(temp, CONFIG_PATH)
    print('Saved to local configuration file. No Client Secret stored.')

if __name__ == '__main__' and '--configure' in sys.argv:
    configure()
    raise SystemExit(0)

LAN_ENABLED = __name__ == '__main__' and '--lan' in sys.argv
CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID', '').strip() or saved_client_id()
if not CLIENT_ID:
    raise SystemExit('Missing Spotify Client ID. Run: python desk_ui.py --configure')

app = Flask(__name__)
app.secret_key = secrets.token_bytes(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  MAX_CONTENT_LENGTH=16384)

auth = SpotifyPKCE(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    scope=SCOPES,
    cache_handler=CacheFileHandler(cache_path=str(BASE / ".spotify_token.json")),
    open_browser=False,
)
spotify = spotipy.Spotify(
    auth_manager=auth,
    requests_timeout=10,
    retries=0,
    status_retries=0,
)

# Limit requests; the Spotify developer quota can also be shared by other apps.
lock = threading.RLock()
state_cache = {"value": None, "expires": 0.0}
cooldown_until = 0.0
POLL_SECONDS = 5  # Active-page refresh: at most one API lookup per 5 seconds across tabs.


def error_json(error):
    global cooldown_until
    status = getattr(error, "http_status", 500)
    if not isinstance(status, int) or not 400 <= status <= 599:
        status = 500
    result = {"ok": False, "error": str(getattr(error, "msg", str(error)))[:220]}
    if status == 429:
        headers = getattr(error, "headers", {}) or {}
        try:
            retry_after = max(30, int(headers.get("Retry-After", 60)))
        except (ValueError, TypeError):
            retry_after = 60
        cooldown_until = time.monotonic() + retry_after
        result["retry_after"] = retry_after
        result["error"] = "Spotify rate limit reached. Requests paused."
    elif status == 401:
        result["error"] = "Spotify authorization expired. Select Connect Spotify."
    return jsonify(result), status


def empty_state():
    return {"ok": True, "connected": True, "has_playback": False}


def playback_state():
    state = spotify.current_playback()
    if not state:
        return empty_state()

    item = state.get("item") or {}
    album = item.get("album") or {}
    device = state.get("device") or {}
    artists = item.get("artists") or []
    images = album.get("images") or item.get("images") or []
    artwork = images[0].get("url") if images else None
    # Music images are from Spotify's image CDN, not an arbitrary client URL.
    if artwork and urlparse(artwork).scheme != "https":
        artwork = None
    return {
        "ok": True,
        "connected": True,
        "has_playback": True,
        "title": item.get("name") or "Unknown track",
        # Stable identity lets the browser distinguish an updated track from
        # Spotify returning the previous track briefly after a skip command.
        "track_key": item.get("uri") or item.get("id") or "",
        "artist": ", ".join(a.get("name", "") for a in artists) or "Unknown artist",
        "album": album.get("name") or "",
        "artwork": artwork,
        "playing": bool(state.get("is_playing")),
        "progress_ms": state.get("progress_ms") or 0,
        "duration_ms": item.get("duration_ms") or 0,
        "device": device.get("name") or "Unknown device",
        "device_id": device.get("id"),
        "volume": device.get("volume_percent"),
        "supports_volume": bool(device.get("supports_volume", True)),
        "updated_at": time.time(),
    }


@app.get("/")
def index():
    return render_template("index.html", desktop_platform=DESKTOP_PLATFORM)


@app.get("/login")
def login():
    state = secrets.token_urlsafe(24)
    session["oauth_state"] = state
    return redirect(auth.get_authorize_url(state=state))


@app.get("/callback")
def callback():
    expected = session.pop("oauth_state", None)
    received = request.args.get("state", "")
    if not expected or not secrets.compare_digest(expected, received):
        return "OAuth state mismatch. Go back and select Connect Spotify again.", 400
    if request.args.get("error"):
        return "Spotify authorization was declined. Go back and try again.", 400
    code = request.args.get("code")
    if not code:
        return "Missing Spotify authorization code.", 400
    try:
        auth.get_access_token(code, check_cache=False)
    except Exception:
        return "Spotify authorization failed. Return to the main page and try again.", 400
    with lock:
        state_cache["expires"] = 0
    return redirect(url_for("index"))


def reject_untrusted_post():
    # Browser access is local-only and mutations require a same-origin request.
    origin = request.headers.get("Origin")
    if origin not in (None, "http://127.0.0.1:8888"):
        return jsonify({"ok": False, "error": "Invalid request origin."}), 403
    if not request.is_json:
        return jsonify({"ok": False, "error": "Expected JSON."}), 415
    return None


@app.get("/api/devices")
def get_devices():
    # Devices are listed only when the user asks; no extra API polling.
    with lock:
        if not auth.get_cached_token():
            return jsonify({"ok": False, "error": "Connect Spotify first."}), 401
        if time.monotonic() < cooldown_until:
            return jsonify({"ok": False, "error": "Spotify rate limit cooldown active.",
                            "retry_after": round(cooldown_until - time.monotonic())}), 429
        try:
            devices = spotify.devices().get("devices", [])
            return jsonify({"ok": True, "devices": [
                {"id": d.get("id"), "name": d.get("name") or "Unknown device",
                 "type": d.get("type") or "Unknown", "active": bool(d.get("is_active")),
                 "restricted": bool(d.get("is_restricted"))}
                for d in devices if d.get("id")
            ]})
        except SpotifyException as error:
            return error_json(error)
        except Exception:
            return jsonify({"ok": False, "error": "Unable to list Spotify devices."}), 503


@app.post("/api/activate")
def activate_device():
    global cooldown_until
    invalid = reject_untrusted_post()
    if invalid is not None:
        return invalid
    body = request.get_json(silent=True) or {}
    chosen = body.get("device_id")
    if not isinstance(chosen, str) or not 1 <= len(chosen) <= 200:
        return jsonify({"ok": False, "error": "Select a valid device."}), 400

    with lock:
        if not auth.get_cached_token():
            return jsonify({"ok": False, "error": "Connect Spotify first."}), 401
        if time.monotonic() < cooldown_until:
            return jsonify({"ok": False, "error": "Spotify rate limit cooldown active."}), 429
        try:
            # Do not allow an arbitrary device ID supplied by a web request.
            available = spotify.devices().get("devices", [])
            target = next((d for d in available if d.get("id") == chosen), None)
            if not target:
                return jsonify({"ok": False, "error": "Device no longer available. Open Spotify and try again."}), 409
            if target.get("is_restricted"):
                return jsonify({"ok": False, "error": "This Spotify device does not support remote control."}), 409
            spotify.transfer_playback(device_id=chosen, force_play=False)
            state_cache["expires"] = 0
            return jsonify({"ok": True, "message": "Device selected. Start or resume music in Spotify if needed."})
        except SpotifyException as error:
            return error_json(error)
        except Exception:
            return jsonify({"ok": False, "error": "Unable to select Spotify device."}), 503


@app.get("/api/status")
def get_status():
    global cooldown_until
    with lock:
        if not auth.get_cached_token():
            return jsonify({"ok": True, "connected": False, "has_playback": False})
        now = time.monotonic()
        if now < cooldown_until:
            return jsonify({
                "ok": False,
                "error": "Spotify rate limit cooldown active.",
                "retry_after": round(cooldown_until - now),
            }), 429
        if request.args.get("fresh") != "1" and state_cache["expires"] > now and state_cache["value"] is not None:
            return jsonify(state_cache["value"])
        try:
            value = playback_state()
            state_cache.update(value=value, expires=time.monotonic() + POLL_SECONDS)
            return jsonify(value)
        except SpotifyException as error:
            return error_json(error)
        except Exception:
            return jsonify({"ok": False, "error": "Unable to read Spotify playback."}), 503


@app.post("/api/control")
def control():
    invalid = reject_untrusted_post()
    if invalid is not None:
        return invalid
    body = request.get_json(silent=True) or {}
    return _wifi_execute(body.get('action'), body.get('value'))


def _wifi_execute(action, value=None):
    if action not in {"toggle", "next", "previous", "volume"}:
        return jsonify({"ok": False, "error": "Unknown action."}), 400

    with lock:
        if not auth.get_cached_token():
            return jsonify({"ok": False, "error": "Connect Spotify first."}), 401
        if time.monotonic() < cooldown_until:
            return jsonify({"ok": False, "error": "Spotify rate limit cooldown active."}), 429
        try:
            current = spotify.current_playback()
            device = (current or {}).get("device") or {}
            device_id = device.get("id")
            if not current or not device_id:
                # The UI may still be showing a cached track. Drop it immediately.
                state_cache["expires"] = 0
                state_cache["value"] = None
                return jsonify({
                    "ok": False,
                    "error": "No active playback device. Open Spotify, start a song, then use Refresh track. You can also select a device below."
                }), 409
            if action == "toggle":
                if current.get("is_playing"):
                    spotify.pause_playback(device_id=device_id)
                else:
                    spotify.start_playback(device_id=device_id)
            elif action == "next":
                spotify.next_track(device_id=device_id)
            elif action == "previous":
                spotify.previous_track(device_id=device_id)
            elif action == "volume":
                volume = value
                if type(volume) is not int or not 0 <= volume <= 100:
                    return jsonify({"ok": False, "error": "Volume must be 0–100."}), 400
                if device.get("supports_volume") is False:
                    return jsonify({"ok": False, "error": "This device does not support volume control."}), 409
                spotify.volume(volume_percent=volume, device_id=device_id)
            state_cache["expires"] = 0
            return jsonify({"ok": True, "message": "Command sent"})
        except SpotifyException as error:
            return error_json(error)
        except Exception:
            return jsonify({"ok": False, "error": "Unable to send Spotify command."}), 503


# Phase 4.2: Spotify's player/device volume and the computer's master volume
# are distinct controls. When the PC media session is Spotify, prefer its
# Spotify Connect volume (the same one displayed in WI-FI mode).
# Other local players continue using Windows/PipeWire system volume.
def _same_spotify_track(local_state, spotify_state):
    if not local_state.get('has_playback') or not spotify_state.get('has_playback'):
        return False
    if 'spotify' not in str(local_state.get('source', '')).casefold():
        return False
    title1 = str(local_state.get('title', '')).strip().casefold()
    title2 = str(spotify_state.get('title', '')).strip().casefold()
    if not title1 or title1 != title2:
        return False
    # MPRIS sometimes sends an abbreviated artist list; require at least
    # the leading artist to match so we don't control another device's song.
    a = str(local_state.get('artist', '')).split(',')[0].strip().casefold()
    b = str(spotify_state.get('artist', '')).split(',')[0].strip().casefold()
    return not (a and b and a != b)


def _cached_spotify_volume_state():
    global cooldown_until
    with lock:
        if not auth.get_cached_token() or time.monotonic() < cooldown_until:
            return None
        now = time.monotonic()
        if state_cache['expires'] > now and state_cache['value'] is not None:
            return dict(state_cache['value'])
        try:
            state = playback_state()
            state_cache.update(value=state, expires=time.monotonic() + POLL_SECONDS)
            return dict(state)
        except SpotifyException as exc:
            # Respect Spotify's global Retry-After without breaking PC mode.
            if getattr(exc, 'http_status', None) == 429:
                error_json(exc)
            return None
        except Exception:
            return None


def _pc_with_volume_source(local_state):
    state = dict(local_state)
    state['volume_source'] = 'system'
    if not state.get('ok', True) or not state.get('has_playback'):
        return state
    if 'spotify' not in str(state.get('source', '')).casefold():
        return state
    spotify_state = _cached_spotify_volume_state()
    if not spotify_state or not _same_spotify_track(state, spotify_state):
        # Spotify was not authorized, is unavailable, or is playing on a
        # different device. Keep a clearly labelled system-volume fallback.
        return state
    state['volume_source'] = 'spotify'
    state['volume'] = spotify_state.get('volume')
    state['supports_volume'] = (
        bool(spotify_state.get('supports_volume'))
        and type(spotify_state.get('volume')) is int
    )
    return state


# Phase 4.1 — Windows/Omarchy media companion (localhost, same-origin).
@app.get('/api/pc/status')
def pc_status():
    local_state = local_companion.status(force=request.args.get('fresh') == '1')
    return jsonify(_pc_with_volume_source(local_state))


@app.get('/api/pc/audio')
def pc_audio():
    # Retained as a compatible low-rate fallback for clients without EventSource.
    local_companion.start_meter()
    return jsonify(local_companion.meter_state())


@app.get('/api/pc/audio/stream')
def pc_audio_stream():
    """Stream audio amplitudes over one persistent localhost connection.

    No raw samples are transmitted. The meter itself runs in a background
    thread; this yields snapshots at ~10Hz for smooth browser animation.
    """
    local_companion.start_meter()

    def events():
        yield 'retry: 5000\n\n'
        try:
            while True:
                snapshot = local_companion.meter_state()
                yield f'data: {json.dumps(snapshot, separators=(",", ":"))}\n\n'
                time.sleep(0.10)
        except GeneratorExit:
            # A closed tab or mode change closes this connection.
            return

    return Response(events(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache, no-transform',
        'X-Accel-Buffering': 'no',
    })


@app.get('/api/pc/artwork')
def pc_artwork():
    raw, content_type = local_companion.artwork()
    if not raw:
        return '', 404
    response = send_file(io.BytesIO(raw), mimetype=content_type)
    response.headers['Cache-Control'] = 'private, max-age=1'
    return response


@app.post('/api/pc/control')
def pc_control():
    invalid = reject_untrusted_post()
    if invalid is not None:
        return invalid
    data = request.get_json(silent=True) or {}
    return _pc_execute(data.get('action'), data.get('value'))


def _pc_execute(action, value=None):
    if action not in ('toggle','next','previous','volume'):
        return jsonify({'ok':False,'error':'Unknown local media action.'}),400
    try:
        if action == 'volume':
            if type(value) is not int or not 0 <= value <= 100:
                return jsonify({'ok':False,'error':'Volume must be an integer from 0 to 100.'}),400
            local_state = _pc_with_volume_source(local_companion.status())
            if local_state.get('volume_source') == 'spotify':
                with lock:
                    if time.monotonic() < cooldown_until:
                        return jsonify({'ok':False,'error':'Spotify rate limit cooldown active.'}),429
                    try:
                        # Confirm the track is still local before modifying any
                        # Spotify Connect volume; never affect a different song.
                        current = spotify.current_playback()
                        device = (current or {}).get('device') or {}
                        current_item = (current or {}).get('item') or {}
                        current_song = {
                            'has_playback':bool(current),
                            'title':current_item.get('name'),
                            'artist':', '.join(a.get('name','') for a in (current_item.get('artists') or [])),
                        }
                        if not _same_spotify_track(local_state, current_song):
                            state_cache['expires'] = 0
                            return jsonify({'ok':False,'error':'Spotify playback changed; refresh the track and retry.'}),409
                        if not device.get('id') or device.get('supports_volume') is False:
                            return jsonify({'ok':False,'error':'Spotify device volume is unavailable.'}),409
                        spotify.volume(volume_percent=value, device_id=device['id'])
                        # Keep the requested value briefly so the fast PC polling
                        # cannot immediately redraw an out-of-date percentage.
                        if state_cache['value'] is not None:
                            state_cache['value'] = {**state_cache['value'], 'volume':value}
                        state_cache['expires'] = time.monotonic() + 1.5
                        result = True
                    except SpotifyException as exc:
                        return error_json(exc)
                    except Exception:
                        return jsonify({'ok':False,'error':'Spotify volume control unavailable.'}),503
            else:
                result = local_companion.command(action, value)
        else:
            result = local_companion.command(action, value)
    except (ValueError, TypeError) as exc:
        return jsonify({'ok':False,'error':str(exc)}),400
    except Exception as exc:
        app.logger.warning('Local media control error: %s', exc)
        return jsonify({'ok':False,'error':'Local media control unavailable. Check the console.'}),503
    if not result:
        return jsonify({'ok':False,'error':'Local media player did not accept this command.'}),409
    return jsonify({'ok':True,'message':'Local media command sent'})


# Phase 5 -- deliberately separate authenticated device API from the original
# browser console and Spotify OAuth endpoints.
def _device_state(mode):
    if mode == 'pc':
        return _pc_with_volume_source(local_companion.status())
    with lock:
        if not auth.get_cached_token():
            return {'ok': True, 'connected': False, 'has_playback': False}
        if time.monotonic() < cooldown_until:
            return {'ok': False, 'error': 'Spotify rate limit cooldown active.', 'has_playback': False}
        now = time.monotonic()
        if state_cache['value'] is not None and state_cache['expires'] > now:
            return dict(state_cache['value'])
        try:
            result = playback_state()
            state_cache.update(value=result, expires=time.monotonic() + POLL_SECONDS)
            return result
        except SpotifyException as exc:
            error_json(exc)
            return {'ok': False, 'error': 'Spotify playback unavailable.', 'has_playback': False}
        except Exception:
            return {'ok': False, 'error': 'Spotify playback unavailable.', 'has_playback': False}


def _device_command(mode, action, value):
    return _pc_execute(action, value) if mode == 'pc' else _wifi_execute(action, value)


def _device_meter():
    local_companion.start_meter()
    return local_companion.meter_state()


device_store = install_device_bridge(
    app, base=BASE, lan_enabled=LAN_ENABLED,
    state_cb=_device_state, command_cb=_device_command,
    artwork_cb=local_companion.artwork, meter_cb=_device_meter,
)

# Avoid printing Spotify's short-lived OAuth authorization codes in terminal logs.
from werkzeug.serving import WSGIRequestHandler

class RedactedRequestHandler(WSGIRequestHandler):
    def log_request(self, code='-', size='-'):
        if self.path.startswith('/callback?'):
            old_path = self.path
            try:
                self.path = '/callback?[authorization-code-redacted]'
                return super().log_request(code, size)
            finally:
                self.path = old_path
        return super().log_request(code, size)


if __name__ == '__main__':
    print('Spotify Desk Thing — Phase 5 companion')
    print('Desktop console: http://127.0.0.1:8888')
    print('Local pairing page: http://127.0.0.1:8888/pair')
    print('Device simulator: http://127.0.0.1:8888/device')
    print(f'One-time device pairing code (10 min): {device_store.code}')
    if LAN_ENABLED:
        print('LAN device mode ENABLED: open http://YOUR-PC-IP:8888/device on the same trusted network.')
        print('All original desktop/API/OAuth endpoints remain loopback-only.')
    else:
        print('LAN device mode disabled. Add --lan to permit paired devices on your local network.')
    print('Ctrl+C to stop.')
    app.run(host='0.0.0.0' if LAN_ENABLED else '127.0.0.1',
            port=8888, debug=False, use_reloader=False, threaded=True,
            request_handler=RedactedRequestHandler)

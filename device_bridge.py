"""Phase 5 device pairing and constrained network API.

The HTTP transport intentionally uses ordinary JSON and bearer headers so a
future ESP32 firmware can use it without a browser, SDK, or client secret.
"""
from __future__ import annotations

import ipaddress
import json
import os
import secrets
import threading
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
from flask import Response, jsonify, render_template, request

EXPOSED = frozenset({
    '/device', '/static/device.css', '/static/device.js', '/static/ui.css',
    '/static/desk-dashboard.css', '/static/desk-dashboard.js', '/static/glucose-history.js', '/static/glucose-chart.js',
    '/api/device/pair', '/api/device/state', '/api/device/action',
    '/api/device/artwork', '/api/device/events',
})


def device_artwork_url(artwork: object) -> str | None:
    """Keep web artwork direct; proxy only known companion-local thumbnails.

    A Linux MPRIS artUrl may already be HTTPS. Advertising a local artwork
    endpoint for such tracks used to trigger endless 404s in PC mode.
    """
    if not isinstance(artwork, str):
        return None
    if artwork.startswith('https://'):
        return artwork
    url = urlsplit(artwork)
    if url.scheme or url.netloc or url.fragment or url.path != '/api/pc/artwork':
        return None
    values = parse_qs(url.query).get('key', [])
    if len(values) != 1:
        return None
    key = values[0]
    if not key or len(key) > 20 or not key.isascii() or not key.isdecimal():
        return None
    return '/api/device/artwork?key=' + key


def is_loopback(addr: str | None) -> bool:
    try:
        return ipaddress.ip_address(addr or '').is_loopback
    except ValueError:
        return False


class PairingStore:
    def __init__(self, path: Path, now=None):
        self.path = Path(path)
        self._now = now or time.monotonic
        self.lock = threading.RLock()
        self.devices = {}
        self._failures = {}
        self.code = None
        self.code_expiry = 0.0
        self._load()
        self.rotate()

    def _load(self):
        try:
            raw = json.loads(self.path.read_text('utf-8'))
            devices = raw.get('devices')
            if isinstance(devices, dict):
                for token, info in devices.items():
                    if (isinstance(token, str) and len(token) == 64
                            and isinstance(info, dict) and info.get('mode') in ('pc', 'spotify')):
                        self.devices[token] = {'name': str(info.get('name', 'Device'))[:40],
                                               'mode': info['mode']}
        except (OSError, ValueError, TypeError):
            pass

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + '.tmp')
        with tmp.open('w', encoding='utf-8') as handle:
            json.dump({'version': 1, 'devices': self.devices}, handle, indent=2)
        if os.name == 'posix':
            os.chmod(tmp, 0o600)
        os.replace(tmp, self.path)

    def rotate(self):
        with self.lock:
            self.code = f'{secrets.randbelow(1_000_000):06d}'
            self.code_expiry = self._now() + 600
            self._failures.clear()
            return self.code

    def pairing(self, supplied: object, name: object, addr: str):
        with self.lock:
            now = self._now()
            attempts = [t for t in self._failures.get(addr, []) if now - t < 900]
            if len(attempts) >= 5:
                self._failures[addr] = attempts
                return None, 'Too many attempts. Try again in 15 minutes.', 429
            if (type(supplied) is not str or len(supplied) != 6 or not supplied.isascii()
                    or not supplied.isdigit() or self.code is None
                    or now > self.code_expiry or not secrets.compare_digest(self.code, supplied)):
                attempts.append(now)
                self._failures[addr] = attempts
                return None, 'Invalid or expired pairing code.', 403
            if len(self.devices) >= 8:
                return None, 'Maximum paired devices reached. Revoke unused devices.', 409
            token = secrets.token_hex(32)
            safe_name = name.strip()[:40] if isinstance(name, str) else 'Desk Thing'
            self.devices[token] = {'name': safe_name or 'Desk Thing', 'mode': 'pc'}
            self.code = None  # One-time code: generate another on local /pair
            self.code_expiry = 0
            self._save()
            return token, None, 200

    def get(self, bearer: str | None):
        if not bearer or not bearer.startswith('Bearer '):
            return None
        token = bearer[7:]
        with self.lock:
            for expected, info in self.devices.items():
                if secrets.compare_digest(expected, token):
                    return token, dict(info)
        return None

    def mode(self, token, mode):
        with self.lock:
            if token not in self.devices or mode not in ('pc', 'spotify'):
                return False
            self.devices[token]['mode'] = mode
            self._save()
            return True

    def clear(self):
        with self.lock:
            self.devices.clear()
            self._save()
            self.rotate()


def install_device_bridge(app, *, base: Path, lan_enabled: bool, state_cb, command_cb,
                          artwork_cb, meter_cb):
    """Wire pairing + device endpoints. Callbacks stay platform independent."""
    store = PairingStore(base / '.desk_devices.json')

    @app.before_request
    def block_desktop_over_lan():
        # Do not expose OAuth, status, login, desktop UI or other original APIs.
        if is_loopback(request.remote_addr):
            return None
        if not lan_enabled or request.path not in EXPOSED:
            return jsonify({'ok': False, 'error': 'Desktop endpoints are local-only.'}), 403
        return None

    def origin_allowed():
        origin = request.headers.get('Origin')
        return not origin or origin.rstrip('/') == request.host_url.rstrip('/')

    def require_local_json():
        if not is_loopback(request.remote_addr):
            return jsonify({'ok': False, 'error': 'Only local host may manage pairing.'}), 403
        if not request.is_json or not origin_allowed():
            return jsonify({'ok': False, 'error': 'Invalid JSON or Origin.'}), 403
        return None

    def require_device():
        if not origin_allowed():
            return None
        return store.get(request.headers.get('Authorization'))

    def fail_auth():
        return jsonify({'ok': False, 'error': 'Pair this device first.'}), 401

    @app.get('/device')
    def device_ui():
        return render_template('device.html')

    @app.get('/pair')
    def pairing_ui():
        if not is_loopback(request.remote_addr):
            return '', 403
        return render_template('pair.html')

    @app.get('/api/device/pairing')
    def pairing_details():
        if not is_loopback(request.remote_addr):
            return '', 403
        with store.lock:
            return jsonify({'ok': True, 'code': store.code,
                            'seconds_remaining': max(0, int(store.code_expiry-store._now())),
                            'devices': [v['name'] for v in store.devices.values()]})

    @app.post('/api/device/pairing/new')
    def new_pair_code():
        invalid = require_local_json()
        if invalid is not None:
            return invalid
        return jsonify({'ok': True, 'code': store.rotate(), 'expires_in': 600})

    @app.post('/api/device/pairing/revoke-all')
    def revoke_paired_devices():
        invalid = require_local_json()
        if invalid is not None:
            return invalid
        store.clear()
        return jsonify({'ok': True, 'message': 'All device tokens revoked.'})

    @app.post('/api/device/pair')
    def pair():
        if not request.is_json or not origin_allowed():
            return jsonify({'ok': False, 'error': 'Invalid JSON or Origin.'}), 403
        body = request.get_json(silent=True) or {}
        token, error, status = store.pairing(body.get('code'), body.get('name'), request.remote_addr or '')
        if error:
            return jsonify({'ok': False, 'error': error}), status
        return jsonify({'ok': True, 'token': token, 'mode': 'pc'})

    def state_payload(info):
        mode = info['mode']
        try:
            result = state_cb(mode)
            if not isinstance(result, dict):
                raise ValueError('Missing state')
            fields = ('ok', 'connected', 'has_playback', 'title', 'artist', 'album',
                      'track_key', 'playing', 'progress_ms', 'duration_ms', 'device',
                      'volume', 'volume_source', 'supports_volume', 'source', 'artwork', 'error')
            state = {key: result[key] for key in fields if key in result}
            artwork = state.get('artwork')
            if mode == 'pc':
                state['artwork'] = device_artwork_url(artwork) if state.get('has_playback') else None
            elif not (isinstance(artwork, str) and artwork.startswith('https://')):
                state['artwork'] = None
            state['mode'] = mode
            state['ok'] = bool(state.get('ok', True))
            return state
        except Exception:
            return {'ok': False, 'mode': mode, 'has_playback': False,
                    'error': 'Companion media state unavailable.'}

    @app.get('/api/device/state')
    def get_device_state():
        paired = require_device()
        if not paired:
            return fail_auth()
        response = jsonify(state_payload(paired[1]))
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/api/device/artwork')
    def device_artwork():
        paired = require_device()
        if not paired:
            return fail_auth()
        if paired[1]['mode'] != 'pc':
            return '', 404
        # An artwork request can arrive just after a skip. Only serve the
        # thumbnail if the requested key still belongs to the current track;
        # never accidentally show the next song's artwork on the old song.
        current_artwork = device_artwork_url(state_cb('pc').get('artwork'))
        if current_artwork != '/api/device/artwork?key=' + request.args.get('key', ''):
            return '', 404
        result = artwork_cb()
        if not result or not result[0]:
            return '', 404
        from flask import send_file
        from io import BytesIO
        response = send_file(BytesIO(result[0]), mimetype=result[1])
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.post('/api/device/action')
    def device_action():
        paired = require_device()
        if not paired:
            return fail_auth()
        if not request.is_json:
            return jsonify({'ok': False, 'error': 'JSON required.'}), 415
        body = request.get_json(silent=True) or {}
        action = body.get('action')
        token, info = paired
        if action == 'mode':
            if body.get('value') not in ('pc', 'spotify'):
                return jsonify({'ok': False, 'error': 'Invalid mode.'}), 400
            store.mode(token, body['value'])
            return jsonify({'ok': True, 'mode': body['value']})
        allowed = {'toggle', 'next', 'previous', 'volume', 'volume_step'}
        if action not in allowed:
            return jsonify({'ok': False, 'error': 'Unknown action.'}), 400
        value = body.get('value')
        if action == 'volume_step':
            if type(value) is not int or value not in (-5, 5):
                return jsonify({'ok': False, 'error': 'Volume step must be -5 or 5.'}), 400
            current = state_payload(info)
            volume = current.get('volume')
            if type(volume) is not int or not current.get('supports_volume', True):
                return jsonify({'ok': False, 'error': 'Current volume is unavailable.'}), 409
            action, value = 'volume', max(0, min(100, volume + value))
        if action == 'volume' and (type(value) is not int or not 0 <= value <= 100):
            return jsonify({'ok': False, 'error': 'Volume must be 0–100.'}), 400
        if action != 'volume':
            value = None
        return command_cb(info['mode'], action, value)

    @app.get('/api/device/events')
    def device_events():
        paired = require_device()
        if not paired:
            return fail_auth()
        token = paired[0]

        def messages():
            yield 'retry: 4000\n\n'
            next_state = 0.0
            next_meter = 0.0
            try:
                while True:
                    with store.lock:
                        info = dict(store.devices[token]) if token in store.devices else None
                    if info is None:
                        yield 'event: revoked\ndata: {}\n\n'
                        return
                    now = time.monotonic()
                    if now >= next_state:
                        yield 'event: state\ndata: ' + json.dumps(state_payload(info), separators=(',', ':')) + '\n\n'
                        next_state = now + (0.9 if info['mode'] == 'pc' else 2.5)
                    if info['mode'] == 'pc' and now >= next_meter:
                        try:
                            meter = meter_cb()
                            snapshot = {'available': bool(meter.get('available')), 'level': meter.get('level', 0)}
                            yield 'event: meter\ndata: ' + json.dumps(snapshot, separators=(',', ':')) + '\n\n'
                        except Exception:
                            pass
                        next_meter = now + 0.15
                    time.sleep(0.10 if info['mode'] == 'pc' else 0.35)
            except GeneratorExit:
                return

        return Response(messages(), content_type='text/event-stream', headers={
            'Cache-Control': 'no-cache, no-transform', 'X-Accel-Buffering': 'no',
        })
    return store

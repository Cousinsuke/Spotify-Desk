# Echo Show 5 browser prototype — increment 2

Static, offline-only UI shell; no service connection, credentials, actual CGM data, firmware changes, real playback or hardware backlight control. All sample data is fabricated. Existing root application is unchanged.

Run on Omarchy from the repository root:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory "Echo Show 5 Gen 1/prototype"
```

Open http://127.0.0.1:8765/ in a desktop browser. Designed for 960 x 480 at 100% zoom; use browser responsive mode if needed. Ctrl+C stops the server.

Implemented: Home with three sample widgets and real local clock; right rail with 10-second default auto-hide and reflow, arrow/edge swipe reveal, Apps drawer with outside/close/select dismissal, Settings Centre shell with General/Navigation controls, top-edge swipe-down quick settings (click top handle for desktop), Graphite/Black, rail appearance, opacity, animation, timeout, per-page hide, preview brightness dimming, manual preview night mode, preference-only local storage and reset. Home always opens on reload. Scheduled night mode is a labelled planned setting, not active. Spotify sample player added: artwork left, mode dropdown (Echo disabled), play/pause, previous/next, seek, shuffle/repeat, save state, floating sample device selector, selectable background and contextual quick settings. No real playback or audio. Calendar/System and Weather/Glucose remain labelled planned destinations. Spotify contextual quick settings are implemented in preview; other app-specific controls and pin/reorder are pending. No Pi preference server yet.

Validation required: browser layout and gestures, accessibility, timer/focus behavior, actual device resource use; Home increment visually accepted by user on Omarchy; Spotify runtime review and hardware testing pending. Run node --check app.js if Node is installed. Use synthetic data only. Next: Weather and Glucose pages using existing chart renderer, then expanded settings and app registry.

## Increment 3 — UI fixes and opt-in live Spotify test

Tap empty content to hide an expanded auto-hide rail; interactive controls and open overlays remain unaffected. Save is a bare circle with green saved state; mode/device selectors use neutral translucent styling. Browser review pending.

Live mode is an isolated loopback Flask server, PKCE with in-memory access/refresh tokens, explicit state check, same-origin API guards, no token logging or disk cache. Stop the static server first. Add `http://127.0.0.1:8765/spotify/callback` to your existing Spotify app Redirect URIs. From repo root:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements-ui.txt
env SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID' ./.venv/bin/python 'Echo Show 5 Gen 1/prototype/live_server.py'
```

Replace YOUR_CLIENT_ID locally (no client secret). Open http://127.0.0.1:8765/?live=1 then Spotify and Connect Spotify. Premium and app user permission required. Real Wi-Fi playback only; PC/Echo disabled. Current library URI endpoints used. Tokens disappear on process exit; no LAN/CGM connection. Live artwork uses original Spotify CDN with neutral background until colour extraction is implemented. No real account or runtime server test yet. Static demo remains available on /.

## Increment 4 — live playback response and progress fixes

User corrected the callback URI and reported real Spotify worked until Pause. The command crashed parsing a non-JSON success body. All successful non-GET acknowledgements and 204/empty responses now bypass JSON parsing; invalid GET JSON produces a controlled error. Frontend distinguishes server errors from a missing live API, serializes commands against in-flight polls, and projects time locally with monotonic clock, duration clamp, 15-second extrapolation cap, pause/disconnect freeze and seek drag protection. Poll interval remains five seconds. Ten pure clock assertions passed in assistant JS runtime; four additional mocked Python tests authored (13 total), pending local run. No real account retest yet. Restart live server, reconnect, hard refresh, then test play/pause/skip/seek and timer.

## Increment 5 — pause synchronization and inactive device recovery

User confirmed 13 Python tests passed and Pause reached iPhone; browser lagged and Previous reported active device changed/unavailable. Keep one historical track on empty playback, visibly labelled, verify same device through available devices before allowing resume/skip, no automatic transfer or alternate-device commands. Use explicit desired play/pause state, acknowledge locally, bounded read-only confirmation polls (250/650/1300 ms waits) after commands; no write retries, ordinary 5s polling unchanged. Show pending status, temporary error messages and re-sync with actual response. No seek/save on historical track. Actual live behavior still pending. Six additional Python regression tests (19 total) authored; 19 pure JS clock/reconciliation assertions passed. Restart/reconnect required.

## Increment 6 — paused iPhone disappears from Spotify Connect

User ran 19 Python tests successfully, then reported controls grey out seconds after Pause until playing on phone. Screenshot confirms historical track and missing target. Retain last confirmed nonrestricted target for up to 300 seconds in memory; if no different active device/restricted match, enable explicit resume to that ID only even when temporarily absent from device list. For unlisted target disable skip/seek/library/shuffle/repeat; verified available target keeps prior resume/skip support. No automatic writes or retries; reject stale/unknown IDs and invalidate unlisted recovery on upstream 403/404 until positive rediscovery. Distinguish last device vs confirmed available; no guarantee Spotify can wake unavailable iPhone. Seven new mocked Python tests (26 total) authored; local runtime and live test pending.

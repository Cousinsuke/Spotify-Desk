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

## Increment 7 — original Desk comparison and diagnostics

Reviewed original desk_ui.py, static/ui.js and static/device.js. Original uses immediate play/pause optimistic feedback, 3.5s override, 7s skip pending, bounded confirmation reads; it also disables transport when no active playback is reported. Ported immediate feedback/rollback and same-device bounded stale response guard, pending skip text, background confirmation reads; preserved existing explicit resume fallback and current library endpoints. Optional DESK_SPOTIFY_DIAGNOSTICS=1 prints fixed player endpoint/status, presence flags, device counts, last-device match/recovery, command and ack only; no IDs, tokens, URLs, titles, artists or payloads. Compare original Wi-Fi playback on port 8888 using same phone (stop other preview while testing). No claim of upstream iPhone fix; capture diagnostic lines if issue persists. 29 pure JS assertions passed; live browser and Python runtime retest pending.

## Increment 8 — live album artwork backgrounds

User ran 26 Python tests and approved Xbox playback; iPhone Connect dropout confirmed by upstream 204/empty device list/404 resume. No playback logic changed in this increment. Adapted original static/ui.js 24x24 saturation/luminance weighted sampler and RGB/HSL helpers to dark, readable background palettes, preserving grayscale artwork. Current artwork only; sample once per image, reuse one in-memory palette, discard stale image callbacks, neutral fallback if CORS/pixel access fails and retry visible cover without CORS. Album colours, dimmed actual artwork, and global theme remain selectable; no real blur, persistent image cache or extra Spotify API calls. Browser/CORS/device performance and user visual review pending. Local unit tests: `node "Echo Show 5 Gen 1/prototype/album-palette.test.js"` and existing Python tests; restart server and reauthorize for live review. No Pi or original root app changes.

## Increment 9 — Weather preview

User visually approved all Spotify background styles. Added isolated synthetic Bournemouth Weather page: large current summary, feels-like/rain today/humidity/sunrise/sunset, 3/5/7-day configurable scrollable cards, colour/outline icons (also Home), static local vector sky with condition CSS variants, tappable day detail overlay with six illustrative hourly values, quick settings and Settings preferences. The displayed values and dates are examples, not forecasts; sunrise/sunset reused for all sample days. Only partly-cloudy background is exercised by fixed current sample; other condition visuals and live weather API/cache remain pending. No real Spotify playback logic changes, no network weather requests. Test browser at 960x480 in both rail states. JS syntax and 13 pure weather assertions passed in assistant runtime; actual browser/gestures pending.

## Increment 10 — current temperature and upcoming hourly forecast

User reviewed screenshots and requested current rather than all-day temperature, upcoming hourly values and better use of expanded forecast bottom space. Main Weather defaults to next 24 hours in a scrollable Hourly strip with Daily toggle preserving 3/5/7-day duration; Today in daily view displays current temperature (Now) and future dates retain forecast high/low. Hour cards open the corresponding day details. Today detail shows current temperature and condition, next 24 hours from next London-local hour including midnight/DST transitions, bottom cards for daily high/low, feels-like, humidity, sunrise/sunset. Future dates show forecast high/low and all actual hourly slots for selected day, bottom daily summary; do not label future temps current or reuse today's current humidity/sun times. All weather values synthetic; no live weather connection. 25 logic assertions and JS syntax checked. Browser visual review pending; no playback changes.

## Increment 11 — live Bournemouth weather

Live mode now uses fixed Bournemouth coordinates from original static/desk-dashboard.js and Open-Meteo current/hourly/daily API. Server refreshes asynchronously, caches 15 minutes, retries failures no faster than 60s, labels stale data, discards data after six hours. Browser polls local cache every 15s on Home/Weather; no direct upstream from browser. Unix timestamps and Europe/London formatting, day/night flag, real sunrise/sunset, current vs daily data. Static mode remains sample. Missing live data does not fall back to sample. Weather source is model-derived forecast, not a station measurement. No changes to Spotify playback or root app. Verify browser and upstream connectivity locally. API docs https://open-meteo.com/en/docs .

## Increment 12 — touch-first forecast navigation

User screenshots confirm live Bournemouth data rendering on the main/expanded views. Replaced Hourly/Daily segmented buttons with compact select matching Spotify, removed all forecast arrows and horizontal scrollbar chrome (including expanded details); native touch swipes remain, longer daily forecasts still scroll, 3-day cards require no arrows. Mouse drag for desktop review with click suppression after dragging; focusable strips also support keyboard arrow keys. Switching forecast type resets position; weather refresh retains strip position. No changes to weather API or Spotify playback. JS syntax and source-level checks passed; desktop drag, native Android touch and actual layout need user review.

## Increment 13 — Glucose layout preview

User approved Weather touch-first layout. Added synthetic-only Glucose LIVE/GRAPH/BOTH views, remembered view preference, 6h/AUTO defaults on reload, equal-height 40/60 cards and compact graph range/scale dropdowns. Original static/glucose-chart.js copied verbatim into isolated prototype, preserving time axis, filtering, gap, 4–7 display band, auto/full scale and extreme behavior. Green/default, global and dynamic display-only backgrounds; sample scenario selector in quick/full settings for visual testing, not persisted. Explicit sample labels and official Libre app footer. No real CGM data, credentials, API transport or changes to existing Spotify/Weather logic. Browser rendering and actual device testing pending. Server restart required for new asset allowlist. Next review UI, then reuse existing Gluroo backend for secure loopback testing before any Pi/Echo transport.

## Increment 14 — live Gluroo loopback integration

User approved all three Glucose layouts. Reuses original root glucose_live.py via same-worktree import; no changes to original reader. Background worker prevents slow upstream CGM from blocking Spotify. Existing 150s minimum poll and daily 429 backoff, HTTPS/no redirect, in-memory cache and 24h source limits retained. Local same-origin GET /api/glucose additionally checks loopback peer; no-store, no secrets/CGM logging, no LAN support. Browser live mode starts empty, never falls back to samples, locally downgrades age >=10 min or cache contact >60s, shows labelled last reading/history when stale, hides stale trend and Home reading, neutral dynamic background when stale, source direction only. Sample mode remains separate; scenario selector hidden in live mode. Local browser polls cache every 15s on Home/Glucose. 15 JS assertions passed; six offline adapter tests authored, Python and actual Gluroo runtime pending. Launch from repo root with local DESK_GLUCOSE_URL and DESK_GLUCOSE_API_SECRET_SHA1 environment variables (existing Gluroo Global Connect URL and 40-character hash, full credential). Never put secrets in Git, URLs, chat, screenshots or command history. Use hidden prompt; retain Spotify Client ID. Do not expose port 8765 on LAN. Compare display with official Libre app; secondary display only. Pi/Echo secure transport separate.

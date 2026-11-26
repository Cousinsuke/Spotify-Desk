# Prototype status — 2026-11-26

Branch: [echo-show/prototype](https://github.com/Cousinsuke/Spotify-Desk/tree/echo-show/prototype)
Latest Spotify preview: [3d8f26b](https://github.com/Cousinsuke/Spotify-Desk/commit/3d8f26b6e8b403205d097808d548c629e15913dd).
First code commit: [fceb865](https://github.com/Cousinsuke/Spotify-Desk/commit/fceb8653d337645ac9df93ec17c162c3b9cd7024).
The first increment is intentionally isolated in Echo Show 5 Gen 1/prototype/; root application, CAD and Pi are unchanged. Main stores design docs.

## Run on Omarchy

From an existing clean checkout (check git status; do not discard user changes):

```bash
cd ~/Projects/Spotify-Desk
git status --short
git fetch origin
git worktree add ~/Projects/Spotify-Desk-Echo-Prototype -b echo-show-preview-local origin/echo-show/prototype
cd ~/Projects/Spotify-Desk-Echo-Prototype
python3 -m http.server 8765 --bind 127.0.0.1 --directory "Echo Show 5 Gen 1/prototype"
```

Use a different worktree path/branch if already present; do not overwrite. Open http://127.0.0.1:8765/ in browser. Use 960 x 480 responsive viewport at 100% zoom if desired. Ctrl+C stops server. To update later, fetch and fast-forward the local preview branch; check status first.

## Implemented in first increment

Home clock and synthetic widgets; right-side rail, default 10s hide and per-page settings, reflow and arrow/edge swipe handlers; Apps drawer; General/Navigation settings shell; top-edge swipe quick settings and click fallback; Graphite/Black, rail styles and opacity, animation options, preview-only dimming, manual night mode, non-sensitive local preference cache and reset. Home on reload.

## Pending/limitations

Source JS parse passed using read-back; branch head verified. User visually approved Home on Omarchy (2026-11-26); HTTP 200 for HTML/CSS/JS, screenshot confirms clock/date, sample tiles and collapsed rail. Favicon 404 was harmless; SVG favicon added in increment 2. Other interactions and Spotify browser tests still pending. No hardware test. Gesture/touch-action and focus/timer behavior require validation, particularly native Android notification shade interactions. Spotify now has a synthetic interactive player; Weather/Glucose/Calendar/System remain planned. No service connection. Spotify contextual quick settings added; other app-specific quick settings, pin/reorder, schedule, full settings, Pi-backed preferences and calendar/system information not implemented. Brightness is CSS dimming only, no hardware backlight or keep-awake integration. No actual CGM readings or credentials, no live network data. No Pi changes.

## First user review

1. Home layout at 960 x 480; clock and sample tiles.
2. Rail hides after 10 seconds when not focused/overlay open; arrow and inward swipe reveal, no automatic page switch.
3. Apps opens right drawer; dismiss outside/close or select Settings.
4. Swipe down from top or click small top handle; theme and preview brightness apply.
5. Settings General/Navigation: opacity, rail style, auto-hide, reset. Reload returns Home.
6. Report layout/interaction problems; do not share private readings or credentials.

## Increment 2 — Spotify

Left artwork, track/artist, simulated play/pause/skip/seek, shuffle/repeat/save, compact Wi-Fi/PC mode selector with Echo disabled pending hardware testing, floating sample device selector, expanded bottom device button and far-right save button (no volume icon), background presets and Spotify quick settings. Pure sample-state module: JS syntax and 17 state assertions passed in assistant JS runtime; browser UI not executed. No real Spotify or audio, no sensitive data. Device switching is simulation only. Home visual approved; other shell tests remain pending. Original checkout had modified static/desk-dashboard.css; preserve it; only update separate preview worktree.

Update existing worktree (do not recreate it):

```bash
cd ~/Projects/Spotify-Desk-Echo-Prototype
git status --short
git pull --ff-only origin echo-show/prototype
```

Refresh existing browser with Ctrl+Shift+R. If server stopped, rerun launch command from preview worktree. Check artwork/control fit with rail expanded/collapsed, mode dropdown, floating device selection/dismissal, play/pause, seek, skip, save/shuffle/repeat, and top-handle Spotify quick settings. Optional local test: `node "Echo Show 5 Gen 1/prototype/spotify-preview.test.js"` if Node installed. Next: Weather layout, then Glucose with existing chart renderer and expanded settings. Pi preflight can run in parallel; do not wipe old data.

## Increment 3 — Spotify refinements and local real-account test

Latest branch commit: [154da1e](https://github.com/Cousinsuke/Spotify-Desk/commit/154da1eb7e4f7364d4c4ec5389d43c6fe8b1a8c4). User screenshot confirms sample Spotify rendering, collapsed rail, and successful static asset responses including favicon. User confirms auto-hide delay works. Requested immediate blank-area dismissal, bare save icon with green tick, neutral mode/device backgrounds; implemented, re-review pending. JS syntax checked; new Python tests authored but not executed by assistant. No actual OAuth or playback tested.

Stop static server with Ctrl+C, update separate worktree, set existing Spotify app redirect URI to http://127.0.0.1:8765/spotify/callback, then run on Omarchy:

```bash
cd ~/Projects/Spotify-Desk-Echo-Prototype
git pull --ff-only origin echo-show/prototype
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements-ui.txt
./.venv/bin/python 'Echo Show 5 Gen 1/prototype/test_live_server.py'
env SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID' ./.venv/bin/python 'Echo Show 5 Gen 1/prototype/live_server.py'
```

Open http://127.0.0.1:8765/?live=1, select Spotify then Connect Spotify; approve in official Spotify authorization page and return to dashboard (Home opens on reload). Start music on an available Spotify device. Test metadata, artwork, device selector and controls. Developer app owner Premium and authorized account required. Do not share client secret, OAuth code, tokens or real account metadata. Current library URI endpoints per Spotify February 2026 migration guide; server uses PKCE, one-time state cookie, tokens in memory, loopback binding, exact host/origin guards, explicit asset allowlist, rate-limit backoff. No LAN or CGM, no production readiness claim. Stopping server clears tokens; live artwork neutral background until real art color extraction implemented. PC/Echo unavailable. Other pages use sample data. Existing static sample preview remains at /; no root app changes.

Sources: https://developer.spotify.com/documentation/web-api/tutorials/code-pkce-flow ; https://developer.spotify.com/documentation/web-api/concepts/redirect_uri ; https://developer.spotify.com/documentation/web-api/tutorials/february-2026-migration-guide . Next verify local account and visual changes, then Weather.

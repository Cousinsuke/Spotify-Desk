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

Latest branch commit: [154da1e](https://github.com/Cousinsuke/Spotify-Desk/commit/154da1eb7e4f7364d4c4ec5389d43c6fe8b1a8c4). User screenshot confirms sample Spotify rendering, collapsed rail, and successful static asset responses including favicon. User confirms auto-hide delay works. Requested immediate blank-area dismissal, bare save icon with green tick, neutral mode/device backgrounds; implemented, re-review pending. JS syntax checked. User ran all 9 mocked Python tests on Omarchy successfully (0.039s, OK), installed dependencies and launched live Flask server on loopback with Client ID. Screenshot shows NOT CONNECTED with Connect Spotify link; OAuth not confirmed. iPhone playback alone does not authorize the dashboard. Next click Connect Spotify, complete same-account authorization, reopen Spotify after returning Home. If still disconnected, report exact error without OAuth codes/tokens or Client ID. No real playback verified.

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

## Increment 4 — real account connection and playback fixes

User confirmed the redirect URI/callback was the initial blocker and reported real Spotify worked before pressing Pause. Screenshot and traceback show a command handler failure at `r.json() if r.content else None`, not an authentication failure. Spotify documents 204 for Pause (https://developer.spotify.com/documentation/web-api/reference/pause-a-users-playback); exact received status/body was not logged. Fix: ignore successful write acknowledgements regardless of body, handle 204/empty reads, report malformed GET JSON as controlled error, retain error handling for rejected writes, invalidate playback cache on commands. Browser distinguishes HTTP errors from absent server. Added monotonic playback clock using actual progress_ms snapshot, local 200ms UI refresh (elapsed display in whole seconds), 5s API poll unchanged, clamp to duration and 15s extrapolation cap, freeze on pause/disconnect/pending commands and during seek drag, discard superseded polls before command and refresh after. No new audio/API mode.

Branch commit [eeaea4d](https://github.com/Cousinsuke/Spotify-Desk/commit/eeaea4d023d508d391513c2cd12feb1aaa2fe433). JS syntax and ten pure clock assertions passed in assistant runtime. Four new mocked Python regression tests authored (13 total), not yet run. User must stop current Flask with Ctrl+C, fast-forward separate preview worktree, run tests, restart with existing Client ID locally, reauthorize (tokens memory-only) using already-correct callback, and hard refresh live URL. Test pause/resume, next/previous, seek, external changes and timer. Actual fixed playback behavior not yet validated; real artwork colour extraction, Pi integration, PC/Echo and Weather/Glucose remain pending. No personal identifiers/tokens/readings saved.

## Increment 5 — playback confirmation and device recovery

User ran all 13 Python tests successfully (0.010s), confirmed Pause reached iPhone but browser lagged; Previous then displayed active-device unavailable and no active playback. Exact upstream state not logged. Preview commit ae6b0c2750cdad8b38a241b82be164b9b7252a39: explicit requested play/pause state, acknowledged local state, bounded post-command confirmation reads (250/650/1300ms waits), one retained historical track labelled inactive, fresh same-device availability checks for resume/skip; never silently target another active device or retry writes. Regular 5s polling retained. Six more Python tests authored (19 total); 19 pure JS assertions passed. Actual live retest and new Python tests pending. Restart/reconnect required; if phone is absent from device list, open Spotify on it and manually select it. No private data committed.

## Increment 6 — paused-device resume fallback

User ran 19 Python tests successfully (0.012s) and reported Pause greys out all transport controls after seconds until manually playing on iPhone. Screenshot shows retained last track, no active playback, device selector without selected device. Upstream device list/status not captured; suspected Connect dropout. Code 861ccf502bc2c224796544618de97491527f2ac8: remember last confirmed unrestricted device ID in memory for five minutes; when no active playback and same device absent from list, allow explicit Resume only, with fresh check for other active/restricted devices and bounded age. Do not auto-transfer, retry writes or allow unverified skip/seek/library actions. If resume gets 403/404, disable unlisted recovery until positive rediscovery. Distinguish last device from verified device; no guarantee Spotify can wake phone. Seven additional Python tests authored (26 total), JS syntax passed; Python runtime and live retest pending. Test with phone Spotify foreground then screen locked, wait 10–15 seconds after pause, attempt Play and inspect device drawer/error. If still unavailable, compare PC playback and collect redacted diagnostics before further code changes. Spotify docs: https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices and https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback . No account identifiers or real track data saved.

## Increment 7 — original player comparison and diagnostic checkpoint

User reported the latest paused-device fallback still behaves incorrectly and asked to review the original Spotify Desk code. Reviewed main desk_ui.py (_wifi_execute, playback_state, cache), static/ui.js (optimisticUpdate, showState, skip feedback/verification), static/device.js. Original uses Spotipy, immediate optimistic UI, 3500ms same-device play override, 7000ms pending skip, bounded confirmation checks and 5s poll; original also disables controls on no active playback and rejects commands without active device, so it cannot establish that iPhone dropout is fixed. Main README identifies 7172c2e as last user-accepted playback baseline. Code fa7c091c93aff77efe856ccfacda644a850f5450: port original optimistic feedback/rollback, bounded stale same-device response hold, skip text/freeze, release write lock after acknowledgement and schedule bounded read-only confirmations. Preserve explicit device selection, current library endpoints and last-device resume fallback. Added opt-in DESK_SPOTIFY_DIAGNOSTICS=1 for fixed endpoint/status, player presence/playing/device flags, device counts/match and recovery, command/ack; no IDs, track metadata, tokens, request bodies or authorization URLs. 29 JS assertions passed and syntax checked; Python/runtime/live retest pending; user did not report a result for 26 Python tests. Compare original on same iPhone in Wi-Fi mode at loopback port 8888, not PC mode; close/stop other preview to avoid competing polls. Original app can use existing configured Client ID or local environment and existing redirect URI (do not change/remove it). Run new preview with diagnostics enabled, pause 15s, try resume; capture [spotify-diag] lines only if still failing. No further speculative device policy changes until actual diagnostics or A/B evidence. No private identifiers committed.

## Increment 7 — diagnostic conclusion and Xbox acceptance

User ran all 26 Python regression tests on Omarchy (0.015s, OK) at prototype commit fa7c091. Redacted diagnostics establish that Pause succeeded (HTTP 200), paused state was confirmed (200), then Spotify playback endpoint returned 204 and available devices returned an empty list; explicit resume against the remembered device returned 404 and recovery was correctly blocked until playback was rediscovered. Subsequent playback/skip/device commands were accepted. User also ran original Spotify Desk Wi-Fi comparison and concluded the iPhone drops out; reported Xbox playback works perfectly and accepted moving past iPhone troubleshooting since it is not a target use case. This is evidence of Spotify Connect device unavailability in this test, not proof of the underlying iOS cause or universal device behavior. Keep current recovery safeguards, no additional speculative changes. Xbox user-reported pass; individual control coverage, Pi with PC off, and physical Echo hardware remain unverified. Next implement actual album-art-derived background colors using the existing Desk color extraction as reference, then Weather and Glucose. No code changes, no raw logs, identifiers, pairing codes or credentials committed.

## Increment 8 — real album artwork backgrounds

Prototype commit b7cb354df0779c58a879d3c4f2e728003ab65425: real Spotify cover-derived background, adapted original static/ui.js RGB/HSL and 24x24 saturation/luminance weighted pixel sampler. Darken palette for readability, preserve neutral artwork, one in-memory palette, reuse same artwork, discard stale async callbacks, reset on missing art; if cross-origin pixel access fails, neutral fallback and regular cover display. Existing three background preferences: Album colours (default), Dimmed album artwork (actual static cover with dark overlay in live mode), Global theme (Graphite/Black). No blur, persistent art cache, new Spotify API requests or playback-control changes. JS syntax and 23 pure/mocked palette assertions passed in assistant runtime (colour, contrast examples, URL allowlist, race, CORS fallback and cache). Actual browser/Spotify CDN CORS, user appearance approval and Echo performance pending. Run existing 26 Python tests and optional node album-palette.test.js, restart server and reauthorize; test on Xbox by skipping between distinct covers and changing Background in Spotify quick settings. If colours stay neutral for colourful art, investigate CDN CORS in browser before changing architecture. Preserve original checkout and accepted playback baseline. Next Weather after visual review. No credentials or personal artwork committed.

## Increment 9 — Spotify visual acceptance and Weather prototype

User reported testing the Spotify update and approving all three background styles. Preserve accepted Xbox playback and visual baseline. Prototype commit dc4c64be75a3d2fb9345b7dbbdfc6338917a2e0c: added synthetic Bournemouth Weather page with large current temperature/condition, feels-like, rain today, humidity, sunrise/sunset; default 3-day forecast with 5/7 options, horizontal scroll and arrow buttons, two icon styles (colour/outline), small Home weather icon, static local vector sky and condition CSS variants, selectable forecast cards opening hourly-detail overlay, Weather quick settings and Settings category. Data is explicitly sample, including daily labels and shared sample sunrise/sunset; no live weather API or cache yet. Only partly cloudy is exercised by fixed sample, remaining condition visuals and final assets need review. 13 pure JS assertions and syntax passed in assistant runtime; actual browser layout, scrolling, gesture and device tests pending. No changes to Spotify playback code or Pi. Next review Weather at 960x480 with both rail states, longer forecasts, icon styles, details/dismissal, then implement actual Open-Meteo feed using original integration and proceed to Glucose. No real readings, account information or credentials committed.

## Increment 10 — Weather refinements

User reviewed main and expanded Weather screenshots; requested current temperature instead of whole-day high/low, upcoming hourly values instead of past times, and better use of lower detail panel space. Prototype commit a13de889afef229a0021db8ddb0cb05a7e915657: main Weather now defaults to scrollable next 24 hours with Hourly/Daily toggle (preserves configured 3/5/7 days). Today card in Daily shows current temperature and Now label; future dates retain high/low. Today's expanded summary shows current temperature/condition and next 24 hours, with bottom cards for daily high/low, feels-like, humidity, sunrise/sunset. Future date details show forecast high/low, selected day's hourly slots and daily summary; no current conditions attributed to future dates. Hour cards open corresponding day detail; arrows and touch scrolling. London-local date/hour labels handle midnight and daylight-saving changes; values still synthetic, not live. Hourly default/toggle, card details and 24-hour horizon are implementation choices for user review. JS syntax and 25 logic assertions passed including midnight and DST; browser layout and real weather integration pending. No Spotify playback changes. Next visual review, then connect original Open-Meteo integration.

## Increment 11 — real Bournemouth weather

User reported Weather displayed 10°C at 00:06 whereas their reference was 6°C, with night screenshot showing sunny icons. Explained sample-only data, not actual readings. Prototype commit c68531d272f8befe42e989b977236de3b883581c: live mode now fetches Open-Meteo at fixed original Bournemouth coordinates 50.72098,-1.87669, current temperature/apparent temperature/humidity/weather code/is_day, hourly temperature/rain probability/code/is_day, daily high/low/rain/sunrise/sunset. Asynchronous server refresh outside Spotify request thread, 15-minute cache, 60s failure retry limit, stale label and 6h maximum cache age, same-origin local API, no synthetic fallback in live mode. Browser uses London-local time and current/day-night icons, upcoming hours and future day details; Home uses same source. Static mode remains illustrative. Open-Meteo provides model-based current estimates and forecasts, not exact weather station observations; user's reported 6°C not independently verified. JS syntax and 14 live data mapping assertions passed using synthetic fixtures. Python runtime, real API connectivity, browser layout/freshness and Pi deployment not tested. No changes to Spotify playback logic; no private data committed. Next user update/restart, inspect current/hourly/night weather and compare with their weather app, then Glucose. API docs https://open-meteo.com/en/docs .

## Increment 12 — touch-first Weather controls

User screenshots confirm Open-Meteo live data rendering in daily, hourly and expanded Weather views, including current and upcoming temperatures. User requested removal of unused 3-day arrows, all hourly/detail scroll arrows and visible horizontal scrollbars, and a Spotify-style Hourly/Daily dropdown. Prototype commit ada89b8c6b01a8ea375e46ae35fd1fe9d9674431: compact native select in forecast header; no forecast arrows in any duration or expanded view; hide scrollbar chrome while retaining native touch pan/momentum and longer daily forecast scrolling. Added mouse drag for desktop review with movement threshold and post-drag click suppression, keyboard arrow scrolling on focused strips. Forecast mode switch resets position; data refresh retains main/detail scroll position. No API, Spotify or Pi changes. JavaScript syntax and nine source-level checks passed; native touch, mouse drag, card taps and actual layout still need user validation. No actual forecast values or screenshots committed. Next review touch-first Weather UI, then Glucose.

## Increment 13 — Weather approval and Glucose preview

User approved revised Weather appearance after touch-first changes; actual Echo touchscreen, cache expiry and individual long forecast gestures remain unverified. Prototype commit b2e51a45c4cab513d2a77b7b2a6b0848c747a39a: synthetic-only Glucose UI follows final agreed layout: no redundant headings, top-right LIVE/GRAPH/BOTH dropdown, aligned equal-height reading/graph cards at 40/60 widths, graph duration (1/3/6/12/24h) and AUTO/FULL dropdowns, default green, optional global and dynamic display-only backgrounds, Home sample tile and Glucose quick/full settings. Copied original static/glucose-chart.js verbatim, preserving existing timestamp filtering, deduplication, 20-minute gaps, local time axis, 4–7 display band, latest dot and scale rules. View preference saved; 6h/AUTO reset on reload. Added explicitly synthetic sample scenarios to review colours (low/red, in-band/green, above-band/yellow-orange, 15+/orange); sample scenario not persisted. Colours are aesthetic, not clinical categories. No live CGM or credentials, no medical guidance, no persisted readings; official Libre app remains authoritative. 27 pure JS assertions and syntax passed; browser layout and device testing pending. Restart local Flask server after pull to serve new assets, reauthorize Spotify if needed, test three views, duration/scale and dynamic background scenarios. Next visual review before adapting existing glucose_live.py for loopback-only testing. No changes to original root application, Spotify playback or weather API. No Pi or physical hardware work.

## Increment 14 — Glucose approval and live local integration

User screenshots and explicit approval confirm LIVE/GRAPH/BOTH Glucose appearance accepted, requested real feed. Prototype commit a5fb75e0b24b92d5ab02920bfc2a196bb860fab5: import original root glucose_live.py from isolated worktree without modifying it; separate asynchronous worker, existing 150s upstream minimum, 429 daily backoff, HTTPS/no redirect, in-memory readings, 24h history. GET /api/glucose protected by existing exact host/header/same-origin policy plus loopback peer check, no-store; no LAN access. Browser live mode starts empty, no sample fallback, uses validated source trend only, labels stale and hides stale Home value and trend, neutral dynamic colour on stale/offline, expires live at source age 600s or no local contact for 60s. Sample scenario removed from live settings. Layout and graph renderer preserved. 15 JS assertions and syntax passed; six mocked Python adapter/route tests authored but not executed by assistant; actual Gluroo connection not verified. No account data, secrets, screenshots or real CGM values committed. User should stop server, pull prototype, run test_glucose_service.py and existing test_live_server.py, then start server using hidden local prompts for existing Gluroo Global Connect HTTPS base URL and API Secret Header SHA-1 (40 hex characters, full read/write credential), plus Spotify Client ID. No need to reconnect LibreLinkUp/Gluroo if existing sharing still works. Open loopback live URL and compare value/timestamp/trend with official app, report status only. No treatment use; Pi/Echo authenticated encrypted transport remains pending. No changes to root application or Spotify/Weather logic.

### Omarchy local launch (after stopping the old server)
```bash
cd ~/Projects/Spotify-Desk-Echo-Prototype
git pull --ff-only origin echo-show/prototype
./.venv/bin/python "Echo Show 5 Gen 1/prototype/test_glucose_service.py"
./.venv/bin/python "Echo Show 5 Gen 1/prototype/test_live_server.py"
bash -c '
read -rp "Spotify Client ID: " SPOTIPY_CLIENT_ID
read -rsp "Gluroo Nightscout URL: " DESK_GLUCOSE_URL; echo
read -rsp "Gluroo API Secret Header SHA-1: " DESK_GLUCOSE_API_SECRET_SHA1; echo
export SPOTIPY_CLIENT_ID DESK_GLUCOSE_URL DESK_GLUCOSE_API_SECRET_SHA1
exec ./.venv/bin/python "Echo Show 5 Gen 1/prototype/live_server.py"
'
```
Open http://127.0.0.1:8765/?live=1 and hard refresh; reconnect Spotify if desired. Prompts do not echo Gluroo values or put them in command history. Keep server local only, do not share secrets or actual readings. Stop server to clear its in-memory cache and process environment.

## Increment 15 — Dynamic Glucose colour refinement

User screenshots confirmed real Gluroo feed rendered on BOTH and GRAPH views and requested reference-style saturated yellow/amber and orange, plus removal of residual green in dynamic mode. Prototype commit fa8e8602d4cc181509a32acb88bf14854703d2c3: existing display thresholds already correct and unchanged (below 4 red, 4–7 green, above 7 and below 15 amber, 15+ orange, stale/offline neutral). Replaced hardcoded green graph gradient with per-theme variables; themed graph traces, labels, grid, dot, shaded display band, cards, controls and status. Amber card #ffbb00 with dark text; high card #c24b00 slightly darkened from reference orange for white text contrast. Darker outer backgrounds preserve existing visual hierarchy. Global theme and stale use neutral colours. Chart geometry, values, history and scaling unchanged. 39 JS assertions passed, four representative amber/orange text contrast checks >=4.5:1. Browser visual review and all real state transitions pending; live feed rendering observed but Python adapter test result and accuracy comparison not reported. Frontend-only pull and hard refresh, no restart or reauthorization. No real readings, screenshots, credentials or account identifiers saved to GitHub. Next user visual approval then Settings; Pi/Echo secure transport still pending.

## Increment 16 — Independent glucose graph, card and background

User requested readable white graph instead of bright amber graph, retaining colour on the live reading, adding status colour to Home glucose tile, and separating global page themes from glucose data colours. Prototype commit 44b78cb5229a8b1257fc6226f56e8db5e1defbff: fixed graphite chart panel with white trace, dot, labels, neutral grid and shaded 4–7 display band; live reading card and Home glucose tile share reading-status palette independent of page background preference. Green, Dynamic and Global theme preferences only change the glucose page backdrop; Dynamic follows fresh reading, Global theme follows Graphite/Black. Home wallpaper and other tiles unchanged. Stale/unavailable status uses neutral card/tile and hides Home reading; existing freshness checks and thresholds unchanged. Design choice: use a consistently dark graph panel to ensure white trace readability in every theme. 27 source-level assertions and JavaScript syntax passed; browser rendering and all status transitions pending user review. No chart geometry, live reader, credentials, polling or Spotify/Weather changes. Frontend-only pull and hard refresh. No actual readings/screenshots committed.


## Increment 17 — App shortcuts and ordering (2026-11-27)

Prototype commit [7f4d9ea](https://github.com/Cousinsuke/Spotify-Desk/commit/7f4d9ea72483809f1b657f046559d9f1c64b8992): Settings > Apps supports pin/unpin and up/down ordering. Home and Apps remain fixed; at most three optional rail pins, retaining original default Spotify/Weather/Glucose order. Drawer lists all four enabled destinations (Spotify, Weather, Glucose, Settings), including unpinned apps; Calendar/System Information hidden until implemented. The same order controls drawer and pinned rail entries. Existing non-sensitive local preference key retained; missing/malformed preferences normalized, duplicates and unknown/disabled IDs discarded, reset restores defaults and redraws rail. Touch-friendly move buttons and focus/scroll restoration; no drag-and-drop. These exact UI choices are proposed for review, not yet user-approved. JavaScript parsed; 23 pure-state/source assertions passed using assistant JS runtime with mocked Node assertion/file interfaces. Native Node/browser/Android execution not performed; test added at prototype/app-shortcuts.test.js. GitHub compare confirmed only four prototype files changed, no original root, CAD, service, playback, weather or glucose changes. Frontend-only pull and hard refresh; no server restart or OAuth needed. Previous glucose palette review still pending; no new live-data tests or hardware work. Pi preflight remains pending.

Next: user review of independent Glucose palettes and Settings > Apps (pin/unpin, order, full limit, drawer accessibility, reload, reset at 960x480). Then extend General/Home settings and scheduled night mode in separate increments; Pi read-only preflight remains independent. Preserve iPhone Connect limitation and accepted Xbox baseline; no real data over LAN before authenticated HTTPS.

```bash
cd ~/Projects/Spotify-Desk-Echo-Prototype
git status --short
git pull --ff-only origin echo-show/prototype
node "Echo Show 5 Gen 1/prototype/app-shortcuts.test.js"
```
Hard refresh the existing browser. If Node is unavailable, the browser can still be reviewed; report that the automated local test was not run. Use static sample mode `/` for range-colour review if desired; do not share real glucose values or screenshots containing private data.


## Local one-command launcher (2026-11-27)

User requested one-command launch rather than re-entering Spotify Client ID, Gluroo URL and API Secret Header SHA-1 at every restart. Prototype commit [0271c7a](https://github.com/Cousinsuke/Spotify-Desk/commit/0271c7acee9a10170380ebc81043aca7cf6c0e5f) adds executable prototype/start-live, blank .env.example, offline regression test and launch documentation. On Omarchy/Linux first run prompts locally with hidden input, validates required values and creates owner-only mode 600 prototype/.env; subsequent runs parse literal key/value data (no shell evaluation), reuse credentials, and exec existing .venv Python live_server.py. Reject duplicate/unknown settings, insecure permissions, symlinks and malformed HTTPS/hash values. Existing root .gitignore already excludes .env at all levels; real credentials never committed. Local plaintext file, not encrypted; do not share or force-add it. No new dependencies or API/port/security-policy changes. 14 synthetic assertions passed in assistant Linux runtime (parsing, bad configuration, permissions, symlink and mocked first-run creation); real credential launch pending user test. Spotify OAuth tokens remain memory-only and reauthorization after restart is unchanged. Pi storage/deployment remains separate.

```bash
cd ~/Projects/Spotify-Desk-Echo-Prototype
git status --short
git pull --ff-only origin echo-show/prototype
./"Echo Show 5 Gen 1/prototype/start-live"
```
Stop any running preview server with Ctrl+C first. First launch prompts once; subsequent launches run the last command without re-entering credentials. Edit locally if needed with `nano "Echo Show 5 Gen 1/prototype/.env"`. Open http://127.0.0.1:8765/?live=1 and reconnect Spotify if needed. Optional test: `python3 "Echo Show 5 Gen 1/prototype/test_start_live.py"`.

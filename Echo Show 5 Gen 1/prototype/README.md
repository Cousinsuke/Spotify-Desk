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

## Increment 15 — dynamic Glucose colour refinement

User confirmed real feed rendered in BOTH and GRAPH and requested vivid yellow/amber and orange matching reference colours, with no leftover green. Existing thresholds unchanged (below 4 red, 4–7 green, above 7 to below 15 amber, 15+ orange), stale remains neutral. Removed hardcoded green graph gradient; scoped complete card, chart, status and control palettes to each theme, including neutral global mode. Amber uses saturated yellow cards with dark text; orange uses saturated orange darkened slightly for readable white text; outer backgrounds darker for contrast. SVG classes allow the original chart geometry and 4–7 shaded band to remain unchanged while tinting its rendering. No live reader or playback changes, no private data committed. Frontend-only update: pull and hard refresh; no server restart or reauthorization. Browser appearance and all colour transitions pending review.

## Increment 16 — independent glucose card, chart and page background

User requested a white graph, Home glucose tile status colour, and global themes affecting only surrounding background. Chart now uses a fixed dark graphite panel with white trace/dot/axis labels and a neutral shaded 4–7 display band in all modes. Live reading card and Home tile share the status palette regardless of background preference; stale/unavailable remain neutral and Home hides the reading. Green, Dynamic and Global theme select only the Glucose page backdrop; dynamic follows fresh source status. Home page wallpaper unchanged. No graph geometry, data transport, threshold or polling changes. JS syntax and 27 source assertions passed; actual browser rendering and status transitions pending. Frontend only; pull and hard refresh.


## Increment 17 — app shortcuts and ordering (2026-11-27)

Settings > Apps lets you pin up to three enabled apps and move them up/down. Home and Apps stay fixed; the drawer lists all enabled apps, including unpinned ones. Calendar and System Information are hidden until implemented. Existing default pins and order retained; validated non-sensitive preferences migrate in place, persist locally and reset with preview preferences. No Pi storage yet. Touch and keyboard controls, local persistence and actual layout need browser review. Run `node "Echo Show 5 Gen 1/prototype/app-shortcuts.test.js"` from repo root. Frontend-only pull and hard refresh; no new asset served, no restart or reauthorization. No playback, weather, glucose or root app changes.


## Local one-command launcher (2026-11-27)

On Omarchy/Linux, stop any running preview server (Ctrl+C), then from the preview worktree root run:

```bash
./"Echo Show 5 Gen 1/prototype/start-live"
```

First launch asks for the Spotify Client ID, Gluroo HTTPS base URL and 40-hex API Secret Header SHA-1 using hidden input, then creates `prototype/.env` with mode 600 and starts the existing loopback server using the existing root .venv. Subsequent launches reuse the file without prompts. The root .gitignore already excludes .env at every level; only .env.example is tracked. To change values locally use `nano "Echo Show 5 Gen 1/prototype/.env"`, keeping literal unquoted KEY=value lines; never force-add or share the real file. Local plaintext secrets protected by owner-only file permissions, not encryption. Do not copy them to Git or chat. Spotify OAuth tokens remain memory-only: reauthorize after a server restart as before. No new dependencies or changes to live_server.py, existing port or LAN security. Offline test: `python3 "Echo Show 5 Gen 1/prototype/test_start_live.py"`. 14 synthetic checks passed in assistant Linux runtime; actual startup with user's credentials pending.


## Settings touch scrolling (2026-11-27)

Hidden scrollbar chrome in the Settings category list, detail pane and quick settings overlay, while retaining native vertical overflow, touch swipes and mouse-wheel scrolling. Category buttons retain their size instead of shrinking. No JavaScript gesture changes or new runtime dependencies. Nine source assertions passed in assistant JS runtime; actual browser and Echo touch scrolling need review. Optional local test: `node "Echo Show 5 Gen 1/prototype/settings-scroll.test.js"`. Pull and hard refresh; no server restart needed.


## Persistent Spotify authorization (2026-11-27)

User approved Settings scrolling and requested no repeated Spotify consent on every launch. After updating, stop/restart via start-live, open live preview, connect and approve once. Server saves only refresh token plus client ID/scope binding in ignored owner-only mode-600 prototype/.spotify_token.json, atomically, with no browser exposure. Access token stays in memory; subsequent launches restore the refresh token and exchange it on first Spotify request; rotated refresh tokens saved, transient failures retain credential and retry no faster than 30s, invalid_grant removes cache and asks to reconnect. Spotify's current documented refresh token lifetime is six months from authorization (not extended by refreshing); revocation and changed client/scopes require new consent. No command write retries, no changes to playback/device policy or Gluroo. Local plaintext credential, not encrypted; remove the local file with server stopped to forget local authorization (revoke via Spotify account app permissions for upstream revocation). Eight offline tests added (34 total); execution pending user runtime. See https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens and https://developer.spotify.com/blog/2026-06-18-refresh-token-expiration .


## Increment 18 — Home customization (2026-11-27)

Home settings and Home quick settings now offer three fixed layouts (existing clock + widgets default, clock only, split dashboard), four clock styles (thin default, bold, split digits, analogue) and five lightweight CSS wallpapers (original abstract default, ocean, dusk, forest, global theme). Options are validated and persisted in existing local non-sensitive preferences; global reset restores the original layout. Clock-only hides summary tiles without changing background polling; one active clock and layout, no new assets or dependencies. Home preview button in Settings; live quick changes apply immediately. The analogue hands update at minute resolution; no seconds animation. Custom image upload, scheduled wallpaper and dynamic layout remain optional later work. 22 pure/source assertions passed in assistant JS runtime; browser visual/interaction and hardware performance pending. No server changes; pull and hard refresh. Optional test: `node "Echo Show 5 Gen 1/prototype/home-customization.test.js"`.


## Home tile transparency refinement (2026-11-27)

User approved Home presets and requested the neutral Spotify/Weather summary tiles match sidebar transparency rather than green-tinted cards. Shared CSS surface variable now drives rail and neutral Home tiles, including rail opacity and Transparent rail style. Neutral label text and transparent tile border; Glucose status background, border and text overrides unchanged. 16 source checks passed in assistant JS runtime; visual review pending. No JS or server changes. Pull and hard refresh. Optional `node "Echo Show 5 Gen 1/prototype/home-surfaces.test.js"`.


## Scheduled night mode (2026-11-27)

User approved matched Home tile/rail transparency. General and Home quick settings now support Off (default), Manual and Scheduled night mode, configurable local start/end (22:00–07:00 default) and 10–70% visual dimming (55% default, matching earlier manual preview). Overnight and same-day windows, inclusive start/exclusive end, equal times disable schedule with status note. Existing manual brightness remains independent: stronger dim wins rather than compounding; no page switch, sleep, new polling or hardware backlight claims. Local preferences persist/reset, automatic status checked by existing second timer and on visibility return. 32 pure/source checks and JS syntax passed in assistant runtime; actual browser time controls, schedule transition, readability and Android backlight/always-on remain pending. Pull and hard refresh; no restart. Optional `node "Echo Show 5 Gen 1/prototype/night-mode.test.js"`.


## Apple Calendar preview (2026-11-27)

User selected Apple/iCloud Calendar. Calendar is now available in Apps and can be pinned (existing default pins unchanged). Local month navigation, Monday-first 42-cell grid, current/selected date, Today button and split agenda. Static sample mode shows explicitly labelled fabricated events; live mode shows iCloud not connected with no fabricated events. No Apple API calls or credentials yet. Planned private authenticated CalDAV read-only connection using Apple app-specific password, no public calendar URL. Browser and real sync untested. JS syntax, 15 date/source checks and 23 updated app shortcut checks passed in assistant JS runtime. Pull and hard refresh, no server restart. Optional `node "Echo Show 5 Gen 1/prototype/calendar.test.js"`.


## Optional Apple Calendar credentials (2026-11-27)

User has generated an Apple app-specific password. The existing private `prototype/.env` can now accept two optional literal lines: `DESK_ICLOUD_USERNAME=` (Apple Account sign-in identifier) and `DESK_ICLOUD_APP_PASSWORD=` (generated four-group app-specific password). Both must be filled or both blank/absent; old three-key configs and first-run setup remain valid. Edit locally using `nano "Echo Show 5 Gen 1/prototype/.env"`, retain mode 600 and never share/commit credentials. The launcher passes the optional pair to the server without shell evaluation or output. Actual CalDAV synchronization is NOT implemented yet; saving credentials does not connect the Calendar page. No main Apple Account password. Six additional synthetic configuration checks authored in test_start_live.py, runtime pending. No new dependencies or changes to existing services.


## Live Apple Calendar (2026-11-27)

Private CalDAV read-only adapter implemented. Install optional dependencies using `.venv/bin/python -m pip install -r "Echo Show 5 Gen 1/prototype/requirements-calendar.txt"` then restart `start-live` with existing .env. Queries authenticated TLS iCloud hosts only, discovers VEVENT calendars, reads bounded 56-day visible-month/upcoming range, expands recurrence with library, renders Europe/London times and all-day/multi-day events; displays all accessible iCloud event calendars initially, no writes. Event titles/time/date only, escaped DOM text, memory-only cache for up to three months, five minute refresh; no private logs, static samples excluded from live mode. Server returns loading/config/error/refreshing status. Actual Apple account, protocol interoperability, Python dependencies and browser not tested by assistant; user validation required. Optional dependency failures do not block other apps. No existing credentials changed.


## iCloud empty-calendar diagnosis (2026-11-27)

User reported Connected but no events, while iPhone shows subscriptions/events. Discovery now merges successful propstats per DAV response, accepts HTTP status lines without reason phrase, counts collections, subscription collections, readable VEVENT calendars, REPORT resources, calendar-data payloads and occurrences, flags embedded access/server errors, and distinguishes authentication without calendars from successful empty date range. Counts only, no names/URLs/IDs/secrets in diagnostic output. UI shows calendar count and event-day count. Use the local endpoint filtered to status/counts (not raw events) for troubleshooting. iPhone may include other providers or local/subscribed calendars; compare private iCloud.com Calendar and iPhone Calendar list, optionally create one harmless iCloud event to isolate. No subscription fetching yet. JS syntax verified; two extra Python regression methods authored, unexecuted. Exact cause pending counts and source comparison.


## Public Calendar direction (2026-11-27)

User clarified personal calendar events are not used; only UK holidays/observances and F1 are required. Live `/api/calendar` now uses public_calendar_service.py, not private CalDAV. Apple adapter retained inactive for possible future opt-in; no Apple credentials sent or required for Calendar. GOV.UK England/Wales bank holidays JSON (https://www.gov.uk/bank-holidays), curated UK observances (including Bonfire Night, Remembrance, Mothering Sunday, Easter Sunday, Father’s Day), and F1Calendar.com community schedule (https://github.com/sportstimes/f1, MIT, year-specific JSON) fetched without credentials; F1 sessions, location and UK time, independent source status, colour-coded dots and agenda, asynchronous hour cache and retry on failure. F1 is unofficial; year coverage depends on upstream availability. No new dependencies. User may revoke Apple app-specific password and remove optional local keys; do not share .env. JS syntax passed; Python fixture tests authored but not run, actual feeds/browser pending. Pull and restart. Optional `.venv/bin/python "Echo Show 5 Gen 1/prototype/test_public_calendar.py"`.


## Calendar month swipe (2026-11-27)

User approved public Calendar direction and requested vertical swipe navigation. Swipe up on the month grid for next month, down for previous month; mouse drag also supported. One month per deliberate gesture, 48px vertical threshold and vertical dominance, accidental date clicks suppressed, horizontal drags do not change month, cancelled gestures discarded. Existing Today/arrows and day taps remain; agenda keeps native vertical scrolling, quick settings/rail unaffected. No server changes. 28 Calendar pure/source checks and JS syntax passed in assistant JS runtime; actual touch/mouse/browser review pending. Pull and hard refresh.


## System Information — combined dashboard (2026-11-27)

User selected option C. System Information enabled in Apps and pin registry; default pins unchanged. Server panel shows OS/architecture, Pi model if detected, CPU usage/logical CPUs, RAM, project-volume storage, recognized CPU temperature, host uptime and network-link state. Service panel reports dashboard, Spotify (last playback probe, idle is connected), Weather, Glucose freshness and Calendar status; no event contents or glucose readings included. Local-only read-only /api/system, standard Linux proc/sys files, no privileged operations/new dependency. Refresh every five seconds while visible; sample mode labelled. Metrics belong to server host, not Echo; display reports browser CSS size only. JS syntax and 12 System plus 23 shortcut checks passed in assistant JS runtime; four offline Python methods authored not executed; browser/Linux readings and actual Pi/Echo pending. Pull, restart, hard refresh.


## Pi production startup (2026-11-27)

User confirmed live Pi System Information: four cores, low CPU, RAM 36%, 35 C, all service rows healthy (Spotify idle). Snapshot only, not a stress test. Nextcloud left running, no need to stop at present. Add optional Waitress production mode (single request worker to preserve Spotify state, same loopback port, private launcher and refresh cache, no proxy trust, bounded requests/connections), and an unprivileged systemd user unit. No changes to browser, data credentials or LAN security boundary. See https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html. Install requirements-production.txt into existing venv before tests. Stop manual preview before starting service. Commands on Pi:

```bash
cd ~/Projects/Spotify-Desk-Echo-Prototype
git pull --ff-only origin echo-show/prototype
./.venv/bin/python -m pip install -r "Echo Show 5 Gen 1/prototype/requirements-production.txt"
./.venv/bin/python -m unittest discover -s "Echo Show 5 Gen 1/prototype" -p "test_*.py" -v
mkdir -p ~/.config/systemd/user
install -m 644 "Echo Show 5 Gen 1/prototype/spotify-desk.service" ~/.config/systemd/user/spotify-desk.service
systemctl --user daemon-reload
systemctl --user enable --now spotify-desk.service
loginctl enable-linger "$USER"
systemctl --user status spotify-desk.service --no-pager
loginctl show-user "$USER" -p Linger
```

If linger authorization denied, keep service enabled but do not claim boot startup; resolve through existing authorized Pi administration before reboot. Verify loopback with ss and browser through existing SSH tunnel; close manual launch shell, test service restart, confirm Spotify restored; boot verification separate. Rollback systemctl --user disable --now spotify-desk.service; original start-live still works. No Nextcloud or disk modifications, no sudo needed for service installation (linger may require privilege), no credentials in unit. Three Python startup tests authored, not run by assistant; Pi test and boot verification pending.


## Secure device access stage 1 — sample-only HTTPS (2026-11-27)

Pi reboot and loopback service recovery verified. Separate device_gateway.py is deliberately NOT a proxy and never imports live_server or any data adapters. Only static sample UI routes are allowed; query strings on index redirect to sample root; API/OAuth/source/secrets denied even for paired devices. Explicit private IPv4 LAN bind on 8443, allowed /24 or narrower peer subnet, exact HTTPS host and origin, no forwarded trust. Gunicorn TLS, one worker/two threads, bounded requests, no access logs. Owner-only state outside repository in ~/.local/share/spotify-desk-device; OpenSSL local CA and IP SAN server certificate (365 days), signing key removed after issuance, only public ca.crt is copied to client. Certificate renewal/reissue requires explicit new trust; never click through warnings. Private key never copied. Pairing code 16 hex characters, expires in ten minutes, one use, eight failed attempts max; session cookie Secure/HttpOnly/SameSite Strict, 30 days, eight devices maximum, hashes only in SQLite and local revocation. Use separate user unit manually started for first test (not enabled); loopback 8765 and OAuth unchanged. No router forwarding. No live values or controls accessible over LAN at this stage.

Pi: install requirements-device.txt, run unittest discovery (expected 68 tests plus launcher assertions), initialize with actual Ethernet IPv4 and /24, run device_gateway.py serve or install/start spotify-desk-device.service without enabling. Copy ONLY public ca.crt by SSH, compare SHA256 fingerprint, verify TLS via curl --cacert (no -k), import verified CA into test browser authority trust, then pair with freshly generated code from Pi. Verify unpaired asset denial, paired sample UI, live API/OAuth denied, revoke test session, confirm existing loopback service still live. Gunicorn 27.0.1 release checked https://pypi.org/project/gunicorn/ and settings https://gunicorn.org/reference/settings/ ; Chromium certificate guidance https://chromium.googlesource.com/chromium/src.git/+/master/docs/linux/cert_management.md . Seven offline test methods authored, not executed by assistant; actual TLS, browser, Android trust and live allowlist boundary still pending. Stop sample gateway when not testing; do not enable it at boot or expose real data until reviewed. No Nextcloud changes.


### Browser pairing 403 fix (2026-11-27)

User reached trusted HTTPS pairing page in Chromium but native form submission returned generic Forbidden. Likely no-referrer policy serialized POST Origin as null (https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy). Set same-origin referrer policy on /pair only, preserving exact HTTPS Origin validation (null/missing/foreign still rejected), no-referrer elsewhere and all other safeguards. No certificate, code store, live server or service unit changes. Added header/origin regression method and closed static test responses to address prior ResourceWarning. Expected 69 tests; not executed by assistant. Pull, test, restart only spotify-desk-device.service, navigate to root fresh and generate a fresh code; browser retest pending.


### Authenticated live gateway opt-in (2026-11-27)

User confirmed sample pairing and actual revoke-all returns browser to pairing page. Live mode defaults off; on Pi stop gateway, use device_gateway.py live-on, restart and pair again. Switching mode revokes all sessions and outstanding code, no change to Spotify credentials. Exact six GET routes and one POST command plus local session check, no OAuth, arbitrary URL, file, redirects, proxy environment, cookies or forwarded headers; local backend remains loopback with fixed request headers. Query/action/body validation, JSON-only bounded response, private HTTPS cookie, no-store and same-origin request header/POST Origin guard. Only existing Spotify image hosts added to CSP; no new data collectors. Device frontend hides local OAuth link and checks session every 15 seconds while online (revocation denies future requests immediately; already rendered/offline information cannot be recalled). Use live-off with service stopped then restart to roll back. Existing admin tunnel remains required for OAuth. Local CA trust/expiry and Android compatibility remain separate. Tests include synthetic backend allowlist, unauthorized requests, command and revocation. JS syntax checked; Python suite not executed by assistant. Do not enable gateway boot until live behavior verified. No router or Nextcloud changes.

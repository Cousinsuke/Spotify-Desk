# Validation checklist and roadmap

Updated 2026-11-26. Order confirmed by user; device and Pi checks pending until actual evidence is recorded.

## Gate A — acquisition and read-only checks

- [x] Selected target model H23K37 / checkers, charcoal black.
- [x] Documented candidate listing and reported return period.
- [x] User confirmed ordering an Echo Show 5 (2026-11-26).
- [ ] Confirm delivered unit, adapter, condition and final total if relevant.
- [ ] Test physical condition without updating stock Fire OS.
- [x] Install usbutils on Omarchy (user observed lsusb now runs).
- [x] Verify ADB/Fastboot 37.0.0p1 and usbutils 019 on Omarchy (2026-11-26).
- [ ] Test a data-capable cable/adapter with the actual device.
- [ ] Record redacted Fastboot product and exact LK.
- [ ] Check current upstream supported build; decide whether to proceed.

## Gate B — custom OS

- [ ] Verify exact release, source, amonet version and hashes if published.
- [ ] Confirm user wishes to modify after understanding brick/return risk.
- [ ] Complete unlock with stable power/USB; verify required recovery.
- [ ] Install correct checkers ROM per current guide.
- [ ] Check boot, touch, screen, sound, Wi-Fi, restart and stability.
- [ ] Test kiosk without Home Assistant, or select a standalone alternative.

## Gate C — Pi deployment (can start before delivery)

See [PRE-ARRIVAL.md](PRE-ARRIVAL.md) for safe preparation.

- [ ] Power on unused Pi; inspect OS/architecture, resources, ports and any retained Nextcloud files. Decide whether to reuse existing OS or use separate clean storage; no wipe without approval.
- [ ] Implement isolated headless backend and authenticated HTTPS device endpoints; preserve existing localhost-only behavior by default.
- [ ] Add negative tests: unauthorized requests, revoked credentials, spoofed proxy headers, blocked admin/OAuth paths, unencrypted requests, origin/CSRF and no-store.
- [ ] Verify protected credentials and no sensitive logging or persistent CGM data.
- [ ] Test restart/autostart, fail/recover and Nextcloud remains available.
- [ ] Validate kiosk trusts certificate, no HTTP fallback.

## Gate D — functions

- [x] User selected Pi hosting and supplied rough clock-first, right-rail UI concept (2026-11-26).
- [x] User accepted arrow + swipe reveal, configurable timeout, content expansion, floating More drawer and per-page auto-hide.
- [x] User accepted Home default B, fixed layout first, selectable clock styles, conditional lightweight presets/backgrounds, and no inactivity page switching.
- [x] User accepted Spotify visual direction, controls, floating device selector and compact mode dropdown (replacing three permanent buttons); requested physical volume and Echo mode subject to feasibility.
- [ ] Test mode dropdown current-mode display, selection/dismissal, unavailable mode handling and distinction from playback-device selector.
- [x] User accepted Weather B, selected current metrics, configurable forecast duration/icon styles, static weather backgrounds, Bournemouth and tap-day details.
- [x] User accepted existing Glucose layouts and range/scale functionality; existing renderer and reader reviewed.
- [x] User accepted compact Glucose view dropdown, selectable green/default and optional dynamic backgrounds, 6h/AUTO reload and unchanged chart interaction.
- [x] User accepted final Glucose 40/60 equal-height BOTH cards, minimal headers, no graph title, compact view and graph duration/scale dropdowns.
- [x] User accepted drawer/Settings layout, dismissal, reorder/pinning, immediate apply/reset and initial Settings/Calendar/System Information apps; delegated preference storage.
- [x] User accepted final themes, animation/display behavior, 10s hide, swipe-down contextual quick settings and Home startup.
- [ ] Review exact contextual controls and default palette/schedule; define Calendar/System Information scope before implementing.
- [ ] Test Graphite/Black, rail style/opacity, animation settings/reduced motion, 10s default, gesture conflicts, always-on behavior and Home startup; verify actual backlight via supported Android integration, not CSS alone.
- [ ] Test drawer dismissal without page change, intentional navigation, pin/order persistence and protected access; immediate settings apply, reset scope, save failure/retry, Pi/local non-sensitive preference recovery, no private data in cache.
- [ ] Test dynamic background boundaries with synthetic data, neutral stale/offline state, static green default, preference selection and 6h/AUTO reset; no clinical alert semantics or change to readings.
- [ ] Regression test all three Glucose views at 960 x 480 in both rail states; 1/3/6/12/24h time filtering, gaps, AUTO/FULL bounds and readable ticks; no extra upstream calls on changing range, no private data persisted; verify equal-height 40/60 cards, dropdown placement/targets, no clipping, no redundant titles, and clear stale/offline/sample labeling.
- [ ] Test physical +/- key events and mode-aware volume popup, safe privacy/power behavior, non-permanent fallback if necessary, no permanent volume icon/slider, extended device selector and far-right save button, no double volume changes or navigation side effects.
- [ ] Verify Spotify seek/shuffle/repeat/save permissions and endpoint/device support; test floating device selector and last-track paused/disconnected states.
- [ ] Experiment with official Spotify Android app/Connect on Echo Show, speaker output and background playback alongside kiosk; measure RAM; keep Echo mode unavailable until verified.
- [ ] Test one active Home layout/preset at a time, wallpaper sizing, settings persistence, clock styles, and verify idle never changes page; measure resource use on device.
- [ ] Validate navigation reflow, swipe/arrow, timer, per-page setting and drawer interactions in browser and on device.
- [x] Commit first isolated synthetic-data Home/navigation/Settings shell on echo-show/prototype; JS parse verified, not executed.
- [x] User visually approved Home on Omarchy; HTML/CSS/JS HTTP 200, clock/date/tiles and collapsed rail shown.
- [ ] Remaining first shell interaction tests: timer, gesture, drawer, theme/reset and reload.
- [x] Spotify synthetic UI committed on preview branch; JS parse and 17 pure-state assertions passed.
- [x] User reviewed sample Spotify screenshot and confirmed auto-hide delay works; refinements requested.
- [ ] Verify blank-area dismissal (without swallowing controls), bare save circle/green tick, neutral selectors in both rail states.
- [x] User ran nine mocked Python tests successfully (0.039s, OK) and started loopback server on Omarchy.
- [x] User corrected callback URI and reported real Spotify connected/working before pause failure.
- [x] Commit shared successful command response parsing fix and local playback progress clock; JS syntax and 10 pure clock tests passed.
- [x] User ran 13 Python tests (OK); Pause reached iPhone, browser lag and subsequent Previous device-unavailable issue observed.
- [x] Commit explicit intent, bounded confirmation and verified inactive-device recovery; 19 JS assertions passed.
- [ ] Run expanded 19 Python tests; retest pause/resume, Previous/Next while playing and paused, external device switch, seek, progress, library endpoints; physical hardware still pending.
- [ ] Complete Spotify, Weather, Glucose, contextual quick controls and pin/reorder; full browser review before hardware deployment.

- [ ] Spotify authorization and active-device metadata.
- [ ] Pause/resume/skip Xbox playback with PC fully off; check unsupported volume gracefully.
- [ ] Optional PC companion: local media/volume/visualisation, offline indication.
- [ ] Bournemouth weather: selected current conditions, clear forecast probability interval, sunrise/sunset local time, configurable daily duration (three-day default proposed), icon styles, static condition imagery, tap-day details, stale/offline status, no clipping or gesture conflicts.
- [ ] Gluroo real source verification locally with no reading/credential disclosure; compare timestamps against official app, verify source trend/units, graph gaps and stale/offline.
- [ ] Home widgets, navigation, layout on actual 960 x 480.
- [ ] Extended soak test: memory, input responsiveness, reconnect, reboot, overnight, no Nextcloud regression.
- [ ] User acceptance before marking complete.

## Evidence template

Date | component | exact version | test/action | expected | actual (redacted) | status | source/commit | next action.

For troubleshooting, record the first error, command, OS, reproducibility and resolution. Do not log personal readings, serials, credentials or unredacted network information. For medical display testing use synthetic cases and report only pass/fail or status/freshness, not actual values. Existing desktop test evidence belongs in existing docs; do not claim Pi/Echo Show validation from it.

- [x] User ran 19 Python tests successfully; paused-device dropout remains in live test.
- [x] Commit bounded last-device resume fallback; JS syntax checked.
- [x] Run 26 Python tests and diagnose paused-device dropout via redacted logs; iPhone recovery not supported when Spotify returns 404. Further phone tests deferred by user.

- [x] Review original Spotify Desk playback code and port bounded optimistic feedback; 29 JS assertions passed.
- [x] User ran 26 Python tests (0.015s, OK), compared original Wi-Fi mode, and supplied diagnostics showing 204/no devices/404 resume. User reports Xbox works perfectly and accepts iPhone limitation.
- [x] Implement real album-art backgrounds using original Desk sampler; 23 palette assertions and syntax passed.
- [x] User reports all three Spotify background styles tested and approved; specific edge cases not individually confirmed.
- [x] Weather synthetic UI committed; 13 pure JS assertions and syntax passed.
- [ ] Review Weather layout at 960x480, rail reflow, duration settings, forecast scrolling, icon styles, Home tile and day detail overlay.
- [ ] Connect real fixed Bournemouth weather feed and validate cache, freshness, condition assets and hourly data; then Glucose.
- [ ] Validate individual remaining Spotify controls and later Pi-hosted Xbox playback with PC off; actual Echo hardware pending.

- [x] User reviewed initial Weather screenshots; commit current-temperature/upcoming-hour refinements and expanded bottom cards; 25 logic tests passed.
- [ ] Review revised Weather UI, hourly/daily toggle, midnight rollover, scrolling and details at 960 x 480; connect real weather after approval.

- [x] Implement live Open-Meteo weather, shared Home tile, day/night icons, asynchronous cache and 14 mapping assertions.
- [ ] Verify actual live data and cache on Omarchy; confirm no sample temperatures in live mode and check hourly forecast and future-day sunrise/sunset. Then Glucose.

- [x] User screenshots confirm live Open-Meteo data rendered on main and expanded Weather views.
- [x] Commit forecast dropdown, remove arrows/scrollbar chrome, retain swiping and add mouse drag; syntax/source checks passed.
- [ ] Verify 3/5/7-day and hourly scrolling, mouse drag vs tap, expanded details and eventual Echo touch behavior; then Glucose.

- [x] User approved revised Weather appearance; hardware touch validation still pending.
- [x] Commit synthetic Glucose UI with original chart renderer and agreed dropdowns/backgrounds; 27 JS assertions passed.
- [x] User visually approved LIVE/GRAPH/BOTH; individual dynamic and rail edge cases not separately confirmed.
- [x] Reuse original Gluroo backend for loopback-only live mode; 15 JS assertions passed.
- [ ] Run six offline adapter tests and existing 26 server tests, then verify real Gluroo connection, timestamps, source trend, range and stale states on Omarchy. Authenticated encrypted Pi/Echo transport remains separate.

- [x] User screenshots confirm live Gluroo feed rendering in BOTH and GRAPH.
- [x] Commit saturated amber/orange palettes and remove fixed green gradient; 39 JS assertions passed.
- [ ] Review dynamic colour appearance and stale neutral state, then full Settings.

- [x] Separate chart, status cards and background themes; add Home status tile. 27 source checks passed.
- [ ] User visual review in all background modes and stale state, then full Settings.


- [x] Implement app pin/unpin and shared ordering on prototype branch; syntax and 23 assistant-runtime pure/source checks passed, commit 7f4d9ea.
- [ ] Run native Node app-shortcuts.test.js; at 960 x 480 confirm default rail, unpin one app then pin Settings, three-pin cap, order changes in both rail/drawer, unpinned destination access, persistent preferences after reload, reset restores original defaults, touch/keyboard and rail reflow. Calendar/System must not be presented as functional.
- [ ] Review independent glucose palettes (white graph and status card/Home tile) from preceding increment; confirm no change to glucose status/freshness behavior. Use sample scenarios rather than sharing real readings.
- [ ] Next Settings General/Home and scheduled night mode; Pi preflight remains separate.


- [x] Add local one-command launcher, ignored mode-600 configuration, blank example and offline regression test; 14 synthetic checks passed.
- [ ] User verifies first launch, repeat launch without prompts and existing loopback UI; do not share .env contents. OAuth reconnect after restart remains expected.

- [x] Hide Settings and quick settings scrollbar chrome, preserve native scrolling; nine source checks passed.
- [ ] Confirm finger swipe and mouse-wheel scrolling in both Settings columns and quick settings, including last row and rail states, with no visible scrollbar or gesture conflict.

- [x] User approved Settings scrolling/appearance.
- [x] Implement local refresh-token cache and add eight mocked regression tests (34 total).
- [x] User reports test_live_server.py passes and restart/reconnection works without further consent (2026-11-27; exact output not provided).
- [ ] Additional repeat-restart, Xbox-specific regression and unchanged weather/glucose verification not separately reported; cover in later integration testing.

2026-11-27: User confirmed both requested Omarchy validations worked: the test_live_server.py regression suite (34 tests expected, including eight new authorization tests) and stopping/restarting the live server with start-live, refreshing the dashboard and controlling Spotify without pressing Agree again. Mark both user-reported passes; exact terminal output, runtime and device were not supplied. Do not invent test duration or claim independent execution, two restart cycles, Xbox-specific retest or weather/glucose revalidation. Persistent local Spotify authorization is accepted; no need to repeat consent or this troubleshooting unless a new issue arises. Six-month expiry/revocation and eventual secure Pi deployment remain separate. Next continue remaining General/Home settings and scheduled night mode; no source changes in this documentation update.

- [x] Implement three Home layouts, four clock styles and five CSS wallpaper presets; 22 pure/source checks passed.
- [ ] User review at 960x480 with rail expanded and hidden, all layout/clock combinations, wallpaper/global theme, Home quick settings, reload and reset, clock-only navigation, summary data and stale glucose colours. Native Node test and physical display performance pending.
- [ ] Next scheduled night mode and remaining optional Home features if requested.

- [x] User approved Home customization overall.
- [x] Shared neutral Home tile/rail background implemented; 16 source checks passed.
- [ ] Verify matched surface styling on wallpapers, both rail states, opacity and Transparent style; confirm Glucose status colour unchanged. Then automatic night mode.

- [x] User approved shared Home surface refinement.
- [x] Implement manual/scheduled night mode, 32 new and 97 existing pure/source checks passed.
- [ ] Browser review of night controls, manual/automatic transitions, schedule persistence/reset, equal times, no page switch and status readability. Android actual backlight/always-on still pending.
- [ ] Calendar scope and design after night-mode review.

- [x] User confirmed night mode update works (browser acceptance; individual edge cases not separately reported).
- [ ] Agree Calendar source and scope; implement after design decision. Hardware brightness and always-on verification remain pending.

- [x] User selected Apple/iCloud Calendar; month/agenda preview and app registry added, 15 Calendar and 23 shortcut checks passed.
- [ ] Review month navigation, date selection, Today, agenda scrolling and both rail states at 960x480, verify no samples in live mode.
- [ ] Implement and validate private read-only CalDAV adapter, local credential setup, recurring/all-day/timezones, freshness, privacy and secure Pi transport.

- [x] Implement optional iCloud credentials in private local .env without changing existing required credentials.
- [ ] Run launcher config tests and validate real read-only CalDAV sync once adapter is implemented.

- [x] Implement read-only iCloud CalDAV adapter and live Calendar UI, 15 JS checks passed.
- [ ] Install optional dependencies, run seven Python test methods, verify actual iCloud connection, event dates, recurrence, errors and no calendar writes. Calendar filtering and hardware validation pending.

- [x] User confirmed iCloud Connected status; event synchronization not yet confirmed (empty month).
- [x] Implement DAV property merge and privacy-safe counts; JS syntax passed.
- [ ] Inspect counts and compare source calendars with iCloud.com; validate iCloud test event, nine Python test methods and subscription behavior.

- [x] User clarified only public holidays/observances and F1 events needed; retire active iCloud sync for current scope.
- [x] Public Calendar implemented, F1 2026 source schema inspected, JS syntax passed.
- [ ] Run test_public_calendar.py; confirm real bank holiday/F1 fetch, November 5 and 27–29, session time/location, source status, colour markers and future season coverage.

- [x] User approved public Calendar direction; add vertical month swipe/mouse drag, 28 Calendar checks passed.
- [ ] Browser review swipe up/down, short/diagonal gesture, date taps, arrow/Today, agenda scroll and rail/quick settings; physical touch pending.

- [x] User confirmed Calendar swipe navigation works in preview.
- [ ] Define System Information scope and host/display distinction, then implement read-only diagnostics.

- [x] User selected combined System Information option C; implement read-only metrics and service status. 35 JS checks passed.
- [ ] Run four Python fixture tests; review live metrics and service states, missing sensors, page scroll and rail; Pi/Echo hardware validation pending.

- [x] User approved live System Information page on Omarchy; screenshot confirms populated metrics and service rows.
- [ ] Verify Python fixture tests separately if not already run; real Pi and Echo hardware metrics pending.
- [ ] Power on Pi and run read-only preflight before selecting deployment approach.

- [x] User provided Raspberry Pi read-only preflight; existing Debian/ARM64 installation and free storage suitable for staged test; RAM differs from earlier assumption.
- [ ] Verify actual model, check git/venv, stage isolated checkout, run Python 3.13 tests; review reversible Nextcloud shutdown separately.
- [ ] Design/test single-worker production service, authenticated HTTPS and device integration before exposing live data.


### Raspberry Pi board confirmation

2026-11-27: User confirmed physical board Raspberry Pi 4 Model B Rev 1.5, ARM64 Cortex-A72, four cores, reported maximum 1.8 GHz, Git 2.47.3 already installed. Earlier 1.8 GiB visible RAM remains the sizing basis; physical RAM capacity not independently verified. Next stage isolated checkout and Python 3.13 virtual environment on existing Debian. Install requirements-ui.txt; for full historical regression suite also install prototype/requirements-calendar.txt (inactive Apple adapter tests need these optional packages; public Calendar runtime does not). No credentials required for offline tests; Nextcloud and external storage untouched. Production startup and secure device transport still pending. No Pi changes or test execution reported yet.


### Raspberry Pi compatibility tests passed

2026-11-27: User supplied Raspberry Pi Python unittest discover output: 58 tests ran in 0.544s, OK, including historical Apple Calendar (9), Glucose (6), Spotify server (34), public Calendar (5), System Information (4), plus launcher synthetic assertions executed on import. Expected synthetic setup/cache warning messages are not real credential failures; launcher tests use temporary directories. Confirms tested dependencies and offline regressions work on Debian 13.3 ARM64 Python 3.13.5. Real upstream connectivity, actual Pi runtime and performance still pending. Next transfer only existing three required .env keys over SSH to owner-only Pi prototype/.env without overwriting existing credentials; omit inactive Apple keys. Do not transfer refresh token while workstation may still refresh it; stop workstation preview and authorize on Pi through encrypted SSH local port forward using canonical 127.0.0.1:8765 on both ends. Keep Pi server loopback-only; no raw LAN exposure, no new proxy. Existing Nextcloud and external disk untouched pending separate decision. After live verification, production single-worker service/systemd and authenticated HTTPS device boundary remain outstanding. No code changes or actual secret transfer by assistant.


### Raspberry Pi SSH access confirmed

2026-11-27: User confirmed successful SSH login to Pi via dedicated Ed25519 key from Omarchy. Hostname resolution failed; Pi has Ethernet and Wi-Fi addresses on local subnet; use Ethernet address supplied privately by user, not committed. Raspberry Pi Connect remote shell provided existing authorized access despite forgotten account password. Initial authorized_keys entry lacked valid full public-key format; corrected full single-line ssh-ed25519 public key and permissions (home/.ssh owner-only, authorized_keys 600), fingerprint check and successful login. Private key passphrase prompt expected; no password reset, SSH daemon changes or private key transfer required. Next transfer three required configuration keys through SSH with no overwrite, start Pi loopback preview, forward canonical 8765 on workstation to Pi, reauthorize Spotify and verify services. No credential transfer or live Pi run confirmed yet. No actual keys, local IPs, hostnames or user identifiers stored in repository.


### Raspberry Pi dashboard remote preview

2026-11-27: User reported dashboard loads via intended Pi SSH tunnel and screenshot shows live-mode Home, populated weather, Spotify no active playback and Glucose Not live. Initial browser loading indicator subsequently stopped. Record remote browser access user-reported; confirm Pi identity through System Information and check service status, not assume credential transfer/authorization succeeded. Spotify refresh cache not migrated by design; authorize once on Pi via existing canonical loopback redirect through tunnel if not connected. Gluroo uses configured URL and SHA1 rather than Spotify-style OAuth; check required .env key presence without printing values, then guarded /api/system service statuses; allow existing source refresh cadence and distinguish stale/unavailable/configuration error. Never paste .env, token, API response containing glucose readings or screenshots with personal data into Git. No LAN exposure, Nextcloud changes or production service changes. Actual Pi-host identity, live Spotify/Gluroo, Calendar and persistence pending verification.


### Pi live preview accepted — automatic startup

2026-11-27: User approved Pi-hosted System Information screenshot: Raspberry Pi 4 Model B Rev 1.5, Debian ARM64, four logical CPUs, CPU 2%, RAM 36%, storage 32%, temperature 35 C, dashboard/Weather/Glucose/Calendar ready and Spotify connected idle. Confirms Pi-hosted live endpoint and service readiness at time of screenshot; not independent playback/control, CGM accuracy, stress or reboot validation. Nextcloud still running; no need to stop based on observed load, no changes to existing containers or disks. Prototype [4fe329b](https://github.com/Cousinsuke/Spotify-Desk/commit/4fe329b9e21d750e3bee82e91a3fdd34d3bd42ce) adds optional Waitress >=3.0.2,<4 production mode and unprivileged systemd user unit, using one request worker to preserve existing serialized Spotify state and background source refresh threads, loopback 127.0.0.1:8765 only, same credential loader and refresh cache, no forwarded-header trust, bounded connections/headers/body, no tracebacks to clients. Waitress docs https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html. Service restarts on failure with rate limit, owner-only umask, no new privileges; boot persistence requires linger. Uses current checkout path and existing venv; no secrets in unit, no sudo for user unit install, linger may require authorization. Existing start-live dev mode unchanged. Three additional mocked Python startup tests authored, not executed; previous 58 passed on Pi. Install requirements-production.txt, rerun regression tests, stop manual server before enabling user service, verify active/listener/browser/restart and Linger=yes; reboot test only after user chooses. Rollback disable --now unit and start original launcher. SSH tunnel still required for browser; authenticated HTTPS Echo network boundary remains a separate gate. No actual systemd installation or boot verification by assistant. No screenshots or credentials committed.

- [x] Pi live System Information and service readiness accepted.
- [ ] Install production dependency, run 61 unittest cases plus launcher assertions, enable user unit and linger, verify restart/boot, retain loopback.
- [ ] Authenticated HTTPS device boundary and physical Echo integration.


### Pi production service verified

2026-11-27: User supplied successful production installation output on Pi: prototype 4fe329b pulled, Waitress 3.0.2 installed, all 61 unittest cases passed in 0.261s plus launcher assertions. systemd user unit installed, enabled and active; loginctl Linger=yes; listener confirmed 127.0.0.1:8765 only; startup log confirms saved Spotify authorization restored. Brief Waitress queue depth warnings 1 and 2 observed after startup, consistent with deliberately serialized single request worker; no failure shown, actual latency not measured. Keep single worker until evidence warrants concurrency redesign. Service configured for boot startup without login; reboot survival not yet tested. Next verify manual restart and optional controlled reboot, reconnect SSH tunnel, verify service readiness and Spotify persistence. User should be aware reboot interrupts existing Nextcloud and remote connections; no container changes. Then design authenticated HTTPS device access (no raw reverse proxy of loopback endpoints, no real glucose on LAN until protections verified). No secrets, raw logs, hostname/IP or identifying process IDs stored. No code changes in this documentation checkpoint.

- [x] 61 Python tests passed on Pi; Waitress installed, systemd enabled/active, linger yes, loopback listener and saved authorization restored.
- [ ] Verify service restart and actual reboot recovery; monitor latency if queue warnings persist.
- [ ] Implement and validate authenticated HTTPS device boundary separately.


### Pi reboot recovery verified

2026-11-27: User verified manual restart and full Pi reboot. Post-reboot uptime ~2 minutes, service active/enabled and started automatically at boot, saved Spotify authorization restored, 127.0.0.1:8765 listener present. User reports runs fine. Initial workstation inactive/not-found output was from local Omarchy after SSH disconnected, not a Pi failure. Boot persistence accepted; no code changes. Actual post-reboot individual upstream data accuracy/playback not separately measured. Next design authenticated HTTPS device access with synthetic data first; keep existing loopback and OAuth path isolated. Physical Echo model/LK, Android trust and kiosk capabilities remain unverified. No public exposure, router forwarding, credential or Nextcloud changes; no identifying raw logs committed.

- [x] Manual restart and full reboot recovery verified; saved authorization restored and loopback listener present.
- [ ] Design and test authenticated HTTPS device boundary with synthetic data before enabling live data.


### Secure device access — sample-only gateway

2026-11-27: User agreed secure direct LAN access next. Prototype [744fc33](https://github.com/Cousinsuke/Spotify-Desk/commit/744fc33bebc287f5d1489a5f8b7524074bb498fe) adds independently running sample-only HTTPS gateway (device_gateway.py), never imports or proxies live app, no access to real Spotify/Gluroo or OAuth, explicit static route allowlist, sample root strips query, TLS+exact host+local subnet guard, cross-origin POST rejection. Gunicorn 27.0.1+ TLS (latest PyPI release checked Nov 27; settings reference https://gunicorn.org/reference/settings/), specific RFC1918 IPv4 interface and /24 or narrower, port 8443, one worker/two threads, bounded connections/headers and form size, no access logs; separate user service supplied but not enabled. OpenSSL local CA/IP SAN leaf (365 days), private CA signing key temporary and removed after issuance; owner-only state outside repo, only public CA copied via SSH with fingerprint verification and client trust, never bypass TLS; renewal/IP change requires fresh trust. Device pairing 16 hex digits, single-use ten-minute code, max 8 failed attempts; 30-day HttpOnly Secure SameSite Strict cookie, hashed tokens stored in private SQLite, eight devices maximum, local list/revoke CLI. Exact port, certificate lifetime and pairing limits implementation choices. Seven new offline tests authored, not run; expected 68 total on Pi. First install requirements-device, run suite, init with local Ethernet IP and /24, manually serve sample gateway, verify curl with trusted CA, unpaired/paired browser access, blocked live endpoints and revocation; stop after test. No change to existing loopback production service, Nextcloud, router, credentials or real data. Live API scoped gateway not implemented yet; real data remains on loopback until security verification, then explicit allowlist and tests. Android CA trust and actual Echo device integration pending. Chromium Linux CA guide https://chromium.googlesource.com/chromium/src.git/+/master/docs/linux/cert_management.md . No identifying local network details stored.

- [x] Implement isolated HTTPS sample pairing boundary.
- [ ] Run 68 Python tests; test TLS, trusted CA, pairing, unauthorized routes, revocation and existing loopback server.
- [ ] Implement scoped live API boundary after synthetic verification; Android trust and kiosk testing pending.

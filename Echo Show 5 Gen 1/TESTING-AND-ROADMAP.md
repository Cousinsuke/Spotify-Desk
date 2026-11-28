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


### Sample HTTPS gateway installation checkpoint

2026-11-27: User supplied Pi sample HTTPS gateway installation output: prototype 744fc33 pulled, Gunicorn 27.0.1 installed, 68 unittest cases passed in 0.520s plus launcher assertions; sample gateway tests passed. Flask test-client static response objects produced nonfatal ResourceWarning for unclosed index/app.js file handles; improve test response cleanup in future increment, no observed production leak established. TLS initialization completed. Separate gateway user service started (disabled at boot as intended); status sampled 31 ms after launch before Gunicorn listener appeared, so actual HTTPS listener and startup success not yet verified. Existing loopback 8765 listener confirmed. Next recheck status/journal/listeners, obtain public CA SHA256 fingerprint on Pi, transfer only ca.crt via authenticated SSH, verify fingerprint and curl --cacert hostname/IP validation, import verified CA into test browser trust and pair with locally generated one-time code. Confirm unauthorized/paired/blocked-live routes and revocation before implementing scoped live access. No actual LAN live data exposure, no TLS bypass, no router forwarding or Nextcloud changes. No secrets, local addresses or raw logs committed. Documentation only.

- [x] Gunicorn installed, 68 Python tests passed, local TLS state generated.
- [ ] Confirm gateway listener after startup, validate TLS and browser trust, pairing and revocation; live routes remain disabled.


### Sample HTTPS transport verified

2026-11-27: User verified Gunicorn 27.0.1 sample-only device gateway active, worker booted and listening on configured LAN IPv4:8443, original 127.0.0.1:8765 listener retained. Public CA copied using authenticated SSH; SHA256 file hashes matched. Workstation curl --cacert verified TLS and returned 303 Location /pair with no-store, no-referrer, nosniff, DENY and restrictive CSP (connect-src none). No certificate bypass. Journal query returned no journal files but systemctl status provided startup logs; persistent journal not required at this stage. Next import verified local CA in test browser (browser certificate authority trust, no private key), generate one-time pairing code locally, verify sample UI, persistence, blocked API/OAuth paths and revocation; no real data enabled yet. Gateway remains disabled at boot intentionally. Do not publish code, cookie, certificate fingerprint, local address or raw output. No Nextcloud or existing live server changes.

- [x] LAN HTTPS listener, matching CA transfer hashes, verified TLS and unauthenticated redirect.
- [ ] Browser trust, pairing, persistence, live-route denial and revocation.


### Browser pairing 403 correction

2026-11-27: User imported verified CA and reached pairing page in Chrome without visible certificate warning, but submitting generated code returned generic Flask 403 Forbidden (distinct from custom invalid-code message). Likely native HTML form POST Origin serialized as null under no-referrer policy, per MDN https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Referrer-Policy and Fetch standard https://fetch.spec.whatwg.org/. Prototype [449bde5](https://github.com/Cousinsuke/Spotify-Desk/commit/449bde5f64a0ba8bb42e6d1595ed50ec77c3e08e) sets Referrer-Policy same-origin on /pair only; exact HTTPS origin guard unchanged, no missing/null/foreign acceptance, no-referrer retained elsewhere. Added regression test and closed static response handles in existing tests. Expected 69 tests, not run by assistant. Pull and rerun tests, restart only sample gateway, reload pairing page fresh, generate fresh code, retry. Browser origin hypothesis not directly measured; if still 403 inspect only Origin and Sec-Fetch-Site headers (no body, cookies or codes). Existing production server/certificates/device database unchanged, no live LAN access. Pairing, persistence and revocation still pending.


### HTTPS browser pairing accepted

2026-11-27: User confirmed successful browser pairing after 449bde5 referrer-policy fix; screenshots show direct HTTPS sample Home and System Information, with sample labels. Expected synthetic statistics and music/glucose/weather values, not missing credentials. Real loopback server and tokens unchanged by gateway. Browser pairing accepted; 69-test rerun output not supplied, persistence across browser restart and real revocation still pending. Next list paired device locally, verify reload and browser reopen, revoke test session(s), hard reload to pairing, verify unauthenticated live API denied and then re-pair. Only after these checks implement explicit authenticated live endpoint allowlist with tests, not arbitrary proxy. No live data exposed; no identifiers or screenshots stored.

- [x] Trusted Chrome pairing and sample dashboard navigation verified after origin-policy correction.
- [ ] Verify persistence and revocation in browser; confirm 69-test suite result before enabling live routes.


### Revocation verified — scoped live gateway

2026-11-27: User listed valid paired session and revoked all; browser screenshot returned to pairing page. Actual revocation verified, browser restart persistence not explicitly reported. Prototype [612b888](https://github.com/Cousinsuke/Spotify-Desk/commit/612b888be85f7ced4d4a6f33e07a740cff24047b) implements explicit live-on/live-off mode, defaults sample, mode change revokes sessions; stop gateway before switch and start after. Fixed loopback backend, six GET endpoints (Spotify state/devices, weather, glucose, calendar, system), one Spotify command POST plus local session check. Exact path/method, auth cookie, explicit request header, query and JSON action validation, POST origin, bounded JSON responses, no redirects/environment proxy/forwarded headers/cookies, no OAuth routes or credentials, no-store. Existing backend continues single poller; no changes to source services or live server. Paired frontend auto directs to live query, labels live and hides OAuth link, checks session every 15 seconds; cannot recall previously displayed/offline data. Existing cert unchanged. Explicit enable only after regression suite succeeds. JS syntax checked; Python tests authored, not run by assistant; expected 80 discovered including inherited boundary tests. Actual live behavior, browser restart persistence, Android CA trust, fixed/reserved LAN IP and kiosk integration pending. Keep service manual until approved; no port forwarding, Nextcloud changes or credentials committed. Revoke test sessions and stop when not needed. Rollback stop, live-off, start.

- [x] Actual paired-device revocation verified.
- [x] Implement explicit opt-in scoped live access.
- [ ] Run regression suite, enable live mode locally, pair, verify real data/control and session restart/revocation.


### Direct authenticated live dashboard accepted

2026-11-27: User pulled prototype 612b888, ran all 80 Python unittest cases successfully in 0.680s plus launcher assertions, enabled explicit live mode and paired. User approved direct HTTPS live Home/System Information screenshots: actual Pi hardware, dashboard/Weather/Glucose ready, Spotify connected idle, Calendar partial data (individual source not established), CPU 2%, RAM 36%, storage 32%, temperature 33.6 C. Direct paired live read access demonstrated, no SSH tunnel required for browser. Actual Spotify command/artwork, calendar source detail, live graph behavior, browser restart persistence, live gateway restart/reboot recovery and Android kiosk trust not separately verified. Keep original admin service loopback and OAuth there. Next test playback controls on an active device and inspect Calendar sources if still partial; confirm browser pairing survives closure, then enable gateway user unit and verify reboot without manual start. Reserve configured Ethernet IP in router DHCP because TLS SAN/bind depend on it; no router forwarding. Gateway boot network readiness is not guaranteed by user network.target; observe actual reboot and adjust retry behavior if needed. No new code, no raw screenshots, glucose values, pairing codes, identifiers, private certificate or local network addresses committed. Nextcloud preserved. Physical Echo model/firmware and Android CA compatibility remain pending.

- [x] 80 Python tests passed on Pi; direct HTTPS paired live dashboard and hardware metrics verified.
- [ ] Real Spotify control/artwork and browser session persistence; check partial Calendar sources.
- [ ] Enable gateway startup and verify reboot; stable LAN address and Android trust/hardware pending.


### Gateway automatic startup enabled

2026-11-27: User enabled the HTTPS device gateway systemd user unit; enable --now returned enabled and active. Both services configured for automatic startup, with previously confirmed user lingering. User reports Calendar transient Partial data when opening System Information quickly, then Ready about one second later; consistent with independent source refresh, no persistent calendar issue reported, no code change needed. Final gateway reboot recovery and browser pairing persistence across reboot pending. Reboot interrupts SSH/Pi Connect and existing Nextcloud temporarily; verify direct trusted HTTPS dashboard without tunnel or manual service start, both units active/enabled, saved Spotify authorization and paired session retained. Fixed DHCP reservation recommended before permanent kiosk deployment, Android CA trust and hardware integration pending. No raw output, local addresses, identifiers or health data committed. Documentation only.

- [x] HTTPS device gateway unit enabled and active; transient Calendar partial status resolves to Ready.
- [ ] Confirm gateway reboot recovery and persistent pairing; real Spotify control check if not already performed.


### Raspberry Pi deployment milestone complete

2026-11-27: User verified complete Pi reboot recovery with both backend and HTTPS gateway active/enabled, both expected listeners (loopback backend 8765 and dedicated LAN HTTPS 8443), Pi uptime four minutes and low load. Browser screenshot after boot showed direct LIVE PAIRED DISPLAY with populated tiles without a new pairing code or SSH tunnel. Automatic startup and persistent pairing across server reboot accepted. Prototype 612b888 previously passed all 80 tests on Pi. No new code changes; no need for manual service start. Pi deployment milestone complete. Remaining: reserve existing Ethernet IPv4 in router DHCP (not confirmed), real Spotify playback command/artwork through HTTPS not separately confirmed, browser process restart persistence not separately confirmed, Echo delivery and physical model/firmware/LK inspection before flashing, Android TLS CA trust and kiosk capability, automatic kiosk startup, volume buttons, speaker integration and final performance/privacy testing. Keep loopback OAuth admin boundary, no router forwarding, no TLS bypass. Existing Nextcloud unchanged. No raw logs, IP, health readings, screenshots, or identifiers committed.

- [x] Both Pi services start after reboot; live HTTPS and pairing survive reboot.
- [ ] Confirm stable DHCP reservation, actual Spotify controls and physical Echo compatibility before kiosk deployment.


### Received Echo Show — stock firmware observed

2026-11-28: Echo Show arrived. User supplied stock Device Options photo confirming Echo Show 5 (1st generation), Fire OS 6.5.7.1 (NS6571/6225). No unlock/flash or read-only fastboot checks performed yet. Archived checkers OTA analysis includes build 6225 in 44072a3-20240709_170103 LK group (https://github.com/bboe/firebreak/blob/main/docs/devices.md#checkers); promising but not a measurement of this unit's actual LK. Current Kiosk Satellite guide confirms supported 2024 LK, exact product AEOCH, amonet-checkers-v2.0.2.zip for first generation only, warns against stock updates (https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md#echo-show-5-1st-gen). Keep offline and do not reset/update; next unplug power, hold all three top buttons while reconnecting power, enter fastboot, test cable and read product/LK; stop before writes and confirm exact result. Physical label and USB stability unverified. No private serial/photo committed; documentation only.


### Physical Fastboot compatibility confirmed

2026-11-28: Physical unit enumerates via existing Micro-USB cable and Omarchy fastboot as regular user; read-only getvar product returns CHECKERS and lk_build_desc exactly 44072a3-20240709_170103. Stock Device Options confirmed first generation, build 6225. Correct earlier expectation that fastboot must print AEOCH: current Kiosk Satellite guide says AEOCH, but R0rt1z2 shared fastbrick script explicitly maps CHECKERS to Echo Show 5 first generation (https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh), and independent successful same-build physical H23K37 report records identical CHECKERS/LK values (https://www.mojowill.com/geek/echo-show-5-lineageos-macos-home-assistant/). Exact LK supported in guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md. Do not bypass any tool device guard. Before writes confirm physical label H23K37, read unlock_status and kaeru-version if supported, obtain exact first-gen amonet-checkers-v2.0.2.zip from maintainer XDA thread (direct fetch returned 502; archive not inspected yet), verify extracted device.prop/profile.sh, exact LK payload and bundled fastboot detection. No flash, no updates, no reset, no stock Wi-Fi, no private serial committed. Documentation checkpoint only.


### Amonet profile and script preflight verified

2026-11-28: User supplied extracted amonet v2.0.2 device.prop/profile.sh/fastbrick.sh and bundled fastboot outputs. Profile DEVICE=checkers, explicit mapping of 44072a3-20240709_170103 to bin/fastbrick-20240709.img, script maps CHECKERS to 2019 first-gen, bundled binary reports exact same product/LK. User's observed locked state and earlier stock generation check match. No script changes or bypasses required; guide's AEOCH wording differs from actual CHECKERS recognized by maintainer script. Rechecked https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md and https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh. No independent archive checksum/signature verified; physical bottom label not yet explicitly confirmed. Next run original script from amonet directory using Bash, check exact product/LK/payload before YES; bootloader rewrite carries brick/data-loss risk, keep USB and power stable, no stock Wi-Fi. Script timeout is only probable success, not proof; successful TWRP 3.7.0_9-0 and adb recovery detection must be checked before proceeding to ROM installation. If failure or stock reboot do not blindly rerun or power-cycle mid-write. No writes performed as of checkpoint, no serials or private paths committed.


### TWRP reached after USB unlock

2026-11-28: User ran original amonet fastbrick.sh, correct CHECKERS/LK/payload detected, confirmed YES, reported likely successful exploit and photographed TWRP Unmodified System Partition prompt. Recovery visibly booted, confirming unlock procedure reached TWRP; exact recovery version and ADB status not yet measured. Next allow modifications for custom ROM, exit completed script, check adb devices and adb shell getprop ro.twrp.version (must be 3.7.0_9-0). Checked upstream first-gen guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md and release https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/releases/tag/checkers-2026.11.3 (27 Nov): lineageos-echo-kiosk-satellite-2026.11.3-checkers.zip SHA256 415b9e9621c2b012bfaa0e690bff8b7fc0e5c30a60b03fc67e7a14fec7fe68f2. Download on workstation, verify checksum, do not wipe until version and file verified. First install requires data/cache wipe (data loss), push image to /sdcard/update.zip, twrp install, stop on errors without reboot. Android and Wi-Fi/kiosk configuration still pending. No further device writes performed by assistant; no photos or serials committed.


### ROM pre-install verification passed

2026-11-28: User verified ADB recovery enumeration, ro.twrp.version exactly 3.7.0_9-0 and workstation ROM SHA256 exact match with published checkers-2026.11.3 release (415b9e9621c2b012bfaa0e690bff8b7fc0e5c30a60b03fc67e7a14fec7fe68f2). Rechecked upstream first-gen installation https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md and https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/releases/tag/checkers-2026.11.3. Ready for destructive initial install: twrp wipe cache, twrp wipe data (stock user data lost, /sdcard retained), adb push exact ZIP to /sdcard/update.zip, twrp install; inspect success before deleting ZIP and rebooting. Stop on any wipe/push/install error or assertion; leave recovery active, no blind retries. User to report install output before reboot. No device serial or personal file paths recorded, no actual ROM write yet confirmed. First boot ADB authorization, time sync, Wi-Fi, kiosk compatibility and trusted CA next.


### LineageOS installation succeeded

2026-11-28: User successfully ran TWRP cache wipe, data wipe (retains /data/media), pushed verified checkers-2026.11.3 ZIP (432544228 bytes) to /sdcard/update.zip and installed via twrp install. Output reports target lineage_checkers Android 11 version 2026.11.3 and script succeeded result [1.000000], no errors reported. ROM installation accepted; first Android boot not yet confirmed. Next remove transferred update.zip only and adb reboot, allow initial boot, observe display and verify ADB/Android version after boot; authorize workstation ADB if prompted. Follow first-gen upstream guide for time/Wi-Fi and Kiosk Satellite configuration; no certificate trust bypass, no new pairing or live device access until verified TLS. Original Fire OS user data wiped. No private serials, raw logs or local paths committed; documentation only.


### Android first boot and ADB confirmed

2026-11-28: First Android boot verified after removing transferred ROM ZIP and rebooting. User approved USB debugging prompt; adb devices reports device, Android release 11, product checkers, sys.boot_completed=1. Next set time and zone using echo_service time sync, join trusted home Wi-Fi (prefer 5 GHz if split), observe automatic Kiosk Satellite installation using adb logcat -s ks-install and echo_service status. Upstream first-gen guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md confirms automatic install/device owner, no Home Assistant needed for our planned standalone URL (actual setup path to verify). Private CA documentation https://kiosksatellite.com/docs/tls/ confirms user-installed Android CAs trusted by app dashboard; restart app after installing. Transfer only verified public CA via USB, install through Android Security/Encryption & credentials; never ignore SSL errors, never copy private key. Confirm app installation and Wi-Fi first, then trust/pairing and fullscreen. No serial, fingerprint, Wi-Fi credentials or personal data committed; no new firmware changes.


### Echo time and offline status verified

2026-11-28: User verified echo_service time sync using Bash command `adb shell echo_service time sync "$(date +%s)" Europe/London`; prior Fish-style parentheses failed in actual Bash terminal, no device change from failed command. Status confirms 2026.11.3 KS, 542 MB available memory, 32.5 C, correct UK time and network time on, screen timeout never, USB ADB on/root off. Wi-Fi on but not connected, KS not installed, update hostname resolution fails; expected before joining network. Next use USB `adb shell echo_service adb wifi off` (documented in https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5.md) to restrict debugging to USB, open Android Wi-Fi settings with `adb shell am start -a android.settings.WIFI_SETTINGS`, join trusted home network via touchscreen, observe `adb logcat -s ks-install` and status. Installer should download after network connection, no manual APK or reflash yet. User CA transfer/trust and standalone kiosk path pending. No private device ID, network address, password, serial, or raw screenshot committed.


### Wi-Fi and Kiosk Satellite installation verified

2026-11-28: User connected Echo to home 5 GHz Wi-Fi, observed -63 dBm and automatic successful Kiosk Satellite 2026.11.36 download/install/device-owner/permissions via ks-install log. Status confirms 470 MB available RAM, 34.4 C, UK time and screen timeout never. Earlier DNS update-check failure still shown, likely prior offline check, installer clearly reached GitHub; not a blocker. Wi-Fi ADB still enabled; disable with documented echo_service adb wifi off while retaining USB. Next transfer only verified public CA via USB, Android Security > Encryption & credentials > Install a certificate > CA certificate; Kiosk Satellite documents user CA trust https://kiosksatellite.com/docs/tls/. No TLS bypass. Inspect actual Kiosk Satellite onboarding for standalone URL path: docs primarily describe HA, standalone setup not verified; do not install HA or enter tokens merely to advance onboarding. If no standalone option, consider separate lightweight kiosk browser/native wrapper. Do not enable lockdown until navigation/recovery verified. No SSID, IP, serial, host identifier, pairing codes or raw logs committed.


### Kiosk onboarding and certificate transfer

2026-11-28: User transferred public CA successfully (1537 bytes), opened Android Security settings, then launched Kiosk Satellite package me.jxl.kiosk_satellite. Photo confirms Welcome wizard with Connect (Home Assistant URL & token), Dashboard, Voice Satellite. Certificate installation not explicitly confirmed; Wi-Fi ADB off command returned nonzero, actual status not verified. Official https://kiosksatellite.com/docs/custom-pages/ supports external URLs as default dashboard after setup, but https://kiosksatellite.com/ documents HA connection/token for wizard and no standalone bypass has been verified. Next inspect Connect page for skip/standalone option, verify CA installed and wireless ADB status; no fabricated HA credentials or new HA deployment. If required connection cannot be skipped, use separate standalone kiosk browser or project-specific WebView wrapper that explicitly trusts the intended CA and rejects TLS errors; retain current ROM, avoid lockdown or removal until fallback tested. No sensitive data, screenshots, serials, addresses or tokens committed.


### Standalone kiosk direction after HA onboarding blocker

2026-11-28: Kiosk Satellite Welcome remote-admin password validation blocked progression with admin enabled and no password; advised disabling remote admin. User reached Connect screen showing mandatory Home Assistant base URL and long-lived token with Validate & continue, no visible skip. Upstream README https://github.com/jxlarrea/kiosk-satellite confirms reachable HA instance and token prerequisites. Custom pages support does not resolve initial onboarding. Recommend retain working LineageOS and build project-owned lightweight Android WebView wrapper (or standalone browser for interim test), no HA deployment. First inspect Android WebView provider, HOME activities, current device-owner/ADB state, local Java/Gradle/SDK availability; avoid removing current owner, changing launcher or locking down until replacement tested. App should use HTTPS-only trusted CA via Android network security configuration, no SSL bypass, no secrets in repo, persistent cookies, safe recovery/settings path; native volume/brightness and boot integration are later tests, not implemented. Public CA transfer confirmed earlier, trust installation remains unverified. No private logs or identifiers committed.


### WebView verified; HOME takeover recovery

2026-11-28: User verified current Android WebView com.android.webview 156.0.8078.47 enabled/valid, multiprocess enabled, 442 MB available memory, USB ADB on/Wi-Fi ADB off, root off. Launcher3 Quickstep and Kiosk Satellite HomeAlias both present; Home button stays in Satellite setup. Upstream https://kiosksatellite.com/docs/home-launcher/ confirms automatic HOME takeover on Echo image; first-gen guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md documents `adb shell setprop persist.echo.ks_install 0` to stop automatic installer. Try direct Launcher3 activity, stop automatic installer, set HOME with `adb shell cmd package set-home-activity com.android.launcher3/.uioverrides.QuickstepLauncher`, verify resolver and HOME behavior. If owner policy overrides, app provisioning home.enabled=false is a proposed inverse of maintainer's documented true example https://github.com/jxlarrea/kiosk-satellite/issues/947; not tested yet. No package removal, root or reset. Development host Bash has OpenJDK 27, no Gradle, SDK not detected. Choose separate JDK 17 and pinned compatible Android Gradle Plugin/wrapper, official SDK; avoid altering default Java or installing newest global Gradle arbitrarily. CA trust, launcher recovery and app build still pending. No private identifiers or network information committed.


### Launcher preference and JDK17 setup

2026-11-28: User confirmed persist.echo.ks_install=0 and set-home-activity Launcher3 returned Success; resolver query accidentally used HOME# rather than HOME, so actual resumed launcher remains unverified. Recheck corrected resolver and resumed activity before removing or disabling anything else. JDK17 installed alongside default JDK27 (17.0.21 verified). Next use official Linux Android command line tools package commandlinetools-linux-15859902_latest.zip (SHA256 4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583, https://developer.android.com/studio/#command-line-tools-only), user-local SDK, accept SDK licenses interactively, install platforms;android-35 and build-tools;34.0.0 for planned AGP 8.7.x/Gradle 8.9/JDK17 compatibility per https://developer.android.com/build/releases/agp-8-7-0-release-notes. Keep existing ADB and default Java unchanged. Development app not built yet; certificate trust and launcher recovery pending. No device or account identifiers committed.


### Standalone Android app initial implementation

2026-11-28: User verified official command-line tools checksum, sdkmanager 22.0, all licenses accepted, SDK platform 35 and build tools 34.0.0 installation reached 100%. Deprecated CLI warning is informational; stray # typo corrected. Launcher verification was not included, still pending. Prototype branch commit 97dda1e9a51c2b44b5b2d8d8dd36a2b29b18dea2 adds android-app/ standalone Java WebView Activity, AGP 8.7.3/Gradle 8.9/JDK17, local build script validating HTTPS origin and CA and generating ignored resources; scoped custom CA trust, TLS errors cancel, main navigation restricted, cookies persisted, fullscreen/keep-screen-on, native Back recovery menu. No HOME role, native volume routing, brightness or auto-start implemented yet. Gradle 8.9 official binary checksum d725d707bfabd4dfdc958c624003b3c80accc03f7037b5122c4b1d0ef15cecab. Build and hardware tests pending; assistant has not compiled APK. User fetch prototype branch into existing workstation worktree, inspect status, fast-forward only; build locally with gateway HTTPS origin and verified public CA; install debug APK via USB then start activity. No backend changes/deployment, no private IPs, paths, keys or secrets committed. Confirm valid pairing page before generating pairing code; no certificate bypass. Local generated CA means Android user-store installation not necessary for this app.


### First native Android build and HTTPS pairing screen verified

2026-11-28: User verified Gradle 8.9 distribution checksum and JDK17 runtime; prototype fast-forward to 97dda1e9a51c2b44b5b2d8d8dd36a2b29b18dea2 clean. Local build script generated HTTPS origin and public CA resources; first assembleDebug succeeded (32 tasks, 24s), repeat succeeded (up-to-date, 4s). SDK XML version mismatch and deprecated API warnings nonfatal; platform-tools auto-installed. adb install -r succeeded and MainActivity launched, user confirms pairing page on physical Echo Show, establishing initial trusted HTTPS access. No paired/live dashboard functionality or negative TLS test confirmed yet. Next use existing Pi gateway pair CLI, enter private one-time code directly on screen, verify Home and all pages, test app restart cookie persistence. HOME resolver and resumed activity still show Kiosk Satellite HomeAlias despite set-home-activity earlier; installer disabled but existing device-owner launcher policy remains, not resolved. Do not press HOME unnecessarily or enable new default launcher until pairing, recovery and policy resolution tested. No Pi service changes required, no serials, private URLs, codes or raw logs committed.


### First physical display layout review

2026-11-28: Physical Echo Show successfully paired over trusted HTTPS, user photos confirm live Home, Spotify artwork and status, Weather and detail overlay, all three Glucose modes, Calendar and System Information. Physical panel reports 788x394 CSS pixels. Home/Spotify/Glucose fit, Weather forecast bottom clips/overlaps status and detail statistics clip; Calendar agenda and system panels require scrolling. Prototype commit 7a0ab548ace285f40d4d667532392a4fa268f4b6 adds compact landscape CSS (701–840px width or <=420px landscape height, minimum width 701px), smaller weather current/stats/cards and detail summary, six-column detail stats, compact calendar/system spacing and rail buttons, preserves horizontal forecast scrolling and independent panel vertical scrolling. Home and glucose styling unchanged; Spotify only reserves right reveal clearance. Added compact-layout.test.js source assertions, not yet executed or browser/device validated. Deploy to existing Pi prototype worktree with clean status and fast-forward only, restart existing user services if needed, reload Android activity without clearing data; no new APK or firmware needed. Recheck daily/hourly/weather popup bottom row, rail visible/hidden, calendar agenda vertical swipe and system panels. Kiosk default HOME remains unresolved, native controls and reboot pairing not yet tested. No screenshots, private readings, artist/track, serials, IPs or credentials committed.


### Compact display layout accepted

2026-11-28: User approved compact physical display layout after prototype CSS commit 7a0ab548ace285f40d4d667532392a4fa268f4b6. General acceptance reported; individual regression checks and source test execution not separately confirmed. Freeze current visual direction. Next automatic startup and pairing persistence: inspect existing Kiosk Satellite device-owner and HOME policy, preserve USB recovery and working app; no factory reset or owner removal until a supported reversible path is established. Then native volume/OSD, hardware brightness, local diagnostics and speaker playback. No private readings, photos or identifiers committed.

### Startup preflight — repository review

2026-11-28: Reviewed the main documentation and prototype branch at 7a0ab548ace285f40d4d667532392a4fa268f4b6. Source inspection of android-app confirms com.spotifydesk.echo/.MainActivity currently declares MAIN/LAUNCHER only, no HOME/DEFAULT filter or boot receiver. The app flushes CookieManager on page finish and pause; persistence across a process restart is not yet verified on the Echo. Existing Kiosk Satellite HOME takeover remains the known blocker; installer was already disabled and previous set-home-activity did not change the resolved HOME. Next, with authorized USB ADB, inspect device-owner and persistent preferred HOME policy without changing it, then force-stop and explicitly relaunch Spotify Desk to test cookie persistence without clearing data. Inspect only relevant redacted policy output; do not publish device identifiers, network addresses, codes or readings. Do not reboot, uninstall, remove device owner, clear data, or change firmware/launcher until the safe startup route is established. No new hardware test or application change in this checkpoint. Main README updated to reflect verified installation, accepted compact layout and current startup gate.

### Echo app restart pairing passed; HOME takeover confirmed

2026-11-28: User ran USB ADB policy preflight and force-stop/relaunch of com.spotifydesk.echo/.MainActivity, then confirmed it worked (no re-pairing required per requested test). Device owner is me.jxl.kiosk_satellite/.KioskAdminReceiver, user 0, testOnlyAdmin=false. Package dump shows normal preferred MAIN/HOME/DEFAULT activity me.jxl.kiosk_satellite/.HomeAlias (mAlways=true) and actual resolver agrees; installer property persist.echo.ks_install=0. The dump does not separately establish a persistent preferred activity. Kiosk Satellite declares a boot receiver, so disabling installer alone does not disable its startup. Official https://kiosksatellite.com/docs/home-launcher/ documents releasing HOME via the app setting without removing ownership. Maintainer https://github.com/jxlarrea/kiosk-satellite/issues/947 documents ProvisionActivity with home.enabled=true; try the inverse false as a reversible, not-yet-verified ADB command because HA onboarding prevents accessing ordinary settings. Verify HOME resolver and restore explicit Spotify Desk activity; do not remove owner, disable entire package, reset or reboot yet. Once role release verified, add opt-in HOME intent filter and recovery path to own app, then select and test startup/reboot. No code or hardware change made by assistant; no raw log, serial or private information committed.

### Kiosk HOME released — optional Spotify Desk launcher implemented

2026-11-28: User executed `adb shell am start -n me.jxl.kiosk_satellite/.ProvisionActivity --es ks.provision '"{\"home.enabled\":false}"'` and resolver changed to com.android.launcher3/.uioverrides.QuickstepLauncher. Explicit launch of Spotify Desk brought existing task to front; normal Android warning. HOME release verified; device owner not removed, installer previously disabled. Prototype [da96c7e](https://github.com/Cousinsuke/Spotify-Desk/commit/da96c7e741d4fc842d57d30fb1d254820cf5f2be) adds optional MAIN/HOME/DEFAULT .HomeAlias targeting existing MainActivity, retains normal LAUNCHER filter, singleTask, native Back and scrollable error panel with Change default Home app (Settings.ACTION_HOME_SETTINGS, fallback Settings), version 0.2.0/code 2. No device-owner transfer, boot receiver, extra permissions, automatic role change, TLS/CA or Pi changes. Basic source assertions passed before commit; APK not built or device-tested yet. Pull clean workstation prototype worktree fast-forward only; reuse existing generated local HTTPS resources and same debug signing key, JDK17/SDK35/Gradle8.9; assembleDebug and adb install -r (never uninstall or clear data). Verify manual launch and native recovery, select HOME explicitly with cmd package set-home-activity com.spotifydesk.echo/.HomeAlias, confirm resolver and actual HOME activity before reboot. Roll back with cmd package set-home-activity com.android.launcher3/.uioverrides.QuickstepLauncher and HOME key; keep USB connected. Reboot test and pairing persistence across device reboot pending; startup may require Retry if network not yet ready, automatic retry deferred. No private data committed.

### Native HOME launcher and rollback verified

2026-11-28: User fast-forwarded workstation prototype to da96c7e741d4fc842d57d30fb1d254820cf5f2be from clean status; Gradle 8.9/JDK17 assembleDebug succeeded in 5s (32 tasks, 10 executed, 22 up-to-date). SDK XML version mismatch and deprecated API warnings nonfatal. adb install -r succeeded, MainActivity started, set-home-activity com.spotifydesk.echo/.HomeAlias returned Success, resolver confirmed HomeAlias, KEYCODE_HOME resumed com.spotifydesk.echo/.MainActivity. User also ran rollback set-home-activity Launcher3 and HOME key; Success reported, actual rollback resolver not separately printed. Current expected default is Launcher3. Native HOME role selection and rollback command accepted; no separate visual confirmation of pairing after this APK update or recovery menu, no reboot yet. Next reselect Spotify Desk HOME, verify resolver, reboot via USB ADB, observe automatic dashboard without manual launch, verify paired Home and resumed activity, boot completion, HOME resolution and installer remains disabled. If native recovery appears before Wi-Fi is ready, record and test Retry; automatic network retry remains pending. USB rollback available. No new code, firmware, Pi changes or private identifiers committed.

### First Echo reboot — default HOME reverted

2026-11-28: User reselected com.spotifydesk.echo/.HomeAlias successfully, confirmed resolver and sent HOME, then rebooted over USB. Post-boot sys.boot_completed=1; resolver and resumed activity both show com.android.launcher3/.uioverrides.QuickstepLauncher; persist.echo.ks_install=0 retained. Automatic Spotify Desk startup failed; no post-reboot pairing test yet. Exact cause not established (role persistence timing, ROM or remaining Kiosk Satellite owner/boot behavior are hypotheses). AOSP Android 11 PackageManagerShellCommand.runSetHomeActivity delegates to RoleManager.addRoleHolderAsUser(ROLE_HOME), so merely using cmd role add-role-holder is not an independent fix: https://android.googlesource.com/platform/frameworks/base/+/refs/heads/android11-security-release/services/core/java/com/android/server/pm/PackageManagerShellCommand.java . Next capture targeted post-boot role state and role/KS logs before changes, then select Spotify Desk through Android HOME settings, verify role and resolver and allow time for persistence before one controlled reboot. Compare post-boot role/resolver. Keep standard launcher, USB ADB, current device owner and APK intact; do not disable system launcher, root, reset or flash. Pairing after manual launch can be checked separately. No code changes or raw logs committed.

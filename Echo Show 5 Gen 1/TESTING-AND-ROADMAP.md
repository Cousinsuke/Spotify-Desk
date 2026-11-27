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

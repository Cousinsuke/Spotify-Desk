# Echo Show 5 Gen 1 changelog

## 2026-11-27 — App shortcut customization

Prototype commit [7f4d9ea](https://github.com/Cousinsuke/Spotify-Desk/commit/7f4d9ea72483809f1b657f046559d9f1c64b8992): Settings > Apps supports pin/unpin and up/down ordering. Home and Apps remain fixed; at most three optional rail pins, retaining original default Spotify/Weather/Glucose order. Drawer lists all four enabled destinations (Spotify, Weather, Glucose, Settings), including unpinned apps; Calendar/System Information hidden until implemented. The same order controls drawer and pinned rail entries. Existing non-sensitive local preference key retained; missing/malformed preferences normalized, duplicates and unknown/disabled IDs discarded, reset restores defaults and redraws rail. Touch-friendly move buttons and focus/scroll restoration; no drag-and-drop. These exact UI choices are proposed for review, not yet user-approved. JavaScript parsed; 23 pure-state/source assertions passed using assistant JS runtime with mocked Node assertion/file interfaces. Native Node/browser/Android execution not performed; test added at prototype/app-shortcuts.test.js. GitHub compare confirmed only four prototype files changed, no original root, CAD, service, playback, weather or glucose changes. Frontend-only pull and hard refresh; no server restart or OAuth needed. Previous glucose palette review still pending; no new live-data tests or hardware work. Pi preflight remains pending.

Next: user review of independent Glucose palettes and Settings > Apps (pin/unpin, order, full limit, drawer accessibility, reload, reset at 960x480). Then extend General/Home settings and scheduled night mode in separate increments; Pi read-only preflight remains independent. Preserve iPhone Connect limitation and accepted Xbox baseline; no real data over LAN before authenticated HTTPS.

## 2026-11-27 — Independent glucose graph and Home tile palettes

User requested readable white graph instead of bright amber graph, retaining colour on the live reading, adding status colour to Home glucose tile, and separating global page themes from glucose data colours. Prototype commit 44b78cb5229a8b1257fc6226f56e8db5e1defbff: fixed graphite chart panel with white trace, dot, labels, neutral grid and shaded 4–7 display band; live reading card and Home glucose tile share reading-status palette independent of page background preference. Green, Dynamic and Global theme preferences only change the glucose page backdrop; Dynamic follows fresh reading, Global theme follows Graphite/Black. Home wallpaper and other tiles unchanged. Stale/unavailable status uses neutral card/tile and hides Home reading; existing freshness checks and thresholds unchanged. Design choice: use a consistently dark graph panel to ensure white trace readability in every theme. 27 source-level assertions and JavaScript syntax passed; browser rendering and all status transitions pending user review. No chart geometry, live reader, credentials, polling or Spotify/Weather changes. Frontend-only pull and hard refresh. No actual readings/screenshots committed.

## 2026-11-27 — Dynamic Glucose colour refinement

User screenshots confirmed real Gluroo feed rendered on BOTH and GRAPH views and requested reference-style saturated yellow/amber and orange, plus removal of residual green in dynamic mode. Prototype commit fa8e8602d4cc181509a32acb88bf14854703d2c3: existing display thresholds already correct and unchanged (below 4 red, 4–7 green, above 7 and below 15 amber, 15+ orange, stale/offline neutral). Replaced hardcoded green graph gradient with per-theme variables; themed graph traces, labels, grid, dot, shaded display band, cards, controls and status. Amber card #ffbb00 with dark text; high card #c24b00 slightly darkened from reference orange for white text contrast. Darker outer backgrounds preserve existing visual hierarchy. Global theme and stale use neutral colours. Chart geometry, values, history and scaling unchanged. 39 JS assertions passed, four representative amber/orange text contrast checks >=4.5:1. Browser visual review and all real state transitions pending; live feed rendering observed but Python adapter test result and accuracy comparison not reported. Frontend-only pull and hard refresh, no restart or reauthorization. No real readings, screenshots, credentials or account identifiers saved to GitHub. Next user visual approval then Settings; Pi/Echo secure transport still pending.

## 2026-11-27 — Glucose approved; live local integration added

User screenshots and explicit approval confirm LIVE/GRAPH/BOTH Glucose appearance accepted, requested real feed. Prototype commit a5fb75e0b24b92d5ab02920bfc2a196bb860fab5: import original root glucose_live.py from isolated worktree without modifying it; separate asynchronous worker, existing 150s upstream minimum, 429 daily backoff, HTTPS/no redirect, in-memory readings, 24h history. GET /api/glucose protected by existing exact host/header/same-origin policy plus loopback peer check, no-store; no LAN access. Browser live mode starts empty, no sample fallback, uses validated source trend only, labels stale and hides stale Home value and trend, neutral dynamic colour on stale/offline, expires live at source age 600s or no local contact for 60s. Sample scenario removed from live settings. Layout and graph renderer preserved. 15 JS assertions and syntax passed; six mocked Python adapter/route tests authored but not executed by assistant; actual Gluroo connection not verified. No account data, secrets, screenshots or real CGM values committed. User should stop server, pull prototype, run test_glucose_service.py and existing test_live_server.py, then start server using hidden local prompts for existing Gluroo Global Connect HTTPS base URL and API Secret Header SHA-1 (40 hex characters, full read/write credential), plus Spotify Client ID. No need to reconnect LibreLinkUp/Gluroo if existing sharing still works. Open loopback live URL and compare value/timestamp/trend with official app, report status only. No treatment use; Pi/Echo authenticated encrypted transport remains pending. No changes to root application or Spotify/Weather logic.

## 2026-11-27 — Weather approved; Glucose preview added

User approved revised Weather appearance after touch-first changes; actual Echo touchscreen, cache expiry and individual long forecast gestures remain unverified. Prototype commit b2e51a45c4cab513d2a77b7b2a6b0848c747a39a: synthetic-only Glucose UI follows final agreed layout: no redundant headings, top-right LIVE/GRAPH/BOTH dropdown, aligned equal-height reading/graph cards at 40/60 widths, graph duration (1/3/6/12/24h) and AUTO/FULL dropdowns, default green, optional global and dynamic display-only backgrounds, Home sample tile and Glucose quick/full settings. Copied original static/glucose-chart.js verbatim, preserving existing timestamp filtering, deduplication, 20-minute gaps, local time axis, 4–7 display band, latest dot and scale rules. View preference saved; 6h/AUTO reset on reload. Added explicitly synthetic sample scenarios to review colours (low/red, in-band/green, above-band/yellow-orange, 15+/orange); sample scenario not persisted. Colours are aesthetic, not clinical categories. No live CGM or credentials, no medical guidance, no persisted readings; official Libre app remains authoritative. 27 pure JS assertions and syntax passed; browser layout and device testing pending. Restart local Flask server after pull to serve new assets, reauthorize Spotify if needed, test three views, duration/scale and dynamic background scenarios. Next visual review before adapting existing glucose_live.py for loopback-only testing. No changes to original root application, Spotify playback or weather API. No Pi or physical hardware work.

## 2026-11-27 — Touch-first Weather controls

User screenshots confirm Open-Meteo live data rendering in daily, hourly and expanded Weather views, including current and upcoming temperatures. User requested removal of unused 3-day arrows, all hourly/detail scroll arrows and visible horizontal scrollbars, and a Spotify-style Hourly/Daily dropdown. Prototype commit ada89b8c6b01a8ea375e46ae35fd1fe9d9674431: compact native select in forecast header; no forecast arrows in any duration or expanded view; hide scrollbar chrome while retaining native touch pan/momentum and longer daily forecast scrolling. Added mouse drag for desktop review with movement threshold and post-drag click suppression, keyboard arrow scrolling on focused strips. Forecast mode switch resets position; data refresh retains main/detail scroll position. No API, Spotify or Pi changes. JavaScript syntax and nine source-level checks passed; native touch, mouse drag, card taps and actual layout still need user validation. No actual forecast values or screenshots committed. Next review touch-first Weather UI, then Glucose.

## 2026-11-27 — Live Bournemouth weather integration

User reported Weather displayed 10°C at 00:06 whereas their reference was 6°C, with night screenshot showing sunny icons. Explained sample-only data, not actual readings. Prototype commit c68531d272f8befe42e989b977236de3b883581c: live mode now fetches Open-Meteo at fixed original Bournemouth coordinates 50.72098,-1.87669, current temperature/apparent temperature/humidity/weather code/is_day, hourly temperature/rain probability/code/is_day, daily high/low/rain/sunrise/sunset. Asynchronous server refresh outside Spotify request thread, 15-minute cache, 60s failure retry limit, stale label and 6h maximum cache age, same-origin local API, no synthetic fallback in live mode. Browser uses London-local time and current/day-night icons, upcoming hours and future day details; Home uses same source. Static mode remains illustrative. Open-Meteo provides model-based current estimates and forecasts, not exact weather station observations; user's reported 6°C not independently verified. JS syntax and 14 live data mapping assertions passed using synthetic fixtures. Python runtime, real API connectivity, browser layout/freshness and Pi deployment not tested. No changes to Spotify playback logic; no private data committed. Next user update/restart, inspect current/hourly/night weather and compare with their weather app, then Glucose. API docs https://open-meteo.com/en/docs .

## 2026-11-27 — Weather layout refinements

User reviewed main and expanded Weather screenshots; requested current temperature instead of whole-day high/low, upcoming hourly values instead of past times, and better use of lower detail panel space. Prototype commit a13de889afef229a0021db8ddb0cb05a7e915657: main Weather now defaults to scrollable next 24 hours with Hourly/Daily toggle (preserves configured 3/5/7 days). Today card in Daily shows current temperature and Now label; future dates retain high/low. Today's expanded summary shows current temperature/condition and next 24 hours, with bottom cards for daily high/low, feels-like, humidity, sunrise/sunset. Future date details show forecast high/low, selected day's hourly slots and daily summary; no current conditions attributed to future dates. Hour cards open corresponding day detail; arrows and touch scrolling. London-local date/hour labels handle midnight and daylight-saving changes; values still synthetic, not live. Hourly default/toggle, card details and 24-hour horizon are implementation choices for user review. JS syntax and 25 logic assertions passed including midnight and DST; browser layout and real weather integration pending. No Spotify playback changes. Next visual review, then connect original Open-Meteo integration.

## 2026-11-26 — Spotify appearance accepted; Weather preview added

User reported testing the Spotify update and approving all three background styles. Preserve accepted Xbox playback and visual baseline. Prototype commit dc4c64be75a3d2fb9345b7dbbdfc6338917a2e0c: added synthetic Bournemouth Weather page with large current temperature/condition, feels-like, rain today, humidity, sunrise/sunset; default 3-day forecast with 5/7 options, horizontal scroll and arrow buttons, two icon styles (colour/outline), small Home weather icon, static local vector sky and condition CSS variants, selectable forecast cards opening hourly-detail overlay, Weather quick settings and Settings category. Data is explicitly sample, including daily labels and shared sample sunrise/sunset; no live weather API or cache yet. Only partly cloudy is exercised by fixed sample, remaining condition visuals and final assets need review. 13 pure JS assertions and syntax passed in assistant runtime; actual browser layout, scrolling, gesture and device tests pending. No changes to Spotify playback code or Pi. Next review Weather at 960x480 with both rail states, longer forecasts, icon styles, details/dismissal, then implement actual Open-Meteo feed using original integration and proceed to Glucose. No real readings, account information or credentials committed.

## 2026-11-26 — Real album artwork backgrounds added

Prototype commit b7cb354df0779c58a879d3c4f2e728003ab65425: real Spotify cover-derived background, adapted original static/ui.js RGB/HSL and 24x24 saturation/luminance weighted pixel sampler. Darken palette for readability, preserve neutral artwork, one in-memory palette, reuse same artwork, discard stale async callbacks, reset on missing art; if cross-origin pixel access fails, neutral fallback and regular cover display. Existing three background preferences: Album colours (default), Dimmed album artwork (actual static cover with dark overlay in live mode), Global theme (Graphite/Black). No blur, persistent art cache, new Spotify API requests or playback-control changes. JS syntax and 23 pure/mocked palette assertions passed in assistant runtime (colour, contrast examples, URL allowlist, race, CORS fallback and cache). Actual browser/Spotify CDN CORS, user appearance approval and Echo performance pending. Run existing 26 Python tests and optional node album-palette.test.js, restart server and reauthorize; test on Xbox by skipping between distinct covers and changing Background in Spotify quick settings. If colours stay neutral for colourful art, investigate CDN CORS in browser before changing architecture. Preserve original checkout and accepted playback baseline. Next Weather after visual review. No credentials or personal artwork committed.

## 2026-11-26 — Xbox playback accepted and iPhone dropout diagnosed

User ran all 26 Python regression tests on Omarchy (0.015s, OK) at prototype commit fa7c091. Redacted diagnostics establish that Pause succeeded (HTTP 200), paused state was confirmed (200), then Spotify playback endpoint returned 204 and available devices returned an empty list; explicit resume against the remembered device returned 404 and recovery was correctly blocked until playback was rediscovered. Subsequent playback/skip/device commands were accepted. User also ran original Spotify Desk Wi-Fi comparison and concluded the iPhone drops out; reported Xbox playback works perfectly and accepted moving past iPhone troubleshooting since it is not a target use case. This is evidence of Spotify Connect device unavailability in this test, not proof of the underlying iOS cause or universal device behavior. Keep current recovery safeguards, no additional speculative changes. Xbox user-reported pass; individual control coverage, Pi with PC off, and physical Echo hardware remain unverified. Next implement actual album-art-derived background colors using the existing Desk color extraction as reference, then Weather and Glucose. No code changes, no raw logs, identifiers, pairing codes or credentials committed.

## 2026-11-26 — Original Spotify Desk comparison and diagnostics

User reported the latest paused-device fallback still behaves incorrectly and asked to review the original Spotify Desk code. Reviewed main desk_ui.py (_wifi_execute, playback_state, cache), static/ui.js (optimisticUpdate, showState, skip feedback/verification), static/device.js. Original uses Spotipy, immediate optimistic UI, 3500ms same-device play override, 7000ms pending skip, bounded confirmation checks and 5s poll; original also disables controls on no active playback and rejects commands without active device, so it cannot establish that iPhone dropout is fixed. Main README identifies 7172c2e as last user-accepted playback baseline. Code fa7c091c93aff77efe856ccfacda644a850f5450: port original optimistic feedback/rollback, bounded stale same-device response hold, skip text/freeze, release write lock after acknowledgement and schedule bounded read-only confirmations. Preserve explicit device selection, current library endpoints and last-device resume fallback. Added opt-in DESK_SPOTIFY_DIAGNOSTICS=1 for fixed endpoint/status, player presence/playing/device flags, device counts/match and recovery, command/ack; no IDs, track metadata, tokens, request bodies or authorization URLs. 29 JS assertions passed and syntax checked; Python/runtime/live retest pending; user did not report a result for 26 Python tests. Compare original on same iPhone in Wi-Fi mode at loopback port 8888, not PC mode; close/stop other preview to avoid competing polls. Original app can use existing configured Client ID or local environment and existing redirect URI (do not change/remove it). Run new preview with diagnostics enabled, pause 15s, try resume; capture [spotify-diag] lines only if still failing. No further speculative device policy changes until actual diagnostics or A/B evidence. No private identifiers committed.

## 2026-11-26 — Paused-device resume fallback

User ran 19 Python tests successfully (0.012s) and reported Pause greys out all transport controls after seconds until manually playing on iPhone. Screenshot shows retained last track, no active playback, device selector without selected device. Upstream device list/status not captured; suspected Connect dropout. Code 861ccf502bc2c224796544618de97491527f2ac8: remember last confirmed unrestricted device ID in memory for five minutes; when no active playback and same device absent from list, allow explicit Resume only, with fresh check for other active/restricted devices and bounded age. Do not auto-transfer, retry writes or allow unverified skip/seek/library actions. If resume gets 403/404, disable unlisted recovery until positive rediscovery. Distinguish last device from verified device; no guarantee Spotify can wake phone. Seven additional Python tests authored (26 total), JS syntax passed; Python runtime and live retest pending. Test with phone Spotify foreground then screen locked, wait 10–15 seconds after pause, attempt Play and inspect device drawer/error. If still unavailable, compare PC playback and collect redacted diagnostics before further code changes. Spotify docs: https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices and https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback . No account identifiers or real track data saved.

## 2026-11-26 — Pause synchronization and inactive device recovery

User ran all 13 Python tests successfully (0.010s), confirmed Pause reached iPhone but browser lagged; Previous then displayed active-device unavailable and no active playback. Exact upstream state not logged. Preview commit ae6b0c2750cdad8b38a241b82be164b9b7252a39: explicit requested play/pause state, acknowledged local state, bounded post-command confirmation reads (250/650/1300ms waits), one retained historical track labelled inactive, fresh same-device availability checks for resume/skip; never silently target another active device or retry writes. Regular 5s polling retained. Six more Python tests authored (19 total); 19 pure JS assertions passed. Actual live retest and new Python tests pending. Restart/reconnect required; if phone is absent from device list, open Spotify on it and manually select it. No private data committed.

## 2026-11-26 — Spotify connected; pause response and timer fixes

- User confirmed callback URI caused initial connection failure and real Spotify worked until Pause. Traceback located JSON decode of command response; exact upstream status/body unknown.
- Code eeaea4d023d508d391513c2cd12feb1aaa2fe433: successful command responses no longer parsed as JSON, 204/empty responses handled, malformed GET controlled error, command cache invalidation, browser error classification and monotonic playback clock with pause/disconnect/seek handling. API polling remains 5 seconds.
- Ten clock assertions and JS syntax passed; four new Python regression tests (13 total) pending local run. Restart/reconnect required; fixed live playback not yet verified. No private credentials or account data committed.

## 2026-11-26 — Local Spotify server tests passed

- User successfully installed dependencies in separate Omarchy preview worktree, ran nine mocked Python tests (0.039s, OK) and started loopback Flask server.
- Screenshot shows NOT CONNECTED and Connect Spotify link while user reports playing music on iPhone. Client ID alone does not authorize Spotify. Next complete OAuth via Connect Spotify and reopen Spotify page after redirect; no actual account or playback validation yet. No identifiers, screenshot or private playback data saved.

## 2026-11-26 — Spotify visual refinements and opt-in live testing

- User reviewed sample player screenshot, confirmed auto-hide delay works, requested tap empty content to hide rail, borderless save circle with green saved tick, neutral translucent mode/device controls. Changes committed, re-review pending.
- Added isolated loopback PKCE Spotify test server and browser integration (code head 154da1eb7e4f7364d4c4ec5389d43c6fe8b1a8c4), with current URI library endpoints, in-memory tokens, local guards and nine mocked Python tests authored. JS syntax passed; Python tests and real OAuth/playback not executed. User has existing Client ID; enter locally, no secret needed. See PROTOTYPE-STATUS.md. No Pi, root application or actual CGM changes.
- Next local Spotify test and Weather.

## 2026-11-26 — Home visual approval and Spotify preview

- User launched first preview on Omarchy, HTML/CSS/JS HTTP 200, screenshot shows Home clock/date, sample tiles and collapsed rail; user said looks good. Other shell interactions not separately verified. Favicon 404 harmless; SVG favicon now added.
- Original checkout has local static/desk-dashboard.css change; leave intact, use separate preview worktree.
- Spotify preview code commit 3d8f26b6e8b403205d097808d548c629e15913dd: split artwork/player, synthetic controls, mode dropdown with Echo disabled, floating device selector, far-right save, no volume icon, selectable backgrounds and contextual quick settings. JS syntax and 17 pure-state assertions passed in assistant runtime; browser and hardware tests pending. No real service connection, Pi changes or private data.
- Next user Spotify review; then Weather and Glucose. See PROTOTYPE-STATUS.md for update command.

## 2026-11-26 — First isolated prototype increment committed

- Development branch echo-show/prototype, commit fceb8653d337645ac9df93ec17c162c3b9cd7024, static files in Echo Show 5 Gen 1/prototype/. Home, right rail/auto-hide, arrow/swipe reveal, Apps drawer, basic quick settings and General/Navigation Settings shell. Existing main root code unchanged.
- Read-back verified branch head and JavaScript parsed successfully (not executed). Browser visual/gesture/timer tests pending. No Pi integration, real data/audio or hardware brightness. Other pages, pin/reorder, scheduled night mode and per-app quick settings are pending. See PROTOTYPE-STATUS.md for run instructions.
- Main remains documentation-only; next user browser review and Pi read-only preflight, then additional pages.

## 2026-11-26 — Final display choices accepted; design baseline complete

- User selected Graphite/Black only, rail styles/transparency, 10s default hide, selectable animations, manual brightness, manual/configurable auto night mode, always-on display, top-edge swipe-down quick settings with per-app controls, and Home on startup.
- Proposed shared context-aware quick settings and Graphite default; exact shortcuts and night schedule pending. Backlight/always-on/gestures need device verification. All seven main design stages accepted; next isolated synthetic browser prototype on echo-show/prototype, alongside read-only Pi preflight. No app or hardware changes in this documentation commit.

## 2026-11-26 — App drawer and Settings direction accepted

- User selected right-side floating drawer, close/outside/app-selection dismissal, Settings Centre plus quick settings, reorder/pin apps, immediate apply and reset defaults. Initial additional apps: Settings, Calendar, System Information.
- User delegated preference storage for resource efficiency; recommend Pi-authoritative non-sensitive preferences/assets plus small local fallback. Apps label and protected Home/Apps access proposed, not individually approved. Calendar/System scope and quick settings details pending.
- Next final themes, animations and display behavior review. Documentation only, no application or hardware implementation.

## 2026-11-26 — Final Glucose layout locked for prototyping

- User requested no redundant Glucose/Libre 2 Plus or demo header in normal live UI, dark green background and lighter green cards, compact view selector top-right and graph duration/scale dropdowns within graph card.
- User explicitly selected equal-height 40/60 reading/graph split for BOTH and no graph title. Keep original data/scale behavior, stale/offline status and supplementary-display notice; synthetic previews remain labelled. No private screenshots or readings added.
- Documentation only; next app drawer and Settings design review.

## 2026-11-26 — Final Glucose refinements accepted

- User selected compact view dropdown, selectable backgrounds with green default and optional dynamic red/green/yellow-orange/orange colours, 6h/AUTO reset on reload and unchanged graph interaction.
- Recorded proposed aesthetic colour boundaries based on existing display band and requested 15+ orange, neutral stale/offline appearance and low-cost CSS implementation. No clinical thresholds or new alerts; exact palette and device performance pending.
- Next review floating app drawer and Settings; documentation only, no application or Pi changes.

## 2026-11-26 — Existing Glucose layout retained

- User supplied existing browser screenshots and requested same appearance/behavior rather than a full redesign. Preserve LIVE/GRAPH/BOTH, visible 1/3/6/12/24h buttons, AUTO/FULL toggle and original chart geometry/data semantics; adapt to 960 x 480 and right rail. Reviewed actual renderer, frontend, reader and docs. No private screenshots/readings copied into Git.
- Documented existing defaults (BOTH, remembered view, 6h, AUTO), time filtering, gaps, scale rules and backend limitations. Proposed minor visual consistency choices; not approved yet. Next complete these and review app drawer/Settings. No application or Pi changes.

## 2026-11-26 — Weather direction accepted

- User selected B large current weather above daily cards; temperature/condition, feels-like, rain probability, humidity and sunrise/sunset; configurable forecast duration and icon styles, condition-themed static backgrounds, always Bournemouth, tap day for details.
- Proposed three-day default, swipeable longer forecast, Pi-served static images and cached forecast/day-details panel; exact detail layout, API fields and resource impact pending. No implementation or hardware tests.
- Updated UI-DESIGN.md, handoff, README, architecture and roadmap. Next review Glucose using established chart preferences.

## 2026-11-26 — Spotify mode dropdown refinement

- User requested replacing the three permanent Wi-Fi/PC/Echo buttons with a compact dropdown and down arrow to reduce clutter. Display the active mode when closed; show available modes when opened, keep the playback-device selector separate. Echo mode and hardware volume remain unverified. Documentation only; Weather review next.

## 2026-11-26 — Spotify bottom row refinement

- User removed the permanent volume icon from the Spotify design; move save-song action to its position on the far right, extend the tappable playback-device selector across the remaining space. Physical volume keys and transient popup preferred. Hardware forwarding remains unverified; consider non-permanent fallback only if necessary. Documentation only; next Weather review.

## 2026-11-26 — Spotify direction accepted; physical controls and local audio research

- User selected current web player's left artwork/right controls with immersive styling, selectable backgrounds, previous/play/pause/next, seeking, shuffle/repeat and like/save; floating device selector.
- Requested physical +/- with transient volume popup and a third Echo speaker mode. Exact-model Kiosk Satellite guide assigns third button to screen power/privacy; preserve these, use three touchscreen selectors. Hardware key forwarding and local Spotify Android/Connect playback remain untested; Web API cannot stream audio. Record alternatives and sources in UI-DESIGN.md.
- Prefer last-track metadata/artwork in memory with correct paused/disconnected label if lightweight; minimal fallback. No implementation or hardware tests; next Weather layout review.

## 2026-11-26 — Home direction accepted

- User selected default B (clock with subtle widgets), optional other fixed presets if lightweight, background options conditional on resources, selectable clock styles, and fixed layout first with optional low-cost customization.
- User explicitly requires staying on current page during inactivity; page changes only by user choice. Layout B's three compact summaries are inferred from selected concept, not separately approved; validate in prototype.
- Documented one-active-layout approach, static resized wallpapers served by Pi, no initial drag/resize editor and unmeasured performance. Next design review: Spotify, with Own idea on all questions. No code/device changes.

## 2026-11-26 — Navigation behavior accepted

- User selected right-edge arrow + inward swipe to reveal; configurable inactivity timeout; full-width content when hidden; grid icon opens floating app drawer; per-page auto-hide settings.
- Updated UI-DESIGN.md, handoff, README and roadmap to supersede the earlier proposals. Default timeout and exact visual design not selected. Next review Home with Own idea options. No implementation or hardware changes.

## 2026-11-26 — Collapsible navigation proposal and design review process

- User proposed automatically hiding the right navigation icons after inactivity to reclaim screen space, with tap or small right-edge arrow to reveal.
- Recorded candidate behaviors in UI-DESIGN.md and updated handoff/README. Exact timing, reveal gesture, layout behavior, More and page designs remain open.
- User requests ideas/questions for every design stage with an explicit Own idea option, including modifications to proposed ideas. Start navigation and Home, then iterate other pages. No code or device changes.

## 2026-11-26 — Pi hosting selected; dashboard concept received

- User explicitly selected the Pi backend for future expansion and to reduce workload on the Echo Show.
- User supplied a rough UI reference with central clock/date, small weather line, abstract wallpaper and right-side vertical icon rail. The final question-mark icon is a placeholder for additional features.
- Recorded proposed five-slot navigation (Home, Spotify, Weather, Glucose, More), proposed grid icon and separate More page first, plus alternatives. Exact icons, page layout and interaction remain for user review.
- Added UI-DESIGN.md and refreshed handoff, pre-arrival plan and roadmap. No implementation, firmware or Pi changes; reference image described in text, not uploaded.

## 2026-11-26 — Omarchy tools verified; hosting alternatives reviewed

- User verified installed ADB 1.0.41 / 37.0.0p1, Fastboot 37.0.0p1 and usbutils 019 on Arch x86_64. Tool availability confirmed, not physical USB compatibility.
- User clarified Pi is powered off and Nextcloud is no longer used. Pi remains recommended initial host; native Android and Termux are possible later experiments without a separate server. Free cloud hosting is not preferred for private CGM data. See SOFTWARE-AND-PI.md.
- Next action: power on and inspect existing Pi OS/storage; no reimage without permission. No application or device changes performed.

## 2026-11-26 — Order confirmed; pre-arrival preparation

- User reported ordering the Echo Show 5; awaiting delivery. No bootloader or actual hardware result yet.
- Prioritized read-only Raspberry Pi inspection and Omarchy tool verification, followed by an isolated headless dashboard, synthetic-data UI tests at 960 x 480, and secure connectivity. See PRE-ARRIVAL.md.
- No Pi installations, firmware changes or root application changes made. Next step: obtain redacted Pi preflight output and verify tools.

## 2026-11-26 — Documentation baseline

- Created dedicated project folder for the Echo Show direction, preserving the existing root code, CAD/PCB work and documentation.
- Captured the Hardware Haven video description links, Kiosk Satellite alternative and exact target model. Rechecked upstream model guide, unlocking guide, known image release and Firebreak firmware analysis. Documented the 2024/2019/2026 LK distinction and why archive counts cannot predict a unit's success probability.
- Recorded current £45.99 candidate, pictured adapter and reported 30-day returns; prior £42.29 listing sold. No purchase or bootloader verification confirmed.
- Recorded Omarchy usbutils fix and corrected interpretation of bare-cable lsusb tests. USB-C to Micro-USB adapter data capability remains unknown.
- Proposed always-on Pi deployment, no Home Assistant dependency, separate PC companion, authenticated HTTPS and secure GGC credential handling. No Pi changes, flashing, code changes or actual-device tests performed.
- Added handoff and validation roadmap.

## Earlier discussion summary (November 2026)

- Initial research considered TECHO5 and larger Echo Show 8; user rejected 8-inch size and requested black. Video screenshots clarified first-gen Android route rather than TECHO5.
- Gen 2 considered as fallback with a distinct image and unlocking procedure. Current selection returned to first-gen model.
- Discussed PC-independent Spotify Connect control (Xbox), optional PC mode, weather and supplementary glucose display. Existing documented GGC reader is the starting point; secure remote health-data transport remains open.
- Discussed stock firmware updates/downgrades, confirmed 2024 LK support and identified alternative test point method as higher risk/unverified for actual unit.

Future updates: append dated entries with evidence and exact versions, distinguish proposed from tested, refresh CHATGPT-HANDOFF.md and checklist after significant progress.

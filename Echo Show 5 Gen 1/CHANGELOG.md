# Echo Show 5 Gen 1 changelog

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

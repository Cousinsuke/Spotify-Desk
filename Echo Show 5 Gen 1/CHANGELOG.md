# Echo Show 5 Gen 1 changelog

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

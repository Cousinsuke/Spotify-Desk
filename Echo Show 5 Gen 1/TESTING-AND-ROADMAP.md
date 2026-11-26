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
- [x] User accepted Spotify visual direction, controls, floating device selector; requested physical volume and Echo mode subject to feasibility.
- [ ] Approve Weather and other remaining layouts, exact Home/Spotify details, rail sizing, defaults and drawer visuals.
- [ ] Test physical +/- key events and mode-aware volume popup, safe privacy/power behavior, non-permanent fallback if necessary, no permanent volume icon/slider, extended device selector and far-right save button, no double volume changes or navigation side effects.
- [ ] Verify Spotify seek/shuffle/repeat/save permissions and endpoint/device support; test floating device selector and last-track paused/disconnected states.
- [ ] Experiment with official Spotify Android app/Connect on Echo Show, speaker output and background playback alongside kiosk; measure RAM; keep Echo mode unavailable until verified.
- [ ] Test one active Home layout/preset at a time, wallpaper sizing, settings persistence, clock styles, and verify idle never changes page; measure resource use on device.
- [ ] Validate navigation reflow, swipe/arrow, timer, per-page setting and drawer interactions in browser and on device.
- [ ] Build browser prototype at 960 x 480 with synthetic test data and review before hardware deployment.

- [ ] Spotify authorization and active-device metadata.
- [ ] Pause/resume/skip Xbox playback with PC fully off; check unsupported volume gracefully.
- [ ] Optional PC companion: local media/volume/visualisation, offline indication.
- [ ] Bournemouth weather, current conditions and three-day forecast.
- [ ] Gluroo real source verification locally with no reading/credential disclosure; compare timestamps against official app, verify source trend/units, graph gaps and stale/offline.
- [ ] Home widgets, navigation, layout on actual 960 x 480.
- [ ] Extended soak test: memory, input responsiveness, reconnect, reboot, overnight, no Nextcloud regression.
- [ ] User acceptance before marking complete.

## Evidence template

Date | component | exact version | test/action | expected | actual (redacted) | status | source/commit | next action.

For troubleshooting, record the first error, command, OS, reproducibility and resolution. Do not log personal readings, serials, credentials or unredacted network information. For medical display testing use synthetic cases and report only pass/fail or status/freshness, not actual values. Existing desktop test evidence belongs in existing docs; do not claim Pi/Echo Show validation from it.

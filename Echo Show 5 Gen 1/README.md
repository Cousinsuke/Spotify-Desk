# Echo Show 5 Gen 1 — Spotify Desk

**Last updated: 2026-11-28. Status: LineageOS installed; Raspberry Pi HTTPS gateway and paired native display working; compact physical layout accepted. Startup/reconnection, hardware brightness and mode-aware volume accepted; Green glucose target-band visual review is next; native Spotify media-session integration deferred.**

This is a separate hardware/deployment path within Spotify-Desk, not a replacement for the existing Windows/Omarchy software or ESP32/Waveshare CAD work. The aim is a small, black, touchscreen desk dashboard with no separate physical media buttons required. Reuse the current software rather than rebuilding it unnecessarily.

## Start here

- [CHATGPT-HANDOFF.md](CHATGPT-HANDOFF.md) — read first in every new conversation.
- [HARDWARE-AND-FIRMWARE.md](HARDWARE-AND-FIRMWARE.md) — models, firmware evidence, purchase decision and upstream references.
- [INSTALLATION-AND-USB.md](INSTALLATION-AND-USB.md) — cable checks, read-only bootloader identification, gated installation and recovery.
- [UI-DESIGN.md](UI-DESIGN.md) — clock-first home, right-side navigation and expandable dashboard pages.
- [SOFTWARE-AND-PI.md](SOFTWARE-AND-PI.md) — dashboard requirements, host architecture, Spotify and privacy-preserving CGM integration.
- [TESTING-AND-ROADMAP.md](TESTING-AND-ROADMAP.md) — validation gates and next steps.
- [PROTOTYPE-STATUS.md](PROTOTYPE-STATUS.md) — branch, first preview scope, launch and validation.
- [PRE-ARRIVAL.md](PRE-ARRIVAL.md) — preparation tasks that do not require the physical device.
- [CHANGELOG.md](CHANGELOG.md) — dated research, decisions, fixes and results.

## Current direction

Amazon Echo Show 5 first generation (2019), charcoal black, physical model H23K37 / checkers. This unit reported fastboot product CHECKERS and supported LK 44072a3-20240709_170103; LineageOS Android 11 build 2026.11.3 has been installed and booted successfully. See hardware and installation documents for historical checks; no repeat flash is required.

The user confirmed the Raspberry Pi deployment direction on 2026-11-26. The selected deployment is a Raspberry Pi 4 serving a lightweight touchscreen web dashboard over authenticated HTTPS. The desktop PC is optional for Spotify Connect, weather and supplementary CGM display; local PC media control and audio visualisation require a separate running desktop companion. Home Assistant is not required. Kiosk Satellite onboarding required HA credentials, so the project uses its own native WebView app with scoped HTTPS CA trust.

The UI direction is based on the user's rough reference: a clock-first home screen, abstract wallpaper, and compact right-side vertical navigation with accepted auto-hide behavior: arrow and swipe reveal, configurable delay and per-page behavior, content reflow, and a grid icon opening a floating app drawer. Home default B (clock with subtle widgets), selectable clock/background options conditional on performance, fixed layouts first and no automatic page changes on inactivity are recorded. Spotify split/immersive layout, floating device selector, physical volume popup and experimental Echo speaker mode are recorded. Weather B layout with configurable forecast length, selectable icons, condition-themed static backgrounds, fixed Bournemouth and tappable daily details is accepted. Glucose preserves the existing browser layouts and chart behavior, with compact view dropdown, selectable backgrounds and optional dynamic display-range colours, 6h/AUTO defaults and unchanged graph interaction. Final layout uses equal-height 40/60 BOTH cards, minimal headings and graph-card duration/scale dropdowns. Right-side Apps drawer with reorder/pinning, Settings Centre plus quick settings, immediate apply/reset, and planned Calendar/System Information accepted. Pi-first preference storage recommended. All seven design stages accepted: Graphite/Black, selectable rail and animations, 10s default, manual brightness, configurable night mode, always-on, contextual swipe-down quick settings and Home startup. The physical compact dashboard layout, hardware volume, brightness, automatic startup and reconnection have since been accepted; see the latest handoff for remaining test limits.

## Maintenance and privacy

Update this folder as each meaningful research result, command outcome, decision or fix is established. Record date, source, exact model/version, status (proposed / documented / tested / accepted / blocked), evidence, next step and any limitations. Do not present planned work as completed. Keep actual secrets, account identifiers, serial numbers, readings, medical screenshots, real network details and token files out of this public repository. Do not alter the existing mechanical work unless explicitly requested.

Existing references: [project README](../README.md), [architecture](../docs/ARCHITECTURE.md), [dashboard design](../docs/DASHBOARDS.md), [Gluroo integration](../docs/GLUCOSE-LIVE.md).

## Latest prototype checkpoint (2026-11-28)

The isolated prototype is at [8c88142](https://github.com/Cousinsuke/Spotify-Desk/commit/8c88142f3bcf67528c87e73b38cbc019cdcf947c). Pi backend and authenticated HTTPS gateway recover automatically after Pi reboot; the paired Android app is 0.9.0. Physical dashboard layout, local Spotify playback, Echo/Xbox mode-aware volume, brightness, diagnostics and startup/reconnection polish accepted for tested paths. Last Pi suite: 96 Python tests passed. Spotify title/artwork latency remains unresolved; user deferred local media-session integration. Green Glucose target band implemented; next physical visual review. Extended stability deferred. See [CHATGPT-HANDOFF.md](CHATGPT-HANDOFF.md) and [TESTING-AND-ROADMAP.md](TESTING-AND-ROADMAP.md).

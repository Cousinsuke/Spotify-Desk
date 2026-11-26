# Echo Show 5 Gen 1 — Spotify Desk

**Last updated: 2026-11-26. Status: ordered by user; awaiting delivery. Pre-arrival software and Pi preparation; no Echo Show installation or Pi deployment confirmed.**

This is a separate hardware/deployment path within Spotify-Desk, not a replacement for the existing Windows/Omarchy software or ESP32/Waveshare CAD work. The aim is a small, black, touchscreen desk dashboard with no separate physical media buttons required. Reuse the current software rather than rebuilding it unnecessarily.

## Start here

- [CHATGPT-HANDOFF.md](CHATGPT-HANDOFF.md) — read first in every new conversation.
- [HARDWARE-AND-FIRMWARE.md](HARDWARE-AND-FIRMWARE.md) — models, firmware evidence, purchase decision and upstream references.
- [INSTALLATION-AND-USB.md](INSTALLATION-AND-USB.md) — cable checks, read-only bootloader identification, gated installation and recovery.
- [UI-DESIGN.md](UI-DESIGN.md) — clock-first home, right-side navigation and expandable dashboard pages.
- [SOFTWARE-AND-PI.md](SOFTWARE-AND-PI.md) — dashboard requirements, host architecture, Spotify and privacy-preserving CGM integration.
- [TESTING-AND-ROADMAP.md](TESTING-AND-ROADMAP.md) — validation gates and next steps.
- [PRE-ARRIVAL.md](PRE-ARRIVAL.md) — preparation tasks that do not require the physical device.
- [CHANGELOG.md](CHANGELOG.md) — dated research, decisions, fixes and results.

## Current direction

Amazon Echo Show 5 first generation (2019), charcoal black, physical model H23K37 / checkers / fastboot product AEOCH. A dedicated unofficial Android 11 LineageOS 18.1 build exists for this hardware. A supported model is not proof that a particular unit has a supported bootloader. Do not connect the stock device to Wi-Fi, update it, flash it or open the case until the initial read-only checks and return conditions have been assessed.

The user confirmed the Raspberry Pi deployment direction on 2026-11-26. The selected deployment is a Raspberry Pi 4 serving a lightweight touchscreen web dashboard over authenticated HTTPS. The desktop PC is optional for Spotify Connect, weather and supplementary CGM display; local PC media control and audio visualisation require a separate running desktop companion. Home Assistant is not required for the intended project; evaluate Kiosk Satellite's standalone configuration versus a simple kiosk browser.

The UI direction is based on the user's rough reference: a clock-first home screen, abstract wallpaper, and compact right-side vertical navigation with accepted auto-hide behavior: arrow and swipe reveal, configurable delay and per-page behavior, content reflow, and a grid icon opening a floating app drawer. Home default B (clock with subtle widgets), selectable clock/background options conditional on performance, fixed layouts first and no automatic page changes on inactivity are recorded. Spotify split/immersive layout, floating device selector, physical volume popup and experimental Echo speaker mode are recorded. Remaining pages and final visual styling remain to be approved; see UI-DESIGN.md.

## Maintenance and privacy

Update this folder as each meaningful research result, command outcome, decision or fix is established. Record date, source, exact model/version, status (proposed / documented / tested / accepted / blocked), evidence, next step and any limitations. Do not present planned work as completed. Keep actual secrets, account identifiers, serial numbers, readings, medical screenshots, real network details and token files out of this public repository. Do not alter the existing mechanical work unless explicitly requested.

Existing references: [project README](../README.md), [architecture](../docs/ARCHITECTURE.md), [dashboard design](../docs/DASHBOARDS.md), [Gluroo integration](../docs/GLUCOSE-LIVE.md).

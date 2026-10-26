# Spotify Desk Thing

An experimental desktop music controller and future physical desk accessory, built around an 800 × 480 touchscreen, a **preferred three-key media layout**, and a **push-to-switch-mode rotary volume encoder**.

**Repository status:** Phase 5.2 is the last **user-accepted playback** baseline (`7172c2e`). An additive Home / Weather / **sample-only** Glucose browser preview was committed on `main` on 2026-10-25 and **visually validated by the user on Windows 11**, including a live Bournemouth weather response. Spotify transport controls, Omarchy and live glucose remain unvalidated. Real ESP32 firmware has not started.

## Direction
## Weather dashboard — Bournemouth (2026-10-25)

The /device Weather screen is now fixed to **Bournemouth, UK** (no city input). It displays live current conditions plus a **three-day forecast covering today and the following two days** with daily high/low temperatures and rain probability, sourced from Open-Meteo. Forecast refresh interval is 15 minutes; the new UI is committed but awaits Windows browser visual acceptance. See [docs/DASHBOARDS.md](docs/DASHBOARDS.md).


- Spotify **Wi-Fi mode**: Spotify Web API and Spotify Connect.
- **PC mode**: local Windows 11 media sessions or Linux MPRIS/playerctl, with PC audio visualisation.
- Common HTML/CSS/JavaScript 800 × 480 player interface.
- Optional private-LAN device simulator, paired using a short-lived code and bearer token.
- Planned physical hardware: ESP32-S3, Waveshare 4.3-inch 800 × 480 touchscreen, **three ~18 mm MX media keys beneath screen and an ~18 mm diameter push-capable rotary knob at right** (rotate for volume; **press to switch PC/Wi-Fi mode**; interaction mapping accepted), custom 3D-printed enclosure. The prior four-key *software simulator* is unchanged. **Board, case dimensions and pinout are not finalized or purchased.**

## Current status

- Windows 11 companion: **Phase 4.2 user-accepted**; later simulator changes need platform-specific revalidation.
- Omarchy/Arch companion and browser device simulator: **Phase 5.2 user-accepted**; 39 tests passed in the user's Omarchy virtual environment.
- Rev B CAD package: both sharp and R5-rounded alternatives and original ZIP uploaded and verified under [`mechanical/revB/`](mechanical/revB/) (`6ae257e`). This is a design baseline, not a final enclosure.
- Real ESP32 firmware, electrical design, final hardware protocol and enclosure: **not implemented**.

## Current source and historical versions

The accepted Phase 5.2 Python, JavaScript, CSS, HTML and tests have been imported to the repository root. **Current source checkpoint:** [`7172c2e`](https://github.com/Cousinsuke/Spotify-Desk/commit/7172c2ee2f285253507b13c71acb7072adc04067). Do not re-run the one-time `import-phase5-2.ps1` script on an already imported checkout.

**Historical ZIP migration is complete.** Sixteen version archives were uploaded in [`f781506`](https://github.com/Cousinsuke/Spotify-Desk/commit/f78150605b15af1fa451aa5ed725f023fd03835c), with checksums recorded in [the archive manifest](docs/history/ARCHIVED-PHASE-ZIPS.md). They are reference snapshots, not alternate active source trees.

## Preserve earlier ZIP versions

Earlier ChatGPT-delivered patch ZIPs have been uploaded as **archives**, without replacing the current runnable code. If additional historical ZIPs are found later, rerun:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$HOME\Projects\Spotify-Desk\scripts\archive-local-phases.ps1" -DownloadsPath "$HOME\Downloads" -Publish
```

The archive script places historical ZIPs under `archives/phase-zips/`, strips generated `__pycache__`/`.pyc` entries from stored copies without changing Downloads, records both original and archived SHA-256 checksums in `docs/history/ARCHIVED-PHASE-ZIPS.md`, and commits/pushes to `main`. The ZIPs are historical reference builds, **not** a replacement for current root-level source. The script rejects common private filenames, but cannot guarantee that older archives contain no secrets within source code; review before publishing in this public repository.


## Experimental multi-dashboard preview (2026-10-25)

An additive **Home / Weather / Glucose** preview now exists in the paired `/device` browser simulator. Home includes clock, music and weather shortcuts; Weather calls Open-Meteo directly from the browser; Glucose has **clearly labelled synthetic graph data only** with no Libre 2 Plus account connection or live values. The earlier Spotify playback implementation is retained. **This new preview awaits Windows/Omarchy runtime validation and user acceptance; it is not ESP32 firmware.** See [dashboard implementation and test plan](docs/DASHBOARDS.md).

## Libre-style glucose timeline preview (2026-10-25)

Glucose v0.5 adds **real clock-time labels**, a user-selected **4–7 mmol/L shaded display band**, responsive auto-scale/full-scale graph controls and **1h / 3h / 6h / 12h / 24h** options. On the Glucose page only, the top-right Wi-Fi/PC control is visually replaced by **LIVE / GRAPH / BOTH** layout choices; Spotify's actual playback mode controls remain unchanged. The v0.5 layouts were shown running on Windows. A follow-up v0.6 chart fix changes FULL to a Libre-style **3–21 mmol/L axis with 3-unit labels**, removes overlapping AUTO Y-axis ticks and awaits a quick visual check. See [dashboard notes](docs/DASHBOARDS.md).

## Live glucose bridge — Gluroo / Nightscout (2026-10-25)

The Glucose screen now has an **opt-in live-capable** HTTPS reader for Gluroo Global Connect / Nightscout-compatible feeds. Pairing and use are **localhost-only**: no personal glucose data is exposed through the prototype HTTP LAN device interface. When configured, it polls at least 150 seconds apart and shows latest mmol/L, trend arrow, timestamp and a time-series graph; delayed readings are explicitly marked **STALE / OFFLINE**. No real Libre 2 Plus account has been connected or end-to-end tested yet. Setup and important privacy caveats: [live glucose integration](docs/GLUCOSE-LIVE.md).

## Experimental historical LibreView CSV graph (2026-10-25)

The local `/device` Glucose screen can now **import a user-downloaded LibreView CSV in the PC browser** to preview **historical readings** (not live), with explicit record timestamps and graph gaps. The import runs in browser memory only; no readings, credentials or CSV files are sent to Flask or stored in GitHub. This new feature **awaits user runtime testing** and does not replace Abbott's app or glucose alarms. Details: [dashboard documentation](docs/DASHBOARDS.md).

## Project documentation

- [Current-state handoff](docs/CHATGPT-HANDOFF.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisions](docs/DECISIONS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Design](docs/DESIGN.md)
- [Hardware overview](docs/HARDWARE.md)
- [Phase 6 Waveshare screen and input-expander research](docs/HARDWARE-RESEARCH.md)
- [Phase 6 extended hardware comparison](docs/HARDWARE-COMPARISON.md)
- [Phase 6 proposed component shortlist with UK prices](docs/HARDWARE-SHORTLIST.md)
- [Phase 6 pre-purchase voltage, wiring and mechanical verification](docs/HARDWARE-PRE-PURCHASE-CHECK.md)
- [Phase 6 electrical chip/boot and protected-input design review](docs/HARDWARE-ELECTRICAL-REVIEW.md)
- [Phase 6 manufacturer-dimensioned faceplate and encoder fit study](docs/HARDWARE-MECHANICAL-LAYOUT-STUDY.md)
- [Editable trial mechanical envelope CAD (SCAD / SVG / coordinates)](mechanical/README.md)
- [Angled wedge 3D shape, internal packaging and input-PCB proposal](docs/HARDWARE-WEDGE-CASE-PROPOSAL.md)
- [Parametric 3D reference model (not a print-ready case)](mechanical/wedge_packaging_concept.scad)
- [Rev B sharp and R5-rounded CAD package, ZIP and coordinates](mechanical/revB/README.md)
- [Selected hook-and-click screwless cover CAD alternative: two front hooks, rear release and LCD screw mounts](docs/HARDWARE-REV-B-HOOK-CLICK-COVER.md)

- [Research: screwless underside cover alternatives — hook-and-click, slide-detent, magnetic and other designs](docs/HARDWARE-REV-B-BOTTOM-COVER-ALTERNATIVES.md)
- [Rev B screwless slide-in bottom cover (new trial, screen mounts keep screws)](docs/HARDWARE-REV-B-SCREWLESS-SLIDING-COVER.md)
- [Rev B removable underside cover and screen mounting prototype (separate STEP download; not print-ready)](docs/HARDWARE-REV-B-REAR-COVER-AND-SCREEN-MOUNTS.md)
- [Selected 4mm caps: final UK keycap shortlist, print process and physical dimensions to verify](docs/KEYCAP-FINAL-SHORTLIST.md)
- [Rounded Rev B actual CAD comparison: 2mm / 4mm / 6mm media keycap heights](docs/HARDWARE-REV-B-KEYCAP-HEIGHT-CAD-COMPARISON.md)
- [Rounded USB-left case: recessed MX media keycaps, play/pause icons, knob and fit drawings](docs/HARDWARE-REV-B-MEDIA-CONTROLS-FIT.md)
- [Rotated 180° experimental case CAD (sharp/R5 shells, side power access cutout; not print-ready)](docs/HARDWARE-REV-B-ROTATED180-CASE-PROTOTYPE.md)
- [Rev B alternative 180° Waveshare module orientation: move USB power to case left](docs/HARDWARE-WAVESHARE-ROTATION-180-STUDY.md)
- [Waveshare manufacturer STEP inspection: actual board sockets, mounting points and corrected connector sides](docs/HARDWARE-WAVESHARE-STEP-INSPECTION.md)
- [Rev B parametric 3D internal packaging study (concept only)](docs/HARDWARE-REV-B-INTERNAL-PACKAGING.md)
- [Latest Rev B dimensioned CAD study and fit blockers](docs/HARDWARE-WEDGE-REV-B-CAD.md)
- [Setup](docs/INSTALL.md)
- [Testing](docs/TESTING.md)
- [Changelog](docs/CHANGELOG.md)
- [Recovery](docs/RECOVERY.md)
- [ChatGPT workflow and continuation prompt](docs/CHATGPT-WORKFLOW.md)

## Safety

Never commit `.spotify_token.json`, `.desk_config.json`, `.desk_devices.json`, `.env`, credentials, device bearer tokens, virtual environments or local machine-specific configuration. Local development servers must not be exposed to the public internet.

This project is a prototype and is not affiliated with Spotify.

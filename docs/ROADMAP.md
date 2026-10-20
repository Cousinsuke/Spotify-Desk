# Spotify Desk Thing — roadmap

This roadmap tracks **planned phases**, not every ad-hoc fix. Actual latest work is recorded in [CHATGPT-HANDOFF.md](CHATGPT-HANDOFF.md).

## Phase 1 — Discovery and Spotify integration
- [x] Define desk-device concept, 800 × 480 target and controls
- [x] Create Spotify developer app using PKCE for localhost prototype
- [x] Read current playback and implement play/pause/next/previous/volume
- [x] Validate Spotify Premium playback in browser

## Phase 2 — Browser UI and playback polish
- [x] Implement 800 × 480 music-player mock
- [x] Album art, track/progress display and Spotify device selection
- [x] Improve skip latency feedback and optimistic controls
- [x] Restrict glow to display bounds
- [x] Add album-colour ambient glow and playback breathing

## Phase 3 — Windows 11 companion
- [x] Read local Windows media session metadata
- [x] Native playback controls and Windows volume
- [x] Audio-reactive output meter and continuous SSE stream
- [x] Fix missing WinRT dependency; validate on Windows

## Phase 4 — Omarchy/Arch companion and volume routing
- [x] Linux playerctl/MPRIS media adapter
- [x] PipeWire/wpctl volume + output monitor prototype
- [x] Synchronize PC-mode Spotify volume with matching Connect playback
- [x] Preserve SYSTEM fallback for non-Spotify local players
- [x] User acceptance of volume behavior on Windows and Omarchy
- [ ] Validate native Linux MPRIS against a running local Linux Spotify session where practical

## Phase 5 — Device bridge and simulator
- [x] Browser `/device` simulator with 4 keys + rotary encoder
- [x] Paired LAN-device protocol, local-only pairing and revocation, restricted LAN API
- [x] Restore polished player look and responsive controls in the device simulator
- [x] Fix PC artwork proxy/race/retry behavior (Phase 5.2); Omarchy accepted
- [x] Run 39 Python tests on Omarchy (reported passing)
- [ ] Revalidate newest Phase 5.2 source on Windows
- [ ] Improve state polling/SSE efficiency and test across real LAN clients
- [x] Import vetted source into GitHub (`7172c2e`), preserve 16 historical ZIPs (`f781506`) and use Git for later history and releases

## Phase 6 — Hardware selection and firmware proof-of-concept (current planning)

- Front-panel decision (2026-10-20): user accepted **three ~18 mm MX keycaps** (Previous / Play-Pause / Next) below screen and **push-capable ~18 mm rotary knob** to the right. **Turn = volume; press = toggle PC/Wi-Fi**. Detached fourth button is a placeholder only. Shuffle/repeat/settings remain touchscreen actions. This accepts input behaviour, **not** electrical/CAD/firmware design; Phase 5.2 simulator unchanged.

- Research checkpoint (2026-10-20): manufacturer-supported shortlist, original-board pin usage, **CH422G I²C address conflict**, potential expansion choices, power and PSRAM estimates recorded in [HARDWARE-RESEARCH.md](HARDWARE-RESEARCH.md). An extended comparison of original/B/C models and AW9523 vs quadrature-decoding seesaw expansion is in [HARDWARE-COMPARISON.md](HARDWARE-COMPARISON.md). **Research only:** user agreed to proceed with provisional parts **Waveshare 25948 + push encoder ADA377 + Waveshare AW9523B 22132** for pre-purchase evaluation (not yet bought). Full manufacturer screen/chip PDF and mechanical gating notes are in [HARDWARE-PRE-PURCHASE-CHECK.md](HARDWARE-PRE-PURCHASE-CHECK.md); a separate *conditional, not solder-approved* electrical input network and indexed module schematic/reset/I²C risks are in [HARDWARE-ELECTRICAL-REVIEW.md](HARDWARE-ELECTRICAL-REVIEW.md). Provisional **150×105 and 165×110 mm** panel trials, I²C cable/knob interference risk and the corrected **7 mm shaft projection beyond encoder bushing** are in [HARDWARE-MECHANICAL-LAYOUT-STUDY.md](HARDWARE-MECHANICAL-LAYOUT-STUDY.md). Exact connector harness, expander safe-power-up circuit and CAD fit remain open.
- [x] Identify **provisional exact** Waveshare touch SKU **25948**, retrieve manufacturer schematic/pinout and dimensions (paper validation; revision/bench still open)
- [ ] Check ESP32-S3 RAM/PSRAM, flash, display bus/controller, touch controller and library support
- [ ] Verify safe electrical map for **six digital inputs** (3 MX + A/B + encoder push), including AW9523B startup-output protection, expander reset bias, I²C 3.3 V jumper/4→6 wire harness, debounce and encoder performance. Logical map proposed, not final physical wiring.
- [ ] Measure/verify power and USB strategy (screen published 5 V/450 mA, not peak), ESD, grounding, connector and accessory power margin
- [ ] Decide first firmware stack (ESP-IDF, LVGL, Arduino or compatible framework)
- [ ] Implement firmware that pairs to Phase 5 companion and renders basic track state
- [ ] Validate touch controls, button debounce and encoder acceleration
- [ ] Design robust reconnect / offline screens

## Phase 7 — Standalone mode and secure provisioning
- [ ] Define what 'standalone' means: remote Spotify Connect control vs direct audio playback
- [ ] Confirm Spotify API/SDK constraints and provisioning/refresh-token storage approach
- [ ] Secure Wi-Fi credentials, device pairing and authenticated local communication
- [ ] Decide HTTP vs TLS/security model before non-local deployment
- [ ] Test recoverability after disconnect/reboot

## Phase 8 — Enclosure and final physical prototype
- [ ] Confirm exact display dimensions and mounting points
- [ ] 3D-print enclosure prototype with tactile key/knob fit
- [ ] Finalize cable clearance, serviceability, ventilation and structural mounts
- [ ] Wiring/PCB/protoboard design and build
- [ ] Test durability, touch responsiveness and everyday ergonomics

## Phase 9 — Reliability, distribution and documentation
- [ ] Robust Windows startup/update workflow and Linux service lifecycle
- [ ] Reproducible builds and CI for desktop + firmware
- [ ] Versioned changelog/releases, restoration instructions and hardware assembly guide
- [ ] Runtime acceptance tests on Windows, Omarchy, and physical device

**Rule:** Tick items only on evidence. A phase can remain open while some components are accepted. Ad-hoc bugs/polish belong in the handoff and changelog even when no roadmap item matches.

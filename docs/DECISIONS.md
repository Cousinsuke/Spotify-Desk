# Spotify Desk Thing — decisions log

Record accepted direction, rationale and alternatives. Proposed decisions must stay clearly labelled as proposed.

## D001 — Build software first
**Status:** Accepted

Develop and test Windows/Omarchy player and a browser simulator **before** buying the display, controller or enclosure components. Reduces risk of incompatible hardware.

## D002 — Target interaction design
**Status:** **Physical control mapping user-accepted (2026-10-20); final hardware/CAD not accepted**

The 800×480 touchscreen plus **three MX media keys** (K1 Previous, K2 Play/Pause, K3 Next) below the display, and a **rotary volume encoder with an integrated push switch** on the right, is the selected interaction direction. Turning the knob adjusts volume; **pressing the knob toggles PC/Wi-Fi mode**. The detached fourth-button symbol in the sketch was a placeholder only, **not a fourth MX key**. Shuffle, repeat, settings and optional mode access remain on the touchscreen. Approximate user sketch dimensions: 18 mm / 0.71 in visible 1u-style keycaps and ~18 mm knob outside diameter.

**Electrical consequences:** exactly **six requested digital contact signals** — 3 MX, 2 encoder A/B quadrature, 1 momentary encoder push — before optional expansion. The input-expander selection, compatible *push-capable* encoder model, mounting dimensions and wiring remain research tasks. Existing accepted **Phase 5.2 four-key browser simulator has not changed**; adapt it in a dedicated implementation task, preserving working playback/pairing/glow behaviour.

## D003 — Cross-platform companion
**Status:** Accepted

One Flask/Spotipy/web UI core plus platform-specific adapters. Windows uses native Windows Media Control + pycaw + WASAPI meter; Linux uses MPRIS/playerctl, wpctl and a PipeWire/Pulse-compatible monitor. Keep observable platform differences and fallbacks documented.

## D004 — Spotify volume ownership
**Status:** Accepted (Phase 4.2)

Wi-Fi mode controls Spotify Connect volume. PC mode uses Spotify volume **only if** local playback matches Spotify Connect; otherwise shows and changes SYSTEM volume. The device must never silently change an unrelated Spotify device. Native PC playback remains local.

## D005 — Paired device bridge
**Status:** Accepted prototype (Phase 5)

Browser simulator represents proposed physical hardware. Six-digit one-time pairing code (ten minutes), authenticated persistent bearer token, revoke controls, `--lan` opt-in. Original Spotify OAuth and desktop APIs remain loopback-only, not general LAN endpoints.

## D006 — Keep prototype credentials local
**Status:** Accepted

Store Spotify public Client ID via `--configure` in ignored `.desk_config.json`; Spotify OAuth cache and paired-device tokens in ignored local files. Never commit credentials, device tokens, audio samples or actual Wi-Fi details.

## D007 — Versioning and source-of-truth
**Status:** Accepted direction

Git main is the canonical source once imported. Use commits, tags/releases and `docs/CHANGELOG.md` for versions, **not duplicated working code folders**. **Implemented source-of-truth:** accepted Phase 5.2 files imported at commit `7172c2e`; 16 prior phase ZIP snapshots archived separately at `f781506` with manifest `docs/history/ARCHIVED-PHASE-ZIPS.md`. No older ZIP replaces active root code.

## D008 — ESP32 board and firmware stack
**Status:** Provisional parts chosen by user for verification; not bought, wired, bench-tested or electrically approved

Research in [HARDWARE-RESEARCH.md](HARDWARE-RESEARCH.md) identifies **Waveshare 25948 (ESP32-S3-Touch-LCD-4.3)** as a preferred candidate (not accepted); B/C variants are alternatives. Original display uses 20 RGB GPIO signals, shared I²C GPIO8/9 and occupies addresses `0x20–0x27`, `0x30–0x3F`, `0x5D`, making common MCP23017 boards a conflict. **Proposed** compact AW9523 breakout (0x58) needing external input pulls, TCA9539 (0x74–0x77), or Adafruit QUAD rotary seesaw breakout (0x49) with possible off-label use of its four independent switch pads for MX keys; the published QUAD pinout has an apparent duplication needing schematic/bench verification. Standard single QT rotary (0x36–0x3D) also conflicts. See [HARDWARE-COMPARISON.md](HARDWARE-COMPARISON.md). Nothing approved/soldered. ESP-IDF+LVGL is the preliminary firmware preference. New [HARDWARE-SHORTLIST.md](HARDWARE-SHORTLIST.md) proposes **touch SKU 25948** (small/270-nit) vs brighter/larger **4.3B 27848**, push-capable **Adafruit 377** (24 detents, 6 mm shaft), and **Waveshare AW9523B expansion 22132** (I²C nominal 0x58) as the compact first-try input module. Proposed three-part UK subtotal £40.90 before accessories. A **QUAD seesaw PID 5752** module could record rotary counts but its off-label 3 MX + press layout remains unverified. User explicitly chose **Waveshare 25948 + Adafruit 377 + Waveshare AW9523B 22132** as proposed hardware to verify before buying. Manufacturer PDF review in [HARDWARE-PRE-PURCHASE-CHECK.md](HARDWARE-PRE-PURCHASE-CHECK.md) confirms LCD outer 106.1×67.8 mm and ~98×60 mm mount pitch, PEC11 13.2 mm body/M7×0.75 threaded bushing, 0.5±0.2 mm push travel, ~16 mm drawing for supplied knob, 4-pin I²C 3.3V-selector and expander 6-pin connector. **AW9523B chip GPIO power up as outputs**; with 0x58 straps P0 defaults LOW open-drain but RSTN has **100k internal pull-down**, requiring verified board-level reset bias. Datasheet-backed register config and **proposed 22kΩ pull-up + 1kΩ series** input protection (6 inputs) are in [HARDWARE-ELECTRICAL-REVIEW.md](HARDWARE-ELECTRICAL-REVIEW.md). **Module-specific reset/pullup/harness circuits not fully verified** and physical build still pending. The exact case, electrical assembly and firmware are **unaccepted and untested**.

## D009 — Meaning of standalone Wi-Fi mode
**Status:** Open

Clarify whether physical standalone means **controlling Spotify Connect playback remotely** or actually **decoding/playing Spotify audio**. The browser Wi-Fi mode is remote control via an authenticated companion, not independent ESP32 playback.

## D010 — Network security
**Status:** Prototype only

The current local bridge uses HTTP with a bearer token and local pairing. Restrict it to trusted private LANs. Never port-forward or deploy on a public network. Review TLS, discovery, token storage, and provisioning before a real device is shipped.

## D011 — Modern volume knob finish
**Status:** User-selected provisional appearance (2026-10-20); mechanical compatibility and purchase pending

Use **Knob Zone KZ0087-01** flat-topped, ridged black aluminium knob as the first design candidate in preference to Adafruit PID 377's supplied retro-looking cap. Dimensions **15.1 mm Ø × 15.2 mm total height** with 6 mm round bore and grub screw; nominal max shaft insertion **12.4 mm**; Bourns PEC11 drawing clarifies the nominal **15 mm L1 shaft length includes bushing** and has **l=7.0 mm bare shaft projection beyond the threaded bushing**. Thus the 6.0–12.4 mm accepted insertion range plausibly fits the encoder on paper. User wants the low exposed profile of their RK M75 keyboard knob. **Do not assert push-click/grub-screw/faceplate compatibility without CAD/fit tests**; check the encoder's integrated push switch and clearance. **KZ0022** remains a compatible-looking fallback, **KZ0059 domed** is rejected. This is a cosmetic selection, not a change of ESP32/input module architecture. No hardware has been purchased or tested.

## D012 — PCB-mounted controls and a split front/rear enclosure
**Status:** User approved an isolated **prototype CAD study** (2026-10-26); not an approved fitted enclosure, printed part, manufactured PCB or purchased hardware.

User suggested attaching the touchscreen and buttons/knob to a PCB/serviceable front assembly and **replacing the restrictive small underside hatch** with a split enclosure whose rear half clips, hooks or slides onto the front. This could solve assembly and servicing without forcing the entire 693-solid Waveshare module through the current ~59.1 mm hatch. Three attempted screened extraction directions from the original case did collide within the first 3.5 mm of vertical descent, while the intended final seated position was fully checked (693/693 model solids, no material overlap above 0.05 mm³). No continuous path is established for either strategy.

**Recommended concept to investigate:** R5 front structural carrier with the original Waveshare module screwed at its four manufacturer mounting points, one custom control PCB accommodating 3 MX switches + Adafruit 377 push encoder, the proposed AW9523B input interface, and a removable near-full-depth rear tub held by short rigid registration hooks plus accessible rear/underside snap catches. The front structural frame, not PCB solder joints, carries repeated button/encoder forces. An oversized custom PCB mechanically carrying the Waveshare itself is an alternative to test only once front/back stack heights, 4 mm resting cap position, actual switch travel, shaft access and PCB screw clearances are known. Do not duplicate the ESP32-S3 already built into the chosen Waveshare.

**Preserve accepted external appearance:** 156 mm R5 shell, 55° slope, rotated 180° USB-left display, three keycaps and knob at their established positions, 4 mm keycap height. New shell seam, I²C power/wiring protection, PCB outline, receiver hooks, service screwdriver clearance and USB cable routing all unverified. **Original V2 hook-click case and lid, software and historical STEP sources untouched**. See [split-case and control PCB proposal](HARDWARE-REV-B-SPLIT-CASE-CONTROL-PCB-CONCEPT.md).


**Prototype checkpoint:** `mechanical/revB/cad/split_case_control_pcb_study.py` and parameters create a valid separate front shell, rear half and unpopulated L-shaped controls PCB outline, with nominal shell split at local inward W=24mm. **No actual screen brackets, joining latches, real PCB footprints or connector alignment have been solved.** See [Rev B-C CAD trial](HARDWARE-REV-BC-SPLIT-CASE-CAD-TRIAL.md). Old V2 hook-click CAD is maintained as reference.

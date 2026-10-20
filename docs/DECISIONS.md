# Spotify Desk Thing — decisions log

Record accepted direction, rationale and alternatives. Proposed decisions must stay clearly labelled as proposed.

## D001 — Build software first
**Status:** Accepted

Develop and test Windows/Omarchy player and a browser simulator **before** buying the display, controller or enclosure components. Reduces risk of incompatible hardware.

## D002 — Target interaction design
**Status:** Accepted direction

800 × 480 touchscreen; 4 MX mechanical keys: previous, play/pause, next and PC/Wi-Fi mode; rotary encoder for volume. Preserve the established player artwork, album-reactive glow, progress and speaker/volume UI. Exact physical locations are not finalized.

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
**Status:** Pending research

Research in [HARDWARE-RESEARCH.md](HARDWARE-RESEARCH.md) identifies **Waveshare 25948 (ESP32-S3-Touch-LCD-4.3)** as a preferred candidate (not accepted); B/C variants are alternatives. Original display uses 20 RGB GPIO signals, shared I²C GPIO8/9 and occupies addresses `0x20–0x27`, `0x30–0x3F`, `0x5D`, making common MCP23017 boards a conflict. **Proposed** compact AW9523 breakout (0x58) needing external input pulls, TCA9539 (0x74–0x77), or Adafruit QUAD rotary seesaw breakout (0x49) with possible off-label use of its four independent switch pads for MX keys; the published QUAD pinout has an apparent duplication needing schematic/bench verification. Standard single QT rotary (0x36–0x3D) also conflicts. See [HARDWARE-COMPARISON.md](HARDWARE-COMPARISON.md). Nothing approved/soldered. ESP-IDF+LVGL is the preliminary firmware preference. The exact board, voltage jumper, expander module, encoder, mechanical fit and framework are still **unaccepted and untested**.

## D009 — Meaning of standalone Wi-Fi mode
**Status:** Open

Clarify whether physical standalone means **controlling Spotify Connect playback remotely** or actually **decoding/playing Spotify audio**. The browser Wi-Fi mode is remote control via an authenticated companion, not independent ESP32 playback.

## D010 — Network security
**Status:** Prototype only

The current local bridge uses HTTP with a bearer token and local pairing. Restrict it to trusted private LANs. Never port-forward or deploy on a public network. Review TLS, discovery, token storage, and provisioning before a real device is shipped.

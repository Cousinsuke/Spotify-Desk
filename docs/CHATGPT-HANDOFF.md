# ChatGPT handoff — Spotify Desk Thing

> Current-state save point, not the full project history. **Read this first** in a new project conversation. Cross-check against the current branch and commits.

Updated: 2026-10-20

## Repository / checkpoint

- Repository: `Cousinsuke/Spotify-Desk`
- Default / current development branch: `main` (no alternate development branch established yet)
- Last source baseline: **Phase 5.2** source imported into `main` from checksum-checked ZIP; actual GitHub commit verified
- Latest implementation checkpoint: **`7172c2ee2f285253507b13c71acb7072adc04067`** (`feat: import accepted Phase 5.2 desktop and simulator baseline`, source commit). Later docs/script commits are not a newer application version.
- Handoff status: GitHub migration verified complete. All 16 historical ZIP snapshots and the checksum manifest are committed at `f78150605b15af1fa451aa5ed725f023fd03835c`; this is an archive commit, not a newer application implementation checkpoint.
- GitHub access: connected read/write access was confirmed at bootstrap; verify access in future conversations

## Current project phase vs current actual work

- **Current project phase:** Phase 6 — hardware research, compatibility decisions, printable-case work to come; **no ESP32 firmware implemented**.
- **Current actual work:** A new **3D wedge packaging concept** based on user's triangular/wedge desk-stand reference. **Do not assume 165×110 face/55° angle are user accepted**. Leading model uses 165 mm wide, 110 mm *sloped-face* length, **55° from tabletop**, 16 mm vertical chin and 20 mm rear top roof, deriving **83.1 mm desk depth and 106.1 mm height**. Raised chin addresses lower MX switch body/floor clearance; roof prevents upper LCD from occupying near-zero tip depth. Previous 2D key/knob/display positions preserved. Removable bottom hatch and AW9523B accessible base position are concepts only.
- **Artifacts:** GitHub [`mechanical/wedge_packaging_concept.scad`](../mechanical/wedge_packaging_concept.scad) for parametric 3D *component-envelope* modelling and [`docs/HARDWARE-WEDGE-CASE-PROPOSAL.md`](HARDWARE-WEDGE-CASE-PROPOSAL.md) for dimensions/assembly/PCB strategy. Chat deliverable `spotify_desk_wedge_packaging_study.zip` includes the OpenSCAD model, rendered exterior/cutaway/ghost images, side-section diagram, 50/55/60 angle comparison, and speculative single-piece L-shaped *input-only* PCB zone diagram. Static OpenSCAD screenshots generated; ZIP integrity verified. **NO accurate board Z stackup, manufacturing holes, printable STL, electrical schematic approval, part order or physical fit test**.
- **Electronics strategy:** keep integrated Waveshare 25948 MCU/display. Prototype AW9523B using validated wiring first, then consider **small custom input-carrier PCB** (3 MX + encoder/push + AW9523B/protective resistors) or two smaller boards, not a ground-up ESP32 motherboard.
- **Current source baseline unchanged:** accepted Phase 5.2 app from `7172c2e`, still four simulator buttons; no hardware firmware.

## Last accepted work

- **Most recent validated repository task:** current Phase 5.2 source import and all 16 historical ZIP imports to GitHub; both commits verified from the remote repository; local `git status --short` clean. This is repository housekeeping, not new app runtime validation.
- **Most recent accepted interaction-design task:** three physical MX media keys plus rotary volume encoder whose **press toggles PC/Wi-Fi** (2026-10-20; design approval only, no hardware implementation).
- **Last accepted software:** Phase 5.2 device/PC artwork reliability fix on **Omarchy**; user confirmed the fix worked and ran **39 Python tests**, all passing.
- Previous accepted: Phase 4.2 Windows and Omarchy volume sync; Windows companion play/pause, album art, sound-level stream; Phase 5 pairing and simulator UI were demonstrated, then polished.
- **Do not assume:** Phase 5.2 has been individually runtime-validated on Windows after the last patch; earlier Windows platform validation is real but older.

## Implemented in current checked-in Phase 5.2 source

- Flask + Spotipy PKCE Spotify Wi-Fi mode at `/`, OAuth redirect on localhost.
- PC mode: Windows media-session adapter or Linux playerctl/MPRIS adapter; WASAPI/PipeWire audio level sampling, SSE for the glow.
- 800×480 HTML/CSS/JS interface, album-colour glow, optimistic controls, synchronized Spotify volume where the local track matches Spotify Connect; SYSTEM fallback.
- Browser `/device` simulator: four switches (previous, play/pause, next, mode switch), rotary volume steps, authenticated paired device API, state/events, album-art proxy/retry.
- Local `/pair` management page, one-time six-digit code; `--lan` optional and restricted device surface.
- `--configure` saves public Spotify client ID locally without committing it.

## Not implemented / still awaiting validation

- Actual ESP32-S3 firmware, pairing on-device, Wi-Fi provisioning, secure LAN transport, final standalone-without-PC architecture.
- Final Waveshare board SKU, connector/pinout, input expander and electrical verification, case/3-key/**push-encoder** placement. Research favors original touch SKU **25948**, but user has not selected final board. Check whether module's *full PCB* (~106.1×67.8 mm) leaves clearance behind 18 mm bottom keys and right knob.
- Real cross-platform end-to-end device simulator testing over separate physical LAN clients; Linux and Windows post-import revalidation.

## Current next action

1. **Review 3D wedge exterior and side section with user.** 165×83.1×106.1 mm (W×depth×H), **55° tilted front, 16mm raised chin, 20mm rear shelf**, soft corners and removable bottom are **proposed**, not yet accepted. Compare 50° lower/more reclined (90.7 mm deep, 100.3 mm high) vs 60° taller/more upright (75 mm deep, 111.3 mm high).
2. Request/measure exact model of the **three owned MX switches/keycaps**, plate retaining clip/total body and wiring/PCB mounting requirements. Need test coupon before full shell.
3. Obtain/mechanically trace screen 25948 **full PCB**, mounting-hole bore, antenna, left USB ports, **right I2C connector/cable direction/bend radius** and expander dimensions on real part, then create complete *collision-checked 3D assembly* (current wedge SCAD is bounding-box only).
4. Validate KZ0087 cap low-profile protrusion (~8 mm styling aim) and **encoder press/grub-screw** on Adafruit 377; Bourns l≈7mm projection beyond bushing is inside KZ0087 6–12.4mm accepted engagement range on paper, but not measured.
5. Resolve **AW9523B reset bias and 3.3 V bus safety** in `HARDWARE-ELECTRICAL-REVIEW.md` and test six resistor-protected contacts plus fast knob rotation under Wi-Fi + display load. **Do not issue solder/PCB production instructions from preliminary circuit**.
6. Only after layout/inputs are measured: draw actual fasteners, hatch, key plate and ports, 3D print fit coupons, then optionally design **custom input-only carrier PCB** in KiCad. Do not redesign the already integrated Waveshare ESP32 main board by default.

## Relevant project files (from Phase 5.2 source)

- `desk_ui.py`, `device_bridge.py`
- `windows_companion.py`, `linux_companion.py`
- `static/ui.js`, `static/ui.css`, `static/device.js`, `static/device.css`
- `templates/index.html`, `templates/device.html`, `templates/pair.html`
- `tests/`, `requirements-ui.txt`, `requirements-windows.txt`
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, **`docs/DESIGN.md`**, **`mechanical/` (editable front + wedge CAD envelopes)**, `docs/HARDWARE.md`, **`docs/HARDWARE-SHORTLIST.md`**, **`docs/HARDWARE-PRE-PURCHASE-CHECK.md`**, **`docs/HARDWARE-ELECTRICAL-REVIEW.md`**, **`docs/HARDWARE-MECHANICAL-LAYOUT-STUDY.md`**, `docs/HARDWARE-RESEARCH.md`, `docs/HARDWARE-COMPARISON.md`, `docs/CHATGPT-WORKFLOW.md`
- One-time import scripts: `scripts/import-phase5-2.ps1` (already run) and `scripts/archive-local-phases.ps1` (already run). Historical files: `archives/phase-zips/` and `docs/history/ARCHIVED-PHASE-ZIPS.md` (16 verified archives and their original/stored hashes).

## Recent meaningful commits

- `7172c2e` — accepted Phase 5.2 source imported into `main` (**implementation checkpoint**).
- `234a976` — sanitize generated Python bytecode when preserving old ZIPs.
- `f781506` — all 16 historical ZIP archives and checksum manifest pushed and verified.
- `196a66a` — Phase 6 WaveShare board/expander manufacturer-source research (documentation only; no application or firmware changed).
- `5833f0e` — Phase 6 extended screen/input-expander comparison; includes AW9523 and QUAD seesaw ideas (documentation only).
- 2026-10-20 user-accepted physical design mapping: **3 MX keys + push encoder (turn volume, push PC/Wi-Fi)**; docs-only. No fourth physical MX key.
- `cc6c4b6` — proposed SKU-specific Waveshare / encoder / AW9523B parts shortlist and UK price estimates (documentation only).
- `bab9e96` — manufacturer PDF-based pre-purchase mechanical, voltage and input-safety checklist (documentation only).
- `3f7d768` — manufacturer chip datasheet electrical review + preliminary protected six-input network and documented unresolved module schematic verification (docs only).
- `e89fa20` — faceplate 150×105 vs 165×110 mechanical study, screen I2C/right-hand knob cable conflict, and manufacturer-supported 7 mm exposed encoder shaft correction (documentation only).
- 2026-10-20 static CAD envelope milestone: source assets added under `mechanical/`; 3-page A3 PDF/SVG/DXF bundle delivered as a conversation attachment. No 3D-print manufacturing geometry or runtime tests; the latest Git source baseline remains unchanged.
- 2026-10-20: wedge 3D packaging proposal + editable SCAD checked in to mechanical/, separate annotated rendered concept ZIP in conversation; purely geometric, not accepted hardware or firmware.
- Documentation-only commits after this checkpoint are not evidence of newer runtime implementation.

## Unresolved issues / deferred

- Raised-front wedge preliminary footprint **83.1 mm depth / 106.1 mm height** (55°); differs from prior 55–75mm depth guess because of 20mm roof for upper LCD clearance; angle/case unapproved.
- Adafruit 377 included cap rejected aesthetically; **KZ0087 provisionally selected** to match low-profile RK M75 styling. Its 12.4 mm maximum insertion is shorter than Adafruit shaft's nominal 15 mm, so mechanical fit/encoder push still require validation. Encoder electronics unchanged.
- The Waveshare AW9523B silicon **defaults GPIO to outputs**; at the anticipated 0x58 straps P0 starts low open-drain, but **RESET has internal 100k pull-down**, so verify module's external reset pull-up and boot timing. Preliminary six-input 22k pullups + 1k series are **not an approved wiring schematic**. Module full diagram still inaccessible even though an indexed text copy identifies R1–R4 10k. See `docs/HARDWARE-ELECTRICAL-REVIEW.md`.
- Part availability is variable. The Adafruit AW9523 PID 4886 module was shown sold out in one checked supplier listing; Waveshare AW9523B SKU 22132 is a proposed same-chip breakout, not necessarily plug-and-play. User has not ordered hardware.
- GPIO/I²C warning: onboard CH422G reserves `0x20–0x27` and `0x30–0x3F`, so default MCP23017 (0x20+) and Adafruit **single** I²C rotary breakout (0x36–0x3D) conflict. AW9523 (0x58) and Adafruit **QUAD** seesaw breakout (0x49) are proposed alternatives; QUAD off-label 3 MX + encoder push switch contact use needs schematic/bench checks due to possible duplicated pin listing. No purchase approval.
- The device simulator can poll `/api/device/state` repeatedly even with SSE; optimization is deferred, not a blocker.
- A test emitted a minor `ResourceWarning` about a stylesheet file handle.
- Linux `playerctl -l` previously found no player in an SSH session, yet paired device state and Spotify API worked; avoid claiming native MPRIS parity without a local player test.
- Desktop Flask server is a development prototype, not an internet-facing deployment.
- Final independent Wi-Fi mode on physical hardware still needs a design decision: do not assume Spotify embedded playback or safe on-device OAuth storage is possible.

## Workflow rules

See `docs/CHATGPT-WORKFLOW.md`. Read repository state before changes. Distinguish implemented, statically tested, runtime-tested and accepted. Preserve 800×480 UI and accepted playback behavior. Record actual ad-hoc work without inventing roadmap numbers. Commit code directly through GitHub when permitted and update this handoff after each user-accepted task. Keep passwords, OAuth tokens, pairing bearer tokens and host-specific config out of Git.

# ChatGPT handoff — Spotify Desk Thing

> Current-state save point, not the full project history. **Read this first** in a new project conversation. Cross-check against the current branch and commits.

Updated: 2026-10-21

## Repository / checkpoint

- Repository: `Cousinsuke/Spotify-Desk`
- Default / current development branch: `main` (no alternate development branch established yet)
- Last source baseline: **Phase 5.2** source imported into `main` from checksum-checked ZIP; actual GitHub commit verified
- Latest implementation checkpoint: **`7172c2ee2f285253507b13c71acb7072adc04067`** (`feat: import accepted Phase 5.2 desktop and simulator baseline`, source commit). Later docs/script commits are not a newer application version.
- Handoff status: GitHub migration completed; 16 historical ZIPs archived at `f781506`. User uploaded the full Rev B package in [`6ae257e`](https://github.com/Cousinsuke/Spotify-Desk/commit/6ae257e2ce01256b320417fd21e14d9339bd9ed1): original ZIP and 13 extracted files. GitHub blob hashes matched the uploaded ZIP entries exactly. This is a CAD artifact checkpoint, not newer application code.
- GitHub access: connected read/write access was confirmed at bootstrap; verify access in future conversations

## Current project phase vs current actual work

- **Current project phase:** Phase 6 physical design research/CAD, no ESP32 firmware implemented.
- **Current actual work:** **Rev B design package is now tracked in GitHub** at [`mechanical/revB/cad/`](../mechanical/revB/cad/), with the [original source ZIP](../mechanical/revB/Spotify_Desk_RevB_CAD_Shared_Package.zip). Both sharp and R5-rounded cases, full reference assemblies, dimensioned DXF, four-page A3 PDF, preview images, Python CadQuery generator and JSON dimensions are preserved. User indicates these are the designs to continue from; no single exterior style or print-ready enclosure is definitively approved.
- **Rev B proposed dimensions:** **156 mm wide × 83.093 mm desk depth × 106.107 mm high**, 156×110 mm sloped face at 55° from desk, 16 mm front chin, 20 mm rear roof, 3 mm assumed wall. Rounded option is **R5 external edge fillets**; sharp option has crisp edges. LCD module X=8..114.1 mm, centre **61.05 mm**; 3 MX X centres **31.05, 61.05, 91.05** mm at V=91, exactly centred under module; 30 mm pitch; knob centre (138,44) mm, diameter 15.1. Gap knob rim to right face edge **10.45 mm**. Assumed 14 mm I2C right-side cable zone leaves just **3.30 mm assumed lateral encoder-body clearance**; **not a guaranteed physical fit**.
- **Status:** Reference STEP solids were reopened/checked, DXF reopened and A3 PDF rendered during design; GitHub files now byte-matched 13/13 with source ZIP. **Not fabrication geometry**: screw bores, full electronics/cable collisions, switch depths, USB openings and fasteners remain unverified. AW9523B RESET/pin mapping still open. No hardware purchase reported. Accepted software remains Phase 5.2 (`7172c2e`).

## Last accepted work

- **Most recent validated repository task:** Rev B package push (`6ae257e`) and GitHub-to-ZIP hash integrity verified. This is asset preservation and does **not** prove physical fit, firmware, or desktop runtime behaviour.
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

## Phase 6 Rev B component-fit review checkpoint (2026-10-21)

- Manufacturer board rear drawing, PEC11 encoder drawing, KZ0087 specs, and Cherry MX plate conventions reviewed. **No measured physical part in hand and no revised enclosure dimensions approved.** Right-side I2C plug remains the principal unknown; encoder's 5mm nominal threaded bushing and 3mm conceptual face require washer/nut assembly checking; common Cherry MX clips may require ~1.5mm local plate, not 3mm.
- Added **[`docs/HARDWARE-REV-B-FIT-REVIEW.md`](HARDWARE-REV-B-FIT-REVIEW.md)**; `mechanical/revB/cad/fit_audit.py`, `fit_coupons.scad` and `test_fit_audit.py`. Fit calculator: assumed I2C extension 14mm -> 3.3mm nominal X gap; if actual extension 20mm overlaps same V/Z region, 2mm trial guard would imply 160.7mm wider-case scenario (NOT a decision).
- **Validation:** 5 Python tests passed; OpenSCAD generated five conceptual mounting coupons without CSG errors in assistant environment. **Pending user testing:** print test samples, seat actual MX switches/encoder/knob and measure real Waveshare connector/cable. Both existing 156mm sharp/R5 STEP variants remain unchanged; no firmware/runtime work.

## Current next action

1. **Complete [the Rev B fit measurement gate](HARDWARE-REV-B-FIT-REVIEW.md): test MX/encoder coupons and measure the H7 I2C connector/cable, mount holes, port and Z envelopes. Only then alter the main sharp/R5 CAD models.** Both are retained as the current design baseline; choose a single outer edge style when ready to finalize. Neither is a production-approved case.
2. Use the [Rev B report](HARDWARE-WEDGE-REV-B-CAD.md), [coordinate notes](../mechanical/revB/README.md) and [checked-in CAD package](../mechanical/revB/cad/) as the source for mechanical edits. Rev A's 165mm OpenSCAD model is historical.
3. **Measure exact owned MX switches and caps**, screen mounting-hole bores, left USB-C service locations, right I2C plug and bend radius, true AW9523B and encoder/knob Z/depth, then perform real 3D collision analysis.
4. **Case engineering** still needed: 3D printable mounting lips and screw bosses, bottom-access hatch fasteners, key/switch tolerances and support, USB ports, screen and antenna keepouts, knob push travel and KZ0087 grub-screw access. Current STEP shell cutouts are placeholders.
5. **Electrical** still needed: AW9523B module RESET/pullup and safe 3.3V connector mapping, protected six input signals and encoder pulse tracking. If layout/electrical tests succeed, *then* consider compact carrier PCB. Firmware unchanged.

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
- 2026-10-20: wedge 3D Rev A packaging proposal + editable SCAD checked in to mechanical/, separate annotated rendered concept ZIP in conversation; purely geometric.
- 2026-10-21: **Rev B** 156mm wedge with centred MX keys; matched sharp/R5 STEP solids, assemblies, DXFs, A3 PDF and rendered previews produced. User pushed CAD ZIP plus all 13 extracted assets in `6ae257e`; remote blobs verified byte-for-byte. No physical test or software implementation change.
- Documentation-only commits after this checkpoint are not evidence of newer runtime implementation.

## Unresolved issues / deferred

- Current Rev B trial is **156×83.09×106.11 mm** (W×D×H), 55° slope and 16mm chin/20mm roof; width is reduced from Rev A 165mm. Proposed R5 round is an *option*, not a final user-accepted finish. 14mm assumed I2C corridor + encoder body leaves just 3.3mm theoretical lateral gap, real fit unknown.
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

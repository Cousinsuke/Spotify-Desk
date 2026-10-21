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
- **Rev B geometry (retained):** 156 mm width × 83.093 mm desk depth × 106.107 mm height, 55° sloped 156×110 mm face, 16mm chin, 20mm roof and assumed 3mm wall; either sharp or R5 edges. LCD origin X=8,V=8, screen centre X=61.05; centred MX keys X=31.05,61.05,91.05 at V=91; knob (138,44), Ø15.1mm. **Important correction from official STEP:** earlier right-I2C/left-USB orientation was taken from a **rear view** and is reversed from front viewing side. Manufacturer source shows **USB-C1/C2 on front RIGHT**, **I2C 4P header on front LEFT**. The earlier 3.3mm right-I2C/encoder gap is only an old hypothetical calculation; not the physical layout.
- **Status:** Reference STEP solids were reopened/checked, DXF reopened and A3 PDF rendered during design; GitHub files now byte-matched 13/13 with source ZIP. **Not fabrication geometry**: screw bores, full electronics/cable collisions, switch depths, USB openings and fasteners remain unverified. AW9523B RESET/pin mapping still open. No hardware purchase reported. Accepted software remains Phase 5.2 (`7172c2e`).

## Last accepted work

- **Most recent repository checkpoint:** User provided genuine official Waveshare STEP ZIP; ZIP SHA-256 independently matched, 31,338,066-byte STEP parsed using OpenCascade/XCAF (693 solids) and source sockets/standoffs inspected. An alignment/clearance reference was implemented with 10 locally passing Python tests; **user Windows testing of this new STEP-based tool pending**. Earlier 3D packaging tool has 8/8 user Windows tests passed. No actual physical fitting or firmware.
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
- **Validation:** Initial assistant-side 5 Python tests passed and OpenSCAD rendered the five conceptual coupons. **User independently confirmed a clean Windows 11 PowerShell pull of `fd82d35`, successful `fit_audit.py` output for 14/17/20/25mm hypothetical cables, and all five `unittest` checks passing** (`Ran 5 tests in 0.002s / OK`). This is **Windows script execution only**, not a Windows companion runtime test, electronics or printed-part validation. The user confirmed we are **still at the design stage**, so no actual parts/coupon prints or measured assembly are available. Both existing 156mm sharp/R5 STEP variants unchanged.

## Phase 6 Rev B internal 3D packaging study — 2026-10-21 (awaiting Windows validation)

- Independent CAD-only packaging study added via `mechanical/revB/cad/internal_packaging.py`, `internal_packaging_view.scad`, `internal_packaging_assumptions.json`, synchronised OpenSCAD parameter file and `test_internal_packaging.py`. Guide: [3D packaging study](HARDWARE-REV-B-INTERNAL-PACKAGING.md). Both original 156mm sharp and R5 STEP cases remain **unchanged**.
- This study maps X/V/inward-W reference boxes onto desk-space wedge coordinates. It models provisional LCD, MX keys, encoder/terminal prism, right I2C and left USB cable envelopes, nominal screen mounting markers, AW9523B historical arbitrary position and hatch clearance; no accurate R5 shell or actual connector model.
- **User Windows validation:** eight new 3D packaging unit tests passed (8/8, 0.014s). User ran `--verify-defaults` 14mm I2C/6mm USB successfully and generated a 20mm I2C/10mm USB scenario. Hypothetical body overlap (2.7×13.2×13.1mm), terminal overlap (2.7×13.2×0.9mm), and left wall encroachments (-1mm and -5mm) matched expectations. This confirms Windows Python execution, **not** real hardware or OpenSCAD visual inspection.
- Default **assumed** 14mm I2C cable projection: 3.3mm nominal X gap to encoder; 20mm scenario produces a **2.7mm X × 13.2mm V × 13.1mm W hypothetical box overlap**. An assumed 6mm left USB cable projection reaches 1mm inside nominal side wall, suggesting a future port-opening or cable-route decision; not measured or confirmed. No case width revision authorised.

## Waveshare official 3D reference discovery — 2026-10-21

- Official [Waveshare hardware resources](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Resources-And-Documents) list a [3D Drawing ZIP](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip). This could reduce guessed LCD board/USB/I2C positions. The ZIP contents, model resolution, touch SKU match and licence are **unverified**; don't assume exact connectors or dimensions.
- Added [`scripts/inspect-waveshare-3d-reference.ps1`](../scripts/inspect-waveshare-3d-reference.ps1) to download the manufacturer's ZIP **outside the repository** and list its members/size/SHA-256; optional `-Extract`. This script has not been executed on Windows yet and no third-party CAD is checked into our public repo.

- **Windows manufacturer archive inspection completed by user (2026-10-21):** `scripts/inspect-waveshare-3d-reference.ps1 -Extract` ran successfully after pulling `8a67325`. Archive path: `$HOME\Downloads\SpotifyDesk-Waveshare-Official-3D\ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip`; **ZIP size 5,677,592 bytes**, reported **SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`**; exactly one entry `esp32-s3-touch-lcd-4_3.stp` (**31,338,066 uncompressed bytes**). Extracted under adjacent `extracted\`. These are **user-reported output values**, not yet independently audited STEP geometry. Direct assistant download was unavailable. Request the **original manufacturer ZIP uploaded into the chat** to inspect full assembly, its coordinate system, connectors, SKU compatibility and whether it has usable mounting/detail geometry. Do not upload it to public GitHub or overwrite the Rev B cases without review.

## Manufacturer STEP geometry checkpoint — 2026-10-21

- User uploaded manufacturer `ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip`; CRC and SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15` independently matched. Sole STEP `esp32-s3-touch-lcd-4_3.stp` 31,338,066 bytes, Creo dated 2023-12-13, **693 solids**, overall bounds **106.106 × 68.268 × 16.906mm**.
- [Detailed STEP findings](HARDWARE-WAVESHARE-STEP-INSPECTION.md) plus [`waveshare_step_reference.json`](../mechanical/revB/cad/waveshare_step_reference.json), [`manufacturer_fit_compare.py`](../mechanical/revB/cad/manufacturer_fit_compare.py), [annotated front overlay](../mechanical/revB/cad/waveshare_step_front_overlay.svg), and 10 passing local tests. This adds only *extracted named bounding measurements and tool code* to GitHub, **not** Waveshare raw STEP/ZIP.
- **Critical front-view orientation correction:** STEP +Z faces viewer; USB-C1 and USB-UART Type-C2 housings on right by encoder, H7 four-pin I2C on left by close side wall. Earlier `fit_audit.py` and `internal_packaging.py` represented mirror-imaged **hypothetical** connector sides. Manufacturer STEP measures 17.544mm bare USB-C1-to-encoder body X gap, and 5.577mm H7-to-left-inner-wall X gap. Assumed 20mm USB extension would produce 2.456×8.327×4.162mm possible box intersection; assumed 6mm H7 I2C extension reaches 0.423mm inside assumed left inner wall. Actual cables/plug paths **unmodelled**. 98×60mm standoff pitches measured in STEP; vendor revision/hole/thread not validated.
- Complete manufacturer depth is **16.906mm**, not earlier 6.8mm assumed rear LCD-depth box; align glass front W=0 as *provisional* and design case supports after mounting datum is chosen. No sharp/R5 original STEP enclosure modified, no finished printable case, no hardware ordered.

## Physical 180° board-rotation concept — 2026-10-21 (unapproved alternative)

- User's Windows 11 report independently confirmed the **STEP front-view comparator 10/10 tests** and both default (USB 14mm, I2C 6mm) and longer-cable (USB 20mm, I2C 10mm) runs; user opened generated SVG. These confirm the current *normal* view tool on Windows, **not** actual geometry fit.
- User suggested **rotate entire Waveshare module 180° within the front plane**, then rotate pixel output and capacitive touch in firmware. Waveshare docs specify **USB-C 5V power** and distinguish main USB from separate USB-to-UART debug. Physical 180° would put **main USB-C1/C2 on case LEFT** and **I2C H7 on case RIGHT**, while keeping glass outward, 156mm case, 98×60 mounts and centred keys. Firmware is not implemented/tested.
- Added [parametric side-by-side orientation study](HARDWARE-WAVESHARE-ROTATION-180-STUDY.md), `mechanical/revB/cad/orientation_180_study.py`, `test_orientation_180_study.py`, and checked-in `orientation_180_comparison.svg`. **Twelve assistant-side regression tests pass**; user Windows test/approval of the new study pending. Original sharp/R5 STEP enclosure variants and the earlier original-orientation reference remain untouched.
- **Design implications from manufacturer bounding boxes:** the main USB-C housing on left would be ~5.244mm inside nominal X=3mm inner wall; a trial 14mm outward plug extension extends **8.756mm through that nominal wall**, calling for a designed left-side access tunnel/port. H7 I2C housing on right is ~17.877mm horizontally from assumed encoder body; 20mm I2C straight-prism assumption can intersect encoder. Visible LCD window shifts down V **4.74mm**, right X **0.10mm**: existing display aperture must relocate in a *future alternative* case variant. Existing 18mm keycaps still have ~10.55mm gap to nominal visible window. Mount pitch still 98×60.
- The 180° mapping at 800×480 could use conceptual touch mapping (x,y)->(799-x,479-y), but LCD RGB/LVGL render and GT911 touch alignment/performance require actual ESP32 test. No physical parts bought and no fabrication/port-opening decision accepted.

## Current next action

1. **Review the new [original vs 180° physical board orientation comparison](HARDWARE-WAVESHARE-ROTATION-180-STUDY.md) on Windows**, including the left-side USB tunnel/connector scenario and revised 4.74mm display viewing-window offset. User has proposed 180° but has **not selected it**; if accepted, make a *separate* rotated Rev B enclosure prototype rather than overwrite sharp/R5 CAD. Plan ESP32/LVGL RGB display and GT911 touch rotation verification as later hardware test.
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

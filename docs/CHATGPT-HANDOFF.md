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

- **Current project phase:** Phase 6 — hardware research, compatibility decisions and first firmware design (**planned, not implemented**)
- **Current actual work:** Phase 6 **pre-purchase verification** of user-confirmed *proposed* hardware: **Waveshare 25948** capacitive touch screen + **Adafruit 377** momentary-push encoder + **Waveshare AW9523B 22132** expander. User agreed to verify wiring, voltage and fit before buying. Manufacturer schematic/datasheet checks completed, but expansion board schematic, safe startup wiring and enclosure fit remain open. Roadmap hardware-research task, not firmware implementation.
- **Status:** Phase 5.2 software unchanged, source checkpoint `7172c2e`. User-selected *proposed* physical component trio documented in **docs/HARDWARE-PRE-PURCHASE-CHECK.md**. Screen physical module **106.1×67.8 mm**, visible drawing **95.54×54.36 mm**, ~98×60 mm screw-center spacing; Adafruit encoder 377 has ~13.2 mm body, M7×0.75 threaded bushing, short momentary switch travel; kit knob family drawing ~16 mm diameter. AW9523B 22132 is 38×23 mm, nominal 0x58 I²C, 3.3 V capable; module-specific reset/pullup and electrical safety still need schematic. Current case sketch likely crowds the LCD rear PCB. No purchase, wiring or hardware runtime test.

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

1. **Read docs/HARDWARE-PRE-PURCHASE-CHECK.md** before recommending a wiring kit. User's proposed screen/encoder/expander parts are **Waveshare 25948 + Adafruit 377 + Waveshare AW9523B 22132**; treat them as research-selected, not purchased or proven.
2. **Electrical blocker:** retrieve/check the exact **AW9523B module schematic**, especially reset pullups, I²C pullups/voltage domains, address straps and GPIO default outputs on power-up. Draw a reviewed 4-wire screen I²C to 6-wire expander harness and safe switch-input bias/current-limit plan; verify 3.3 V selector. Do not issue plug-by-color/soldering instructions yet.
3. **Case-fit blocker:** revise original mockup with full **106.1×67.8 mm** LCD PCB footprint (rather than visible 95.54×54.36 mm), ~98×60 mm mounting pitch, and bottom/side bezels. The 18 mm MX caps directly below display and ~18 mm right knob may compete for PCB/encoder body space. Develop an explicit 3D cross-section and mounting study before printing; tentative faceplate exploration 140–150×100–110 mm is only an estimate.
4. **Encoder check:** Adafruit 377's linked PEC11 drawing says **M7×0.75 mounting bushing**, **15 mm shaft (part code)**, 6 mm D shaft, 13.2 mm body and **0.5±0.2 mm momentary switch travel**. Linked included 450-BA761 knob drawing shows **~16 mm outside diameter**, so it can plausibly replace an 18 mm sketch circle; confirm actual kit knob after receipt.
5. When mechanical and electrical issues are resolved, make a separately approved prototype procurement checklist and then bench-validate I²C address, six inputs, rotary at speed and screen+Wi-Fi simultaneous operation. Phase 5.2 app unchanged; independent firmware work still future.

## Relevant project files (from Phase 5.2 source)

- `desk_ui.py`, `device_bridge.py`
- `windows_companion.py`, `linux_companion.py`
- `static/ui.js`, `static/ui.css`, `static/device.js`, `static/device.css`
- `templates/index.html`, `templates/device.html`, `templates/pair.html`
- `tests/`, `requirements-ui.txt`, `requirements-windows.txt`
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, **`docs/DESIGN.md`**, `docs/HARDWARE.md`, **`docs/HARDWARE-SHORTLIST.md`**, **`docs/HARDWARE-PRE-PURCHASE-CHECK.md`**, `docs/HARDWARE-RESEARCH.md`, `docs/HARDWARE-COMPARISON.md`, `docs/CHATGPT-WORKFLOW.md`
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
- Documentation-only commits after this checkpoint are not evidence of newer runtime implementation.

## Unresolved issues / deferred

- The Waveshare AW9523B silicon **defaults all GPIO to outputs** before software config: avoid directly grounding contacts without validated startup/current-limit protection. Manufacturer module schematic was not accessible through research interface; check it prior to soldering. Exact connector and reset wiring remain unproven.
- Part availability is variable. The Adafruit AW9523 PID 4886 module was shown sold out in one checked supplier listing; Waveshare AW9523B SKU 22132 is a proposed same-chip breakout, not necessarily plug-and-play. User has not ordered hardware.
- GPIO/I²C warning: onboard CH422G reserves `0x20–0x27` and `0x30–0x3F`, so default MCP23017 (0x20+) and Adafruit **single** I²C rotary breakout (0x36–0x3D) conflict. AW9523 (0x58) and Adafruit **QUAD** seesaw breakout (0x49) are proposed alternatives; QUAD off-label 3 MX + encoder push switch contact use needs schematic/bench checks due to possible duplicated pin listing. No purchase approval.
- The device simulator can poll `/api/device/state` repeatedly even with SSE; optimization is deferred, not a blocker.
- A test emitted a minor `ResourceWarning` about a stylesheet file handle.
- Linux `playerctl -l` previously found no player in an SSH session, yet paired device state and Spotify API worked; avoid claiming native MPRIS parity without a local player test.
- Desktop Flask server is a development prototype, not an internet-facing deployment.
- Final independent Wi-Fi mode on physical hardware still needs a design decision: do not assume Spotify embedded playback or safe on-device OAuth storage is possible.

## Workflow rules

See `docs/CHATGPT-WORKFLOW.md`. Read repository state before changes. Distinguish implemented, statically tested, runtime-tested and accepted. Preserve 800×480 UI and accepted playback behavior. Record actual ad-hoc work without inventing roadmap numbers. Commit code directly through GitHub when permitted and update this handoff after each user-accepted task. Keep passwords, OAuth tokens, pairing bearer tokens and host-specific config out of Git.

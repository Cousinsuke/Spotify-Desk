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
- **Current actual work:** Phase 6 follow-up research: compare Waveshare 4.3/4.3B/4.3C screens and input-expansion strategies, including ready-made AW9523 and a possible combined four-key/one-encoder QUAD seesaw controller. Roadmap research, not implementation, **awaiting user decision**.
- **Status:** Phase 5.2 source at `7172c2e`, 16 archives at `f781506`; software unchanged. Research reports `docs/HARDWARE-RESEARCH.md` and `docs/HARDWARE-COMPARISON.md` compare exact boards, GPIO conflicts, and four-switch+encoder options. Hardware not selected/accepted, purchased or bench tested.

## Last accepted work

- **Most recent validated repository task:** current Phase 5.2 source import and all 16 historical ZIP imports to GitHub; both commits verified from the remote repository; local `git status --short` clean. This is repository housekeeping, not new app runtime validation.
- **Most recent accepted:** Phase 5.2 device/PC artwork reliability fix on **Omarchy**; user confirmed the fix worked and ran **39 Python tests**, all passing.
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
- Final Waveshare board SKU, connector/pinout, input expander and electrical verification, case and encoder/switch placement. Research favors original touch SKU **25948**, but user has not accepted a final board.
- Real cross-platform end-to-end device simulator testing over separate physical LAN clients; Linux and Windows post-import revalidation.

## Current next action

1. Discuss **compact standard Waveshare 25948 (270 nits)** versus **larger/brighter 27848 4.3B (550 nits)**; 4.3C audio variant only if needed. Avoid prematurely selecting/ordering.
2. Compare **Adafruit AW9523 (0x58)** six-input polling with external bias resistors against **Adafruit I²C QUAD rotary breakout (0x49)** proposed off-label layout using one encoder and four separate switch pads. QUAD schematic/pinout has a possible duplicate pin number and must be bench-verified before use. Both avoid Waveshare CH422G reserved addresses.
3. If preferred, settle an experiment plan: check exact I²C bus 3.3 V jumper, shared SDA/SCL, connector adapter, mechanical space and encoder responsiveness before committing to firmware/wiring.
4. Keep Phase 5.2 post-import Windows/Omarchy runtime retest and LAN protocol hardening as separate pending work.

## Relevant project files (from Phase 5.2 source)

- `desk_ui.py`, `device_bridge.py`
- `windows_companion.py`, `linux_companion.py`
- `static/ui.js`, `static/ui.css`, `static/device.js`, `static/device.css`
- `templates/index.html`, `templates/device.html`, `templates/pair.html`
- `tests/`, `requirements-ui.txt`, `requirements-windows.txt`
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/HARDWARE.md`, **`docs/HARDWARE-RESEARCH.md`**, **`docs/HARDWARE-COMPARISON.md`**, `docs/CHATGPT-WORKFLOW.md`
- One-time import scripts: `scripts/import-phase5-2.ps1` (already run) and `scripts/archive-local-phases.ps1` (already run). Historical files: `archives/phase-zips/` and `docs/history/ARCHIVED-PHASE-ZIPS.md` (16 verified archives and their original/stored hashes).

## Recent meaningful commits

- `7172c2e` — accepted Phase 5.2 source imported into `main` (**implementation checkpoint**).
- `234a976` — sanitize generated Python bytecode when preserving old ZIPs.
- `f781506` — all 16 historical ZIP archives and checksum manifest pushed and verified.
- `196a66a` — Phase 6 WaveShare board/expander manufacturer-source research (documentation only; no application or firmware changed).
- `5833f0e` — Phase 6 extended screen/input-expander comparison; includes AW9523 and QUAD seesaw ideas (documentation only).
- Documentation-only commits after this checkpoint are not evidence of newer runtime implementation.

## Unresolved issues / deferred

- GPIO/I²C warning: onboard CH422G reserves `0x20–0x27` and `0x30–0x3F`, so default MCP23017 (0x20+) and Adafruit **single** I²C rotary breakout (0x36–0x3D) conflict. AW9523 (0x58) and Adafruit **QUAD** seesaw breakout (0x49) are proposed alternatives; QUAD off-label four-MX-switch use needs schematic/bench checks due to possible duplicated pin listing. No purchase approval.
- The device simulator can poll `/api/device/state` repeatedly even with SSE; optimization is deferred, not a blocker.
- A test emitted a minor `ResourceWarning` about a stylesheet file handle.
- Linux `playerctl -l` previously found no player in an SSH session, yet paired device state and Spotify API worked; avoid claiming native MPRIS parity without a local player test.
- Desktop Flask server is a development prototype, not an internet-facing deployment.
- Final independent Wi-Fi mode on physical hardware still needs a design decision: do not assume Spotify embedded playback or safe on-device OAuth storage is possible.

## Workflow rules

See `docs/CHATGPT-WORKFLOW.md`. Read repository state before changes. Distinguish implemented, statically tested, runtime-tested and accepted. Preserve 800×480 UI and accepted playback behavior. Record actual ad-hoc work without inventing roadmap numbers. Commit code directly through GitHub when permitted and update this handoff after each user-accepted task. Keep passwords, OAuth tokens, pairing bearer tokens and host-specific config out of Git.

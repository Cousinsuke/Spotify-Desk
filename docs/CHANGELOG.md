# Changelog / version history

This is **historical milestone tracking**, not a separate implementation branch for each ZIP. The accepted Phase 5.2 source is committed at `7172c2e`; historical ZIPs are reference snapshots only. Prefer Git commits, tags and releases for future work rather than duplicated source folders.

## Manufacturer Waveshare STEP analysed and front/rear corrected — 2026-10-21
- Uploaded original Waveshare source ZIP independently hashed/CRC-verified; OCCT imported the single 31.34MB Creo STEP and located 693 solid bodies, the two USB-C sockets, 4-pin I2C socket, four M2.5-named standoffs and actual overall 3D assembly bounds.
- Corrected earlier **front-vs-rear mirrored connector placement**: front USB-C1/C2 RIGHT toward encoder, I2C four-pin LEFT toward inner left sidewall. Archived old scenario scripts are explicitly labelled historical hypotheses.
- Added extracted measured part boxes (no third-party CAD redistribution), front-layout SVG, pure Python cable/shell clearance scenarios and 10 passing local tests. Neither sharp nor rounded Rev B STEP design has been modified; no physical fit or Windows execution of the new tool confirmed.

## Manufacturer STEP download confirmed on Windows — 2026-10-21
- User ran the new PowerShell inspection helper after successful Git pull; downloaded official Waveshare ZIP (5,677,592 bytes, SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`) and extracted the sole STEP `esp32-s3-touch-lcd-4_3.stp` (31,338,066 bytes).
- ZIP member listing is now confirmed by user PowerShell output, but **the actual STEP model has not been opened or analysed**, touch SKU 25948/PCB revision alignment remains open. Manufacturer bytes stay outside GitHub pending rights/fit review.

## Rev B Windows tests and official manufacturer CAD discovery — 2026-10-21
- User confirmed `internal_packaging.py` generates expected nominal and expanded cable scenarios on Windows; **8/8 Python tests passed**. No physical assembly, electrical or OpenSCAD user visual test accepted.
- Waveshare publishes an official 3D Drawing ZIP for the original ESP32-S3-Touch-LCD-4.3 model. Added a PowerShell archive downloader and listing tool with SHA-256; keeping manufacturer models separate from the repository until exact contents, revisions and distribution terms are checked.

## Rev B internal packaging model (design-only) — 2026-10-21
- Added Python standard-library 3D envelope collision report, configurable right I2C and left USB scenarios, OpenSCAD reference scene, assumptions JSON, SCAD parameters and eight tests.
- Assistant environment: 8 Python tests passed and OpenSCAD CGAL generated geometry without errors. Original sharp/R5 STEP reference designs unchanged; user Windows validation still pending.
- Trial 20mm I2C reach overlaps a nominal encoder reference prism; provisional left USB extension enters nominal wall. These are **unmeasured box assumptions**, not physical collisions or a dimension decision.

## Rev B Windows fit-audit validation — 2026-10-21
- User pulled commit `fd82d35` on Windows 11 and ran the Rev B Python clearance auditor successfully; 14/17/20/25mm scenarios reported the expected nominal 3.3/0.3/−2.7/−7.7mm gaps.
- User's Windows 11 Python ran all **5 fit-audit unit tests successfully**; this validates the calculation tooling on Windows, **not** physical CAD fit or the desktop media companion.
- User explicitly confirmed the project is **still designing**. Next mechanical task is parameterized 3D packaging/keep-out exploration using clearly marked assumptions; no real-world measurement or hardware purchase claimed.

## Rev B component-fit preparation — 2026-10-21
- Reviewed manufacturer LCD rear board/connectors, Bourns PEC11 encoder mounting geometry, KZ0087 specs and standard Cherry MX plate cutouts.
- Added a pure-Python cable-clearance scenario audit, explanatory vector overlay export, five OpenSCAD mounting coupons, five regression tests and a measured-fit checklist. The script retains original 156mm Rev B dimensions; no existing STEP assemblies changed.
- Static validation: five Python tests passed; OpenSCAD produced valid coupon geometry. No measurements, physical parts, print trials or final manufacturer tolerance confirmation yet.

## Rev B CAD package archived on GitHub — 2026-10-21
- User pushed [`6ae257e`](https://github.com/Cousinsuke/Spotify-Desk/commit/6ae257e2ce01256b320417fd21e14d9339bd9ed1) containing the original Rev B ZIP and 13 extracted STEP, DXF, PDF, PNG, generator and metadata files to `mechanical/revB/`.
- Verified that all 13 GitHub blobs match the original ZIP's entries byte-for-byte. Added `.gitattributes` to prevent Windows CRLF conversion of CAD and binary data on future checkout.
- Both sharp and R5-rounded variants retained as concept geometry; no final manufacturing signoff, wiring or firmware test.

## Repository migration — 2026-10-20
- Imported exact accepted Phase 5.2 desktop/simulator source into `main`: commit `7172c2e`.
- Uploaded 16 historical ZIP archives with SHA-256 manifest: commit `f781506`.
- Omitted 2 generated Python bytecode/cache entries from archived Phase 2.2 ZIP; originals in Downloads unchanged.
- GitHub source and archives verified; this housekeeping work is not a new software phase or hardware runtime validation.

## Phase 5.2 — Last user-accepted prototype on Omarchy (2026-10-20)
- PC artwork reliability: preserve direct HTTPS cover URLs from MPRIS; use local thumbnail proxy only when applicable.
- Validate artwork key against current track; bounded retries and fallback cover; delayed Windows artwork retry.
- 39 Python tests passed on Omarchy; user confirmed issue resolved.
- Windows Phase 5.2 specific retest still to do.

## Phase 5.1 — Simulator design restoration
- Restored established 800×480 screen layout, album glow, proper speaker icon/slider and optimistic playback/skip feedback.
- Preserved device pairing and K1–K4 + encoder simulation.

## Phase 5.0 — Virtual hardware and pairing
- Added `/device`, `/pair`, pairing tokens, authenticated state/control/events bridge and optional restricted `--lan`.
- Public Spotify Client ID persisted locally via `--configure`.

## Phase 4.2 — Spotify volume routing
- Synchronized PC Spotify volume with matching Spotify Connect playback.
- SYSTEM fallback for other/unmatched player sessions; Windows and Omarchy user-accepted.

## Phase 4.1 — Linux companion
- MPRIS/playerctl, PipeWire default volume and monitor integration; initial Omarchy tests.

## Phase 3.3 — Windows audio stream
- Replaced high-frequency HTTP audio polling with SSE stream; Windows user-accepted.

## Phase 3.1–3.2 — Windows companion & dependencies
- Native media sessions, playback, output volume and audio signal capture; added missing WinRT Collections dependency.

## Phase 2.1–2.7 — Browser UI
- 800×480 music player, Spotify controls, skip feedback, audio/album-colour glow, and glow confinement.

## Phase 1 — Initial prototype
- Spotify developer application using PKCE; basic browser API controls.

## Future versioning

The Phase 5.2 source checkpoint exists at `7172c2e` and was imported with a checksum-verified source archive. Consider tagging only after confirming platform tests from the checked-in repository. For future changes, use normal Git history and release artifacts instead of reconstructions of older snapshots.

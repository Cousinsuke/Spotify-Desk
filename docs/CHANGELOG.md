# Changelog / version history

This is **historical milestone tracking**, not a separate implementation branch for each ZIP. The accepted Phase 5.2 source is committed at `7172c2e`; historical ZIPs are reference snapshots only. Prefer Git commits, tags and releases for future work rather than duplicated source folders.

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

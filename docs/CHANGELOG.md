# Changelog / version history

This is **historical milestone tracking**, not a claim that all archives or commit history are already in Git. Once source is imported, use Git commits/tags and normal releases rather than keeping duplicated code folders.

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

Create a source checkpoint for accepted Phase 5.2, then tag it as a **prototype** only after confirming repository contents match the validated archive. Keep major historical versions as Git history or release artifacts; don't reconstruct old snapshots from guesswork.

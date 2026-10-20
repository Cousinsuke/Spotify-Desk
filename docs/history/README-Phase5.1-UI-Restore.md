# Phase 5.1 — Restore the full 800×480 player in the hardware simulator

This patch addresses the Phase 5.0 simulator's visual and interaction regression. The original `/` console, Spotify auth, Windows/Omarchy companion and device pairing are retained.

## Changes

- `/device` now shares `/static/ui.css` with the established player. Reuses its fixed 800×480 visual composition, album art dimensions, Spotify-green controls, proper SVG Play/Pause/Previous/Next, visible speaker icon and input slider.
- `/device` reuses the established album-art colour sampling and audio-reactive glow (PC with audio-meter events; timed breathing fallback if the meter is unavailable). The Wi-Fi mode is Spotify API mode and does not stream raw audio.
- Immediate Play/Pause icon updates and pending-track feedback. The new screen keeps the 'Skipping track…' state until new metadata is confirmed or a safety timeout expires. A small number of follow-up state requests help refresh after commands; the backend still enforces its shared Spotify polling/cache and rate-limit controls.
- The simulator retains K1–K4, the rotary encoder, pairing and PC/Wi-Fi mode selection. Adds a touchscreen volume slider.
- The device LAN allowlist now includes only the shared static CSS required by the simulator. All original dashboard, OAuth, and PC/Spotify control routes remain loopback-only.
- Versioned simulator assets `?v=5.1` force browsers to load the restored UI.

## Install on Windows

1. Stop any running Desk Thing server with Ctrl+C.
2. Extract `spotify-desk-thing-phase5-1.zip` into `~/Projects/Display-Spotify-Desk-Thing` (same root directory used by Phase 5.0), overwriting project files. Do not remove `.venv`, `.spotify_token.json`, `.desk_devices.json`, or your saved Client ID.
3. Start using `.\\.venv\\Scripts\\python.exe .\\desk_ui.py`. Visit `http://127.0.0.1:8888/device`, hard-refresh (`Ctrl+F5`). Existing pairing should remain.

## Install on Omarchy over SSH

1. Transfer the ZIP with `scp` from Windows to `cousinsuke@tuf-linux:~/`.
2. Stop the Linux server, then `cd ~/Projects/Display-Spotify-Desk-Thing` and `unzip -o ~/spotify-desk-thing-phase5-1.zip`.
3. Run `./.venv/bin/python desk_ui.py`. Use your existing SSH port forward to view `/device` if desired.

## Test

- Confirm the screen looks like the main player at `/` (rather than the Phase 5.0 simplified design).
- Confirm play/pause updates immediately and Next/Previous show a pending state until the media player reports the change. The PC backend has fast local media detection; Wi-Fi/Spotify API requests can still take longer because of Spotify's remote service and API latency.
- Confirm album artwork colours and the PC audio meter alter the ambient glow, and the speaker icon / volume slider appear.
- Verify Wi-Fi and PC mode transitions, volume changes in Spotify, and K1–K4 and knob.

## Testing and limitations

- Python source syntax compilation, Node JavaScript syntax check, six dependency-free regression tests, and a headless Chromium smoke test using simulated media endpoints passed in the build environment.
- Live Spotify, PipeWire, WinRT and physical ESP32 hardware are not available in the build environment. Confirm behaviour on Windows and Omarchy before marking Phase 5.1 validated.
- Existing pairing data is preserved by the ZIP; no re-pairing should be required unless you previously revoked the device or cleared browser storage.
- Only use `--lan` on a trusted LAN. The pairing protocol still uses HTTP in this prototype; it should be encrypted before production deployment.

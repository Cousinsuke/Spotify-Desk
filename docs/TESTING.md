# Validation and acceptance

Never conflate **implemented**, **statically checked**, **runtime-tested**, and **user-accepted**.

## Accepted evidence

- **2026-10-25 multi-dashboard browser preview, Windows 11:** user screenshot-validated Home/clock, all four screen tabs, paired PC status, live **Bournemouth Open-Meteo** current/hourly weather data, and a prominently marked sample-only Libre glucose graph at 6h. User stated it looks like it works. This is visual/browser acceptance of the preview, **not** live CGM integration, actual media-control tests, switching glucose ranges, Omarchy or ESP32 validation.
- **2026-10-25 Windows regression run:** Python 3.13 venv, 44 tests, **42 pass / 2 errors** (`test_linux_companion.test_empty_player_list` and `.test_spotify_track`; Linux-only adapter invoked on Windows, resulting in `KeyError: has_playback`). Dashboard-specific tests and device LAN allowlist test passed. `node --check static/desk-dashboard.js` succeeded. Nonfatal file-handle ResourceWarnings appeared. A cross-platform test-selection fix is deferred; do not claim the whole suite passes.
- **2026-10-25 Spotify OAuth:** `client_id: Invalid` seen on original `/` login, independent from paired PC device simulator. Spotify app/client ID verification still needed before claiming Spotify Wi-Fi playback functioning on this new Windows checkout.

- Phase 4.2: user confirmed PC/Wi-Fi and Spotify volume synchronization on **Windows and Omarchy**.
- Phase 5.1: browser simulator UI shown and refined after design regression.
- Phase 5.2: Omarchy tests returned **39 passed**; user confirmed artwork did not become stuck. The log no longer contained repeated artwork-404 responses during the recorded test.
- Phase 5.2 Windows post-patch runtime: **not explicitly confirmed**.
- Real ESP32 hardware: **not tested or assembled**.

## Commands

```bash
python -m unittest discover -s tests -v
python -m py_compile desk_ui.py device_bridge.py linux_companion.py windows_companion.py
```

For UI: `node --check static/ui.js` and `node --check static/device.js` where Node is available. CI/static checks do not replace user testing.

## Runtime smoke test

1. Start Spotify playback and confirm title/artist, album art and progress.
2. Test Wi-Fi play/pause/next/previous/Connect volume.
3. Test PC native playback and correct `SPOTIFY` vs `SYSTEM` volume routing.
4. Open `/pair`, pair `/device`, test 4 keys, encoder, pairing persistence and revocation.
5. Skip multiple tracks; ensure correct/fallback artwork, no permanent `404` loop.
6. Check output-reactive glow, clipped background and browser icon consistency.
7. Repeat on Windows and Omarchy; test SSH-tunnel and opt-in real LAN clients separately when needed.
8. Record each environment, observed result, log excerpts, and user acceptance in handoff.

## Known quality debt

- `/api/device/state` can be polled repeatedly despite device SSE.
- A ResourceWarning for an unclosed stylesheet in one test.
- Linux MPRIS state under SSH may have no running media player.

# Software architecture

## Components

```text
Spotify Connect / Web API
          |
     Spotipy PKCE
          |
   desk_ui.py (Flask)
       |         +-- device_bridge.py --> /pair + /device + authenticated SSE/API
       |                                    |
       +-- Windows adapter                  +-- browser hardware simulator
       |   windows_companion.py                  four switches, encoder, screen
       |   Windows Media Control / pycaw / SoundCard
       |
       +-- Linux adapter
           linux_companion.py
           playerctl (MPRIS) / wpctl / pactl / parec
```

The planned ESP32 device will be a **new consumer of a versioned, security-reviewed device protocol**; it does not run the Python/Flask code.

## Key source areas in Phase 5.2

| Component | Responsibility |
|---|---|
| `desk_ui.py` | Flask server, Spotify API PKCE, routes, platform adapter selection |
| `device_bridge.py` | Pairing state, device commands, token auth, SSE, artwork proxy |
| `windows_companion.py` | Windows SMTC/GSMTC metadata, native commands, local output volume and audio levels |
| `linux_companion.py` | Local MPRIS/playerctl metadata/commands, default output, audio monitor |
| `static/ui.js` and `static/ui.css` | Main 800×480 desktop player |
| `static/device.js` and `static/device.css` | Paired browser hardware simulator, controls and glow |
| `templates/` | Desktop player, simulator and pairing UI |
| `tests/` | Unit and simulated integration regressions |

## Boundaries

- **Wi-Fi:** Spotify Web API state; updates cached to avoid excessive API traffic.
- **PC:** local OS media-session state; Spotify volume is used only when playback matches.
- **Audio meter:** local output amplitude levels, not saved or streamed raw audio.
- **Device API:** bearer-authenticated state/command/stream; opt-in private LAN access.
- **Local desktop/OAuth API:** loopback only.

## Important implementation limits

- Current browser simulator is *not ESP32 firmware*.
- An HTTP `200` for a control request means the endpoint returned successfully, not proof of perceived audio output; test in the real target environment.
- LAN protocol, pairing and token storage need a security review before real hardware.
- Old client/browser caches can display stale UI; verify JS/CSS version query and hard refresh before diagnosing regressions.

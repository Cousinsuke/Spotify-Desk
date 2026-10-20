# Spotify Desk Thing — Phase 5.0 (virtual hardware + paired local-network bridge)

Phase 5 extends **Phase 4.2** without changing the main 800×480 browser desktop UI or its Windows/Omarchy media controls.

## What this milestone tests

- A second browser acts like the planned ESP32-S3 touchscreen plus **four mechanical switches** and a **rotary encoder**.
- The simulated device can pair with a running companion, read current track / artwork / progress / volume, switch between PC and WI-FI modes, and send media commands.
- The device state is delivered over one **authenticated SSE** stream (PC status about every 0.9 s, Spotify state about every 2.5 s but with the existing ~5 s cached Spotify API refresh). The PC sound-level snapshots are multiplexed on the same stream, about every 150 ms; raw sound samples are never transmitted.
- Pairing uses a 6-digit code valid for **10 minutes**, **single use**, plus a 256-bit persistent bearer token. There is a 5-attempt / 15-minute limit per source address. Up to eight devices may be paired. Tokens can be revoked from a local-only page.
- Spotify Client ID is saved **locally** so you don't reenter it after reboot. It is a public client identifier, not a client secret. Spotify authorization tokens remain in the existing `.spotify_token.json` file.
- `--lan` is **opt-in**. Even in LAN mode, the main Spotify OAuth page and original desktop/control endpoints stay accessible only through loopback.

This is **software proof-of-concept**. No ESP32 firmware, USB/serial pairing, bootloader, on-device Spotify authentication or final hardware protocol implementation is included yet. In WI-FI mode the simulator calls the **companion's Spotify API session**; a disconnected, fully standalone physical device is a later phase.

## Windows 11 — local simulator first

Stop the existing 4.2 server with Ctrl+C. Download `spotify-desk-thing-phase5.zip` into Downloads:

```powershell
$Project = "$HOME\Projects\Display-Spotify-Desk-Thing"
Set-Location $Project
Expand-Archive -LiteralPath "$HOME\Downloads\spotify-desk-thing-phase5.zip" -DestinationPath $Project -Force

# Do once: saves the same client ID already used in 4.2
.\.venv\Scripts\python.exe .\desk_ui.py --configure

# Runs on localhost only; no network exposure yet
.\.venv\Scripts\python.exe .\desk_ui.py
```

Open both in your Windows browser:

- Companion player: `http://127.0.0.1:8888/`
- Pairing manager: `http://127.0.0.1:8888/pair`
- Simulated device: `http://127.0.0.1:8888/device`

On `/device`, type the one-time code from `/pair`, then click **Pair device**. Test:

1. Play/Pause, Next, Previous and PC/WI-FI mode switch using four key buttons (`1`, `2`, `3`, `4` work as keyboard shortcuts).
2. Turn the virtual encoder with the +/− buttons, or with the mouse wheel over the knob. The knob sends volume steps of 5%; PC Spotify volume follows the Phase 4.2 source logic.
3. Change a song in Spotify itself; the device should update metadata and artwork. PC sound level should affect the screen glow.
4. Refresh the device page: the paired token should persist. Click **Forget pairing on this browser** to clear only this browser's stored token.
5. Open `/pair`, select **Revoke all devices**, and check that the simulator requires pairing again.

## Omarchy / Arch Linux — through SSH

Transfer from Windows PowerShell:

```powershell
scp "$HOME\Downloads\spotify-desk-thing-phase5.zip" cousinsuke@tuf-linux:~/
ssh cousinsuke@tuf-linux
```

On the **Linux SSH session**:

```bash
cd ~/Projects/Display-Spotify-Desk-Thing
unzip -o ~/spotify-desk-thing-phase5.zip

# Do once: enter the existing Spotify public Client ID
./.venv/bin/python desk_ui.py --configure

# Launch localhost-only first
./.venv/bin/python desk_ui.py
```

In a **second Windows PowerShell session**, tunnel to the Linux app:

```powershell
ssh -N -L 8888:127.0.0.1:8888 cousinsuke@tuf-linux
```

Then open `/pair` and `/device` using `http://127.0.0.1:8888` on Windows. **Stop the Windows Desk Thing server first** so local port 8888 is available. If something else already owns Linux port 8888, stop that old server with Ctrl+C before launching the updated version; do not start two servers on the same port.

### Optional: two actual devices on your home Wi-Fi

Once localhost tests pass, stop the server and start the companion with:

```bash
./.venv/bin/python desk_ui.py --lan
```

On another device connected to the same **trusted private LAN**, open `http://tuf-linux:8888/device` (or substitute the Linux machine's private IP). The pairing code is displayed via the Linux server terminal and its `/pair` management page (accessible on Linux itself or through an SSH localhost tunnel). On Windows, the corresponding optional LAN command is:

```powershell
.\.venv\Scripts\python.exe .\desk_ui.py --lan
```

Windows Defender Firewall may need a **Private-network, local-subnet-only** inbound permission for TCP 8888; do not allow it on Public networks. If your router or Wi-Fi isolates clients, remote pairing may fail until both machines are on the same accessible LAN.

**Security limitations:** the prototype uses HTTP, **not TLS**. Pairing codes, tokens, metadata and commands can be observed by someone with access to the network path. Only use `--lan` on a trusted network, never port-forward 8888 or expose it to the internet, public Wi-Fi or untrusted devices. A production device should use HTTPS or another encrypted/authenticated transport before deployment. The built-in Flask server is development-only.

## Device protocol reference (HTTP JSON v1)

Only when `--lan` is enabled, the following are the remote-exposed routes. All original desktop UI, OAuth and PC/Spotify routes stay loopback-only.

| Method | Path | Authentication | Purpose |
|---|---|---|---|
| GET | `/device` | None | Device simulator HTML |
| GET | `/static/device.css`, `/static/device.js` | None | Simulator assets |
| POST | `/api/device/pair` | One-time 6-digit code in JSON | Returns 64-character hex bearer token |
| GET | `/api/device/state` | `Authorization: Bearer <token>` | Current state, selected mode |
| POST | `/api/device/action` | Bearer | Send controls |
| GET | `/api/device/events` | Bearer | SSE `state`, `meter`, `revoked` events |
| GET | `/api/device/artwork` | Bearer | Current PC artwork bytes |

Pair request:

```json
{"code":"123456","name":"My Desk Thing"}
```

The server sends back `{"ok":true,"token":"...","mode":"pc"}`. The code is only an example; use the current code printed by the running companion. Never publish paired bearer tokens.

Action requests:

```json
{"action":"next"}
{"action":"previous"}
{"action":"toggle"}
{"action":"mode","value":"spotify"}
{"action":"mode","value":"pc"}
{"action":"volume_step","value":5}
{"action":"volume_step","value":-5}
{"action":"volume","value":50}
```

A future ESP32 firmware can consume `/api/device/state` over simple authenticated GET polling if it doesn't support streamed JSON events; `/api/device/events` provides lower-latency updates to the browser simulator.

## Local pairing management

Local-only endpoints:

- `GET /pair` and `GET /api/device/pairing`: display active one-time code, expiry, and paired names.
- `POST /api/device/pairing/new` with empty JSON `{}`: rotate pairing code for another device.
- `POST /api/device/pairing/revoke-all` with `{}`: invalidate all existing tokens.

Pairing tokens and device modes persist in `.desk_devices.json`; Client ID in `.desk_config.json`; original Spotify token cache in `.spotify_token.json`. All three are excluded from `.gitignore` and **not** included in this ZIP. On Unix the two new files are written with owner-only (0600) file permissions. Do not commit, publish or share the token cache or device-token file.

## Run tests

Run locally in the project environment:

```powershell
# Windows
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

```bash
# Linux
./.venv/bin/python -m unittest discover -s tests -v
```

The `test_device_bridge.py` tests exercise Flask endpoint protection, pairing, controls and SSE without contacting Spotify. Existing tests cover the Linux adapter and Phase 4.2 volume routing.

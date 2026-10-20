# Setup — Windows 11 and Omarchy/Arch

> Applies to the Phase 5.2 source layout once that source has been imported into this repository. During repository bootstrap the source may still be in the validated Phase 5.2 archive.

## Shared Spotify setup

A Spotify Premium account and an existing Spotify developer application are used for this prototype. Allow `http://127.0.0.1:8888/callback` as the PKCE redirect in the app configuration. **No client secret is needed.** Avoid exposing OAuth code/token logs or local device tokens.

## Windows 11

```powershell
cd "$HOME\Projects\Display-Spotify-Desk-Thing"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt -r requirements-windows.txt
.\.venv\Scripts\python.exe desk_ui.py --configure
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe desk_ui.py
```

Run `--configure` once per installation to store the **public** Spotify Client ID locally. Open `http://127.0.0.1:8888/`, `/pair` and `/device`.

## Omarchy / Arch Linux

```bash
sudo pacman -Syu --needed python python-pip playerctl libpulse
cd ~/Projects/Display-Spotify-Desk-Thing
python -m venv .venv
./.venv/bin/python -m pip install -r requirements-ui.txt
./.venv/bin/python desk_ui.py --configure
./.venv/bin/python -m unittest discover -s tests -v
./.venv/bin/python desk_ui.py
```

On Arch, avoid partial pacman upgrades; if mirrors return 404s, refresh/upgrade together.

## Windows browser → Linux server over SSH

On Windows PowerShell, stop any Windows Flask server bound to port 8888, then:

```powershell
ssh -N -L 8888:127.0.0.1:8888 cousinsuke@tuf-linux
```

Use `http://127.0.0.1:8888/device` in Windows browser. Default server is localhost-only. `--lan` is optional for a trusted private network and should **never** be internet-exposed.

## Local-only files (never commit)

`.spotify_token.json`, `.desk_config.json`, `.desk_devices.json`, `.venv`, `.env`. Preserve them when applying an update; remove pairing via the local manager if revocation is desired.

## Run-time diagnostics

Windows: `windows_diagnostics.py`. Linux: `linux_diagnostics.py`; check `playerctl -l`, `wpctl status` and media source selection. A blank `playerctl -l` means no detected MPRIS session at that moment, not necessarily a failure of Wi-Fi Spotify control.

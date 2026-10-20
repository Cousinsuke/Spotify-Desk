# Spotify Desk Thing — Phase 4.1 (Omarchy / Arch Linux)

## What this version adds

- **WI-FI:** Existing standalone Spotify Web API prototype preserved.
- **PC:** Uses `playerctl` with MPRIS to read/skip/pause locally playing tracks, preferring Spotify when it is available.
- **Volume:** Uses `wpctl` to read/write the default PipeWire output level. This is **system output volume**, not Spotify's independent volume.
- **Audio glow:** Captures the **monitor of the default output sink**, not your microphone, with `parec` and streams RMS only using the existing SSE connection. It can react to other sounds besides music.
- Works with the existing 800×480 interface and the Windows companion from Phase 3.3; the Python server chooses its adapter based on the OS.

### Required Linux software

On **Omarchy / Arch Linux** (a Linux terminal, not Windows PowerShell):

```bash
sudo pacman -S --needed python python-pip playerctl libpulse unzip
command -v wpctl pactl parec playerctl
pactl info | grep 'Server Name'
```

Omarchy normally already uses PipeWire + WirePlumber. If `wpctl` is missing, **check your existing audio setup** before making changes; don't blindly replace or install a competing PulseAudio server. `libpulse` provides the `parec`/`pactl` client utilities, and works with PipeWire's PulseAudio-compatible server.

### Copy from Windows to Linux (optional SSH workflow)

In **Windows PowerShell**, after downloading `spotify-desk-thing-phase4-1.zip`:

```powershell
scp "$HOME\Downloads\spotify-desk-thing-phase4-1.zip" cousinsuke@tuf-linux:~/spotify-desk-thing-phase4-1.zip
ssh cousinsuke@tuf-linux
```

On the **Linux SSH terminal**:

```bash
mkdir -p ~/Projects/Display-Spotify-Desk-Thing
cd ~/Projects/Display-Spotify-Desk-Thing
sudo pacman -S --needed python python-pip playerctl libpulse unzip
unzip -o ~/spotify-desk-thing-phase4-1.zip
python -m venv .venv
./.venv/bin/python -m pip install -r requirements-ui.txt

# A Spotify Client ID is public, but keep tokens private. Enter it interactively:
read -rp 'Spotify Client ID: ' SPOTIPY_CLIENT_ID
export SPOTIPY_CLIENT_ID

./.venv/bin/python linux_diagnostics.py
./.venv/bin/python desk_ui.py
```

For a browser running **on that Linux desktop**, open `http://127.0.0.1:8888`.

If you are SSH-ing from Windows, keep the server running and open a **second Windows PowerShell** window for port forwarding:

```powershell
ssh -N -L 8888:127.0.0.1:8888 cousinsuke@tuf-linux
```

Then open `http://127.0.0.1:8888` in **Windows Chrome**. Stop the **Windows** Desk Thing server first if it already uses that local port. The same loopback OAuth callback works through this tunnel if you later authorize the Linux copy's Spotify Wi-Fi mode.

For SSH-launched media access, run under the **same logged-in Linux user** as your Spotify application, with a working user D-Bus. If `playerctl -l` is empty over SSH but populated in a local terminal, verify your session environment and try:

```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
playerctl -l
```

Don't use `sudo` to run the Python server; the user D-Bus and audio session belong to your normal user.

### What to test

1. Launch Spotify **on the Linux desktop** (not only on the Windows PC). Start a song and verify `playerctl -l` and `playerctl -p spotify status`.
2. Select PC on the Desk Thing UI. Test artist/title, local Play/Pause and Next/Previous.
3. Move the volume slider **at a comfortable level** and check the correct PipeWire output changes.
4. Play music through your chosen Linux default output and inspect the audio-reactive glow.
5. Switch back to WI-FI and verify remote Spotify Connect controls still work.

### Known prototype limitations

- MPRIS metadata and art availability depend on the Linux media player. HTTPS artwork is shown directly; local artwork is only served from files under the user's `.cache` directory and only if recognized as PNG, JPEG or WebP.
- Audio meter follows the default sink; if output devices change, the capture process restarts.
- MPRIS currently polls locally every ~800ms (no Spotify API cost). Event subscriptions and multi-player selection are future improvements.
- This is a **localhost browser prototype**. It is **not** yet the standalone ESP32 firmware or an external network service.
- Test the audio glow under the actual local desktop session first; over SSH, the output can be different or unavailable.

**Do not port-forward this development server to the public internet.** The local HTTP controls use same-origin restrictions but aren't designed for untrusted remote networks.

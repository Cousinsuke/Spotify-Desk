# Phase 4.2 — Spotify volume sync in PC mode (Windows + Omarchy)

The Spotify application's volume slider and the operating system's master speaker volume are **different controls**. In Phase 4.1 the PC-mode slider represented Windows master volume (WASAPI/pycaw) or PipeWire default output volume (wpctl). This caused a mismatch when the user adjusted volume inside Spotify.

Phase 4.2 changes this behavior:

- **WI-FI:** Spotify volume (unchanged).
- **PC + Spotify playing locally + Spotify Connect authorized + same current track:** Spotify Connect volume (read and set via the existing Spotify Web API). The label beside the slider says `SPOTIFY`.
- **PC + other MPRIS/GSMTC media player, unavailable Spotify API or unmatched track:** Local system output volume via the OS companion. The label says `SYSTEM`.
- PC playback buttons remain native Windows media-session / Linux playerctl controls and do **not** use Spotify Web API.
- Album artwork, PipeWire/WASAPI audio glow stream, and 800×480 UI are unchanged.

To avoid polling the Spotify Web API at PC-media-session speed (~0.8s), Spotify status is cached across both modes for **5 seconds**. Spotify volume edits made in the original Spotify app can therefore take several seconds to appear in PC mode. Local PC playback status still refreshes rapidly. The slider optimistically reflects its own changes briefly, then reconciles with Spotify.

Safety behavior: Before sending Spotify volume commands, the current Spotify Connect track is compared with the selected local Windows/Linux media session track. A mismatch returns HTTP 409 rather than sending the change to a different track's Spotify playback. If Spotify Connect isn't available, the clearly labelled `SYSTEM` slider remains usable as before. The PC-mode volume label changes automatically based on the active source.

## Windows PowerShell installation

Stop the Windows Desk Thing server (Ctrl+C) before installing.

```powershell
$Project = "$HOME\Projects\Display-Spotify-Desk-Thing"
$Zip = "$HOME\Downloads\spotify-desk-thing-phase4-2.zip"
Set-Location $Project
Expand-Archive -LiteralPath $Zip -DestinationPath $Project -Force
.\.venv\Scripts\python.exe .\desk_ui.py
```

Open `http://127.0.0.1:8888` and hard-refresh with Ctrl+F5.

## Omarchy / Arch installation over SSH

Download this ZIP onto Windows and copy it to the Linux laptop:

```powershell
scp "$HOME\Downloads\spotify-desk-thing-phase4-2.zip" cousinsuke@tuf-linux:~/
ssh cousinsuke@tuf-linux
```

On the Linux SSH session, stop the currently running Desk Thing server, then:

```bash
cd ~/Projects/Display-Spotify-Desk-Thing
unzip -o ~/spotify-desk-thing-phase4-2.zip
read -rp 'Spotify Client ID: ' SPOTIPY_CLIENT_ID
export SPOTIPY_CLIENT_ID
./.venv/bin/python desk_ui.py
```

If your OAuth token is already cached in `.spotify_token.json`, you won't need to reauthorize. The ZIP does not contain credentials or overwrite existing OAuth tokens or Python `.venv` environments.

## Testing

1. Start playing Spotify on this computer, select PC, and confirm the slider label says `SPOTIFY` with the same percentage as Spotify.
2. Change Spotify's own slider; within about 5 seconds PC mode should reflect that percentage.
3. Move the Desk Thing slider; Spotify should change too (provided Spotify Connect allows volume control).
4. Switch to another local player; PC mode should label the slider `SYSTEM` and control the OS output volume.
5. Confirm the existing audio-reactive glow still works. The audio meter always monitors the OS output, regardless of whether the slider is in SPOTIFY or SYSTEM mode.

If PC mode shows `SYSTEM` even when Spotify is playing locally, check that the Spotify Web API authorization is present under WI-FI mode and that Spotify Connect reports the same current track as the local media session. It falls back rather than accidentally changing playback on another device.

# Recovery and safe updates

## Sources of truth

1. Current checked-out code and newest relevant Git commits.
2. `docs/CHATGPT-HANDOFF.md` and `docs/CHANGELOG.md` after checking for newer commits.
3. Roadmap and decisions.
4. Previously validated Phase 5.2 ZIP if source import is incomplete.

## Keep local secrets out of Git

Do not push, display or paste `.spotify_token.json`, `.desk_devices.json`, `.desk_config.json`, `.env` or any temporary copies. In particular, device bearer tokens and PKCE OAuth tokens are credentials.

## Recreate a development environment

- Create a fresh `.venv` and install `requirements-ui.txt`, plus `requirements-windows.txt` on Windows.
- Run `desk_ui.py --configure` if the local public Spotify Client ID is absent.
- Reauthorize through localhost Spotify OAuth if necessary.
- Run unit tests before starting the server.

## Typical failure modes

- Port 8888 already occupied: stop the old server before starting another; for SSH port forwarding, stop the Windows local instance or use a different free local port.
- Missing MPRIS sessions under SSH: verify Spotify is actually playing on the Linux desktop and that the user D-Bus session is accessible.
- No album art: verify current PC state, keyed proxy, direct HTTPS MPRIS art and no stale browser cache; the music-note fallback is valid.
- `SPOTIFY` vs `SYSTEM` volume mismatch: verify Spotify Connect matches the local current track; don't change unrelated devices.
- Excess logs: HTTP GETs can reflect status polling; persistent audio levels should use SSE in normal operation.

Never force-reset source or overwrite local secrets as a generic troubleshooting step. Preserve accepted behaviour and recover from Git commits or verified release archives.

# Spotify Desk Thing

An experimental desktop music controller and future physical desk accessory, built around an 800 × 480 touchscreen, four mechanical keys, and a rotary encoder.

**Repository status:** Documentation bootstrap is underway. The currently accepted software release is **Phase 5.2**, tested on Omarchy/Arch. The source import is tracked separately from the documentation bootstrap and should not be described as complete until the full source tree is committed.

## Direction

- Spotify **Wi-Fi mode**: Spotify Web API and Spotify Connect.
- **PC mode**: local Windows 11 media sessions or Linux MPRIS/playerctl, with PC audio visualisation.
- Common HTML/CSS/JavaScript 800 × 480 player interface.
- Optional private-LAN device simulator, paired using a short-lived code and bearer token.
- Planned physical hardware: ESP32-S3, Waveshare 4.3-inch 800 × 480 touch display, 4 MX switches, encoder, custom 3D-printed enclosure. **Board and pinout not yet finalized or purchased.**

## Current status

- Windows 11 companion: **Phase 4.2 user-accepted**; later simulator changes need platform-specific revalidation.
- Omarchy/Arch companion and browser device simulator: **Phase 5.2 user-accepted**; 39 tests passed in the user's Omarchy virtual environment.
- Real ESP32 firmware, electrical design, final hardware protocol and enclosure: **not implemented**.

## Project documentation

- [Current-state handoff](docs/CHATGPT-HANDOFF.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisions](docs/DECISIONS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Design](docs/DESIGN.md)
- [Hardware](docs/HARDWARE.md)
- [Setup](docs/INSTALL.md)
- [Testing](docs/TESTING.md)
- [Changelog](docs/CHANGELOG.md)
- [Recovery](docs/RECOVERY.md)
- [ChatGPT workflow and continuation prompt](docs/CHATGPT-WORKFLOW.md)

## Safety

Never commit `.spotify_token.json`, `.desk_config.json`, `.desk_devices.json`, `.env`, credentials, device bearer tokens, virtual environments or local machine-specific configuration. Local development servers must not be exposed to the public internet.

This project is a prototype and is not affiliated with Spotify.

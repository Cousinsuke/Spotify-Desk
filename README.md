# Spotify Desk Thing

An experimental desktop music controller and future physical desk accessory, built around an 800 × 480 touchscreen, a **preferred three-key media layout**, and a **push-to-switch-mode rotary volume encoder**.

**Repository status:** Phase 5.2 application source is committed on `main` at [`7172c2e`](https://github.com/Cousinsuke/Spotify-Desk/commit/7172c2ee2f285253507b13c71acb7072adc04067). This is the current checked-in software baseline; hardware firmware has not started.

## Direction

- Spotify **Wi-Fi mode**: Spotify Web API and Spotify Connect.
- **PC mode**: local Windows 11 media sessions or Linux MPRIS/playerctl, with PC audio visualisation.
- Common HTML/CSS/JavaScript 800 × 480 player interface.
- Optional private-LAN device simulator, paired using a short-lived code and bearer token.
- Planned physical hardware: ESP32-S3, Waveshare 4.3-inch 800 × 480 touchscreen, **three ~18 mm MX media keys beneath screen and an ~18 mm diameter push-capable rotary knob at right** (rotate for volume; **press to switch PC/Wi-Fi mode**; interaction mapping accepted), custom 3D-printed enclosure. The prior four-key *software simulator* is unchanged. **Board, case dimensions and pinout are not finalized or purchased.**

## Current status

- Windows 11 companion: **Phase 4.2 user-accepted**; later simulator changes need platform-specific revalidation.
- Omarchy/Arch companion and browser device simulator: **Phase 5.2 user-accepted**; 39 tests passed in the user's Omarchy virtual environment.
- Real ESP32 firmware, electrical design, final hardware protocol and enclosure: **not implemented**.

## Current source and historical versions

The accepted Phase 5.2 Python, JavaScript, CSS, HTML and tests have been imported to the repository root. **Current source checkpoint:** [`7172c2e`](https://github.com/Cousinsuke/Spotify-Desk/commit/7172c2ee2f285253507b13c71acb7072adc04067). Do not re-run the one-time `import-phase5-2.ps1` script on an already imported checkout.

**Historical ZIP migration is complete.** Sixteen version archives were uploaded in [`f781506`](https://github.com/Cousinsuke/Spotify-Desk/commit/f78150605b15af1fa451aa5ed725f023fd03835c), with checksums recorded in [the archive manifest](docs/history/ARCHIVED-PHASE-ZIPS.md). They are reference snapshots, not alternate active source trees.

## Preserve earlier ZIP versions

Earlier ChatGPT-delivered patch ZIPs have been uploaded as **archives**, without replacing the current runnable code. If additional historical ZIPs are found later, rerun:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$HOME\Projects\Spotify-Desk\scripts\archive-local-phases.ps1" -DownloadsPath "$HOME\Downloads" -Publish
```

The archive script places historical ZIPs under `archives/phase-zips/`, strips generated `__pycache__`/`.pyc` entries from stored copies without changing Downloads, records both original and archived SHA-256 checksums in `docs/history/ARCHIVED-PHASE-ZIPS.md`, and commits/pushes to `main`. The ZIPs are historical reference builds, **not** a replacement for current root-level source. The script rejects common private filenames, but cannot guarantee that older archives contain no secrets within source code; review before publishing in this public repository.


## Project documentation

- [Current-state handoff](docs/CHATGPT-HANDOFF.md)
- [Roadmap](docs/ROADMAP.md)
- [Decisions](docs/DECISIONS.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Design](docs/DESIGN.md)
- [Hardware overview](docs/HARDWARE.md)
- [Phase 6 Waveshare screen and input-expander research](docs/HARDWARE-RESEARCH.md)
- [Phase 6 extended hardware comparison](docs/HARDWARE-COMPARISON.md)
- [Phase 6 proposed component shortlist with UK prices](docs/HARDWARE-SHORTLIST.md)
- [Phase 6 pre-purchase voltage, wiring and mechanical verification](docs/HARDWARE-PRE-PURCHASE-CHECK.md)
- [Phase 6 electrical chip/boot and protected-input design review](docs/HARDWARE-ELECTRICAL-REVIEW.md)
- [Phase 6 manufacturer-dimensioned faceplate and encoder fit study](docs/HARDWARE-MECHANICAL-LAYOUT-STUDY.md)
- [Editable trial mechanical envelope CAD (SCAD / SVG / coordinates)](mechanical/README.md)
- [Setup](docs/INSTALL.md)
- [Testing](docs/TESTING.md)
- [Changelog](docs/CHANGELOG.md)
- [Recovery](docs/RECOVERY.md)
- [ChatGPT workflow and continuation prompt](docs/CHATGPT-WORKFLOW.md)

## Safety

Never commit `.spotify_token.json`, `.desk_config.json`, `.desk_devices.json`, `.env`, credentials, device bearer tokens, virtual environments or local machine-specific configuration. Local development servers must not be exposed to the public internet.

This project is a prototype and is not affiliated with Spotify.

# New conversation handoff

**Last updated: 2026-11-26**

Repository: https://github.com/Cousinsuke/Spotify-Desk  
Folder: Echo Show 5 Gen 1  
Branch: main (documentation baseline). Read the actual latest files before acting.

## User's intended project

- Repurpose a charcoal-black 5.5-inch Echo Show 5 (2019), not an 8-inch model, as the Spotify Desk touchscreen.
- Home dashboard, Spotify, Bournemouth weather, supplementary live CGM display; expandable to more widgets later.
- Spotify Wi-Fi mode must control the active Spotify Connect device (including Xbox) with the PC off. PC mode remains separate and optional; it controls local Windows/Omarchy media, system volume and audio meter when its companion is running.
- Prefer existing Raspberry Pi 4 (8 GB) as always-on host alongside existing Nextcloud; no extra hardware or paid hosting if avoidable. No Home Assistant requirement.
- Reuse existing interface and code; keep old CAD/PCB and software baselines intact. Design for the 960 x 480 screen and 1 GB RAM.
- Follow the upstream exact-model guide; the stock firmware/bootloader must be checked first. Keep stock device offline until then.
- Use clear OS-specific commands (Omarchy/Arch Linux preferred for firmware checks; Windows 11 and Pi Linux are distinct). Never advise destructive steps before compatibility and prerequisites are known.

## Current checkpoint

The £45.99 used H23K37 candidate has a pictured UK 15 W adapter, seller condition Very Good, screenshot listing two units available, and a reported 30-day returns policy. A previous £42.29 unit sold. Purchase, physical condition, exact shipped unit, bootloader, cable capability and return eligibility after modification are not confirmed. Existing Micro-USB cables cannot be tested on their own; an unbranded USB-C female to Micro-USB male adapter is available but data capability is unverified. USB utilities are now installed on Omarchy; a bare-cable lsusb test returned no new device, which is expected.

The primary source for installation is the current Kiosk Satellite unlocking guide; model-specific firmware analysis is in HARDWARE-AND-FIRMWARE.md. A 2024 LK build is documented as supported, a 2019 LK is unsupported by Fastbrick USB, and the 2026 LK is not confirmed. Do not update Fire OS just to try to get a different LK. Do not assume stock firmware downgrades are possible.

The existing Gluroo reader and dashboard are already in the repository; a prior Windows live-feed test is recorded in docs/GLUCOSE-LIVE.md. The current medical-data endpoint is deliberately loopback-only. No secure external Echo Show connection or Pi deployment is implemented yet. Keep the upstream credential private on the Pi and do not expose the entire Flask app through a reverse proxy.

## Next step

If the hardware has not been purchased, assess listing condition, adapter, returns and total cost. If it arrives, leave it off Wi-Fi and follow the read-only checks in INSTALLATION-AND-USB.md. Ask for the product and LK version outputs, with serial/unique identifiers redacted. Do not flash until the exact build and current guide have been checked. Separately, inspect the Pi's OS/resources/ports without changing Nextcloud.

## Copy/paste prompt for a new chat

> Continue my Spotify Desk Echo Show 5 Gen 1 project in https://github.com/Cousinsuke/Spotify-Desk. Read every Markdown file in the "Echo Show 5 Gen 1" folder, then inspect relevant existing code and docs before making changes. Follow the latest handoff, preserve previous hardware/software work, and do not repeat resolved troubleshooting. Give practical OS-specific commands. After each meaningful research finding, fix, completed task or validation result, update the appropriate Markdown files and CHANGELOG directly in GitHub; refresh this handoff with the current status and next step. Label unverified assumptions and keep personal data, credentials and actual CGM readings out of GitHub. Ask for user validation where physical testing is required. Do not perform or recommend destructive flashing without checking the exact unit and current upstream guide.

## Documentation workflow

Read before editing; append dated evidence; keep one current next action; record actual test outputs in redacted form, not invented results. For changes to code, add tests and note commit(s), validation status and any rollback path. If GitHub write access is unavailable, say so and supply a patch or suggested document update instead of claiming it was saved.

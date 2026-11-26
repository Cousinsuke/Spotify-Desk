# New conversation handoff

**Last updated: 2026-11-26**

Repository: https://github.com/Cousinsuke/Spotify-Desk  
Folder: Echo Show 5 Gen 1  
Branch: main (documentation baseline). Read the actual latest files before acting.

## User's intended project

- Repurpose a charcoal-black 5.5-inch Echo Show 5 (2019), not an 8-inch model, as the Spotify Desk touchscreen.
- Home dashboard, Spotify, Bournemouth weather, supplementary live CGM display; expandable to more widgets later.
- Spotify Wi-Fi mode must control the active Spotify Connect device (including Xbox) with the PC off. PC mode remains separate and optional; it controls local Windows/Omarchy media, system volume and audio meter when its companion is running.
- User explicitly selected the existing Raspberry Pi 4 (8 GB) as always-on host; user clarified the Pi is currently powered off and Nextcloud is no longer in use; no extra hardware or paid hosting if avoidable. No Home Assistant requirement.
- Reuse existing interface and code; keep old CAD/PCB and software baselines intact. Design for the 960 x 480 screen and 1 GB RAM.
- Follow the upstream exact-model guide; the stock firmware/bootloader must be checked first. Keep stock device offline until then.
- Use clear OS-specific commands (Omarchy/Arch Linux preferred for firmware checks; Windows 11 and Pi Linux are distinct). Never advise destructive steps before compatibility and prerequisites are known.

- New UI direction: user's rough reference has a large central clock/date, small weather line, abstract background and right-side vertical navigation. Five primary slots: Home, Spotify, Weather, Glucose, More. User accepted reveal by right-edge arrow AND inward swipe, configurable inactivity delay, content expands when hidden, per-page auto-hide, and grid icon opening a floating app drawer. Exact defaults, rail sizing and other visual details remain pending. For every design decision include Own idea and optional modifications. Home default B accepted (clock with subtle summaries); optional other fixed presets/backgrounds if lightweight, selectable clock styles, fixed layouts first, no automatic page changes on inactivity. Exact widget details inferred from B and need prototype review. Spotify direction accepted: current web player artwork left with immersive colour background selectable in Settings; previous/play/pause/next, seek, shuffle/repeat, save, floating device selector. User requests physical +/- with temporary volume popup and experimental Echo speaker mode; no permanent volume icon/slider, save song at far right and extended tappable active-device selector. If hardware volume fails, evaluate non-permanent fallback; preserve third privacy/power button, use a single compact Wi-Fi/PC/Echo dropdown with current mode and down arrow, separate from the bottom device selector. Last track retained in memory if lightweight, correctly labelled. Local Spotify playback, remote key bridge and new API actions unverified; see UI-DESIGN.md for sources and gates. Next review Weather. Read UI-DESIGN.md before designing or coding.

## Current checkpoint

The £45.99 used H23K37 candidate has a pictured UK 15 W adapter, seller condition Very Good, screenshot listing two units available, and a reported 30-day returns policy. A previous £42.29 unit sold. User confirmed ordering the Echo Show on 2026-11-26; awaiting delivery. Final price, exact shipped unit, condition, bootloader, cable capability and return eligibility after modification remain unverified. Existing Micro-USB cables cannot be tested on their own; an unbranded USB-C female to Micro-USB male adapter is available but data capability is unverified. Omarchy tool checks passed on 2026-11-26: android-tools 37.0.0.p1-1, ADB 1.0.41 / 37.0.0p1, Fastboot 37.0.0p1, usbutils 019; physical USB detection remains pending. USB utilities are installed on Omarchy; a bare-cable lsusb test returned no new device, which is expected.

The primary source for installation is the current Kiosk Satellite unlocking guide; model-specific firmware analysis is in HARDWARE-AND-FIRMWARE.md. A 2024 LK build is documented as supported, a 2019 LK is unsupported by Fastbrick USB, and the 2026 LK is not confirmed. Do not update Fire OS just to try to get a different LK. Do not assume stock firmware downgrades are possible.

The existing Gluroo reader and dashboard are already in the repository; a prior Windows live-feed test is recorded in docs/GLUCOSE-LIVE.md. The current medical-data endpoint is deliberately loopback-only. No secure external Echo Show connection or Pi deployment is implemented yet. Keep the upstream credential private on the Pi and do not expose the entire Flask app through a reverse proxy.

## Next step

While awaiting delivery, start with the read-only Pi preflight in PRE-ARRIVAL.md (Omarchy tool checks are complete). Pi is off and unused; existing OS/storage and whether old Nextcloud data should be preserved are unknown; do not assume a deployment architecture until preflight results arrive. Pi is now the user-selected initial host, to reduce Echo Show workload and simplify future expansion. Native Android APK or Termux loopback server are later alternatives; neither is tested. Do not erase existing storage without explicit approval. In parallel, review Weather next (navigation, Home and Spotify visual directions accepted), then define the remaining page layouts using UI-DESIGN.md. Next build an isolated headless backend and synthetic-data browser preview, then secure and test it before enabling real data. On delivery, keep stock Fire OS offline, inspect the device and follow INSTALLATION-AND-USB.md; request redacted product and LK version only. Do not flash until compatibility and the current guide are checked.

## Copy/paste prompt for a new chat

> Continue my Spotify Desk Echo Show 5 Gen 1 project in https://github.com/Cousinsuke/Spotify-Desk. Read every Markdown file in the "Echo Show 5 Gen 1" folder, then inspect relevant existing code and docs before making changes. Follow the latest handoff, preserve previous hardware/software work, and do not repeat resolved troubleshooting. Give practical OS-specific commands. After each meaningful research finding, fix, completed task or validation result, update the appropriate Markdown files and CHANGELOG directly in GitHub; refresh this handoff with the current status and next step. Label unverified assumptions and keep personal data, credentials and actual CGM readings out of GitHub. Ask for user validation where physical testing is required. Do not perform or recommend destructive flashing without checking the exact unit and current upstream guide.

## Documentation workflow

Read before editing; append dated evidence; keep one current next action; record actual test outputs in redacted form, not invented results. For changes to code, add tests and note commit(s), validation status and any rollback path. If GitHub write access is unavailable, say so and supply a patch or suggested document update instead of claiming it was saved.

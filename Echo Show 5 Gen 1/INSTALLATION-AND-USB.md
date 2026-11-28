# Installation, USB troubleshooting and recovery gates

Last updated 2026-11-26. **No actual Echo Show commands have been run on a device in this project.**

## 1. Before any modification

Confirm correct model H23K37, condition and adapter. Keep the stock Show disconnected from Wi-Fi to avoid firmware updates. Do not connect to an already saved network if possible (e.g. keep its prior network unavailable). Inspect hardware and establish return eligibility before opening or modifying. Do not flash a different model image or try stock downgrades.

## 2. Cable test history

On Omarchy, `watch -n 1 lsusb` initially returned `lsusb: command not found` (127). Fixed by installing usbutils. Connected and disconnected lists were identical, because the cable was not attached to a USB peripheral. A passive USB cable is not enumerated; this does **not** prove that any cable is charge-only or faulty.

Available: multiple Micro-USB cables and a pictured, unbranded USB-C female to Micro-USB male adapter. Adapter connector appears appropriate; CE sticker does not establish data capability. A known USB-C data cable plus adapter may work if both carry data and correctly support USB device connection. No compatible peripheral available for immediate testing. Do not buy another cable until testing the Echo Show if practical.

When hardware arrives, prefer a short, direct USB-A to Micro-USB data cable (0.5–1 m) and a direct PC port, not a hub. The adapter is a reasonable diagnostic option; prefer a stable direct cable for flashing. A new USB 2.0 charge-and-sync cable is sufficient if needed; earlier Amazon Basics/eBay options were around £3–5, prices not current. Charging alone does not prove data support.

### Omarchy / Arch Linux

```bash
sudo pacman -S --needed usbutils android-tools
watch -n 1 lsusb
```

In another terminal if needed:

```bash
sudo dmesg -w
```

Ctrl+C exits watch or dmesg. If a known peripheral enumerates, data lines work; repeated disconnects/errors imply instability. If Fastboot sees the USB device only with elevated privileges, troubleshoot udev/permissions rather than assuming a bad cable.

## 3. Read-only compatibility check (first action on arrival)

Upstream guide: https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md

1. Disconnect the Show's power. Hold volume down, volume up, and microphone-off together while reconnecting power. Continue until Fastboot mode appears (per upstream instructions).
2. Connect its Micro-USB port to the PC using a candidate cable and try detection. Swap cables/ports as needed without flashing.
3. On Omarchy run:

```bash
fastboot devices
fastboot getvar product
fastboot getvar lk_build_desc
```

Optionally query `fastboot getvar unlock_status` if supported by the device; do not infer failure from an unsupported variable. Do not publish the serial printed by fastboot devices. Share only product and LK version, with identifiers redacted. Expected documented product AEOCH; known supported LK prefix 44072a3-20240709. See HARDWARE-AND-FIRMWARE.md for exact strings. If product or LK is not as expected, stop and research before any writes.

When finished with inspection:

```bash
fastboot reboot
```

Keep stock OS offline after reboot. These commands query/reboot rather than flash. No guarantee of successful exploit based only on detection.

## 4. Gated installation plan (not executed)

Only after unit compatibility and permission to modify are confirmed:
- Reopen current upstream guide and original XDA thread. Confirm supported build and obtain amonet-checkers-v2.0.2.zip (version documented 2026-11-26), current model-specific image, required recovery and any published hashes. Verify download provenance and checksums when available. Do not mix checkers/cronos/8-inch files.
- Use the exact current Fastbrick procedure for the supported LK; upstream documents Linux fastbrick.sh and Windows fastbrick.bat. It rewrites the bootloader and installs TWRP, so interruption could brick the device. Keep power and USB stable. Do not proceed with unsupported or uncertain LK.
- Confirm TWRP version required by current release (documented 3.7.0_9-0 for amonet 2). Follow image-specific installation/wipe instructions, not generic Android commands. Unlock/install may erase data and alter return eligibility.
- After custom firmware installation, follow upstream instructions for time/Wi-Fi and first boot; test touch, screen, Wi-Fi, speaker, wake, reboot and kiosk. Do not connect stock Fire OS to Wi-Fi for a downgrade/update experiment.
- Validate kiosk's custom HTTPS page without Home Assistant, or choose another fullscreen browser if needed.

## 5. If unsupported or failed

Do not try arbitrary firmware or cross-model recovery images. Preserve error text, exact LK and stage (redact serials). A hardware test-point alternative is mentioned by upstream; opening the enclosure is higher risk and may affect returns. Investigate the exact device guide before considering it. No guaranteed downgrade, unbrick or test-point recovery has been established for this particular unit. If still stock and incompatible, consider a normal return subject to seller terms.

For any failure during an actual write, do not repeatedly power-cycle or rerun arbitrary commands. Consult the exact tool's recovery instructions and identify whether it is in Fastboot, TWRP or another state.


### Received Echo Show — stock firmware observed

2026-11-28: Echo Show arrived. User supplied stock Device Options photo confirming Echo Show 5 (1st generation), Fire OS 6.5.7.1 (NS6571/6225). No unlock/flash or read-only fastboot checks performed yet. Archived checkers OTA analysis includes build 6225 in 44072a3-20240709_170103 LK group (https://github.com/bboe/firebreak/blob/main/docs/devices.md#checkers); promising but not a measurement of this unit's actual LK. Current Kiosk Satellite guide confirms supported 2024 LK, exact product AEOCH, amonet-checkers-v2.0.2.zip for first generation only, warns against stock updates (https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md#echo-show-5-1st-gen). Keep offline and do not reset/update; next unplug power, hold all three top buttons while reconnecting power, enter fastboot, test cable and read product/LK; stop before writes and confirm exact result. Physical label and USB stability unverified. No private serial/photo committed; documentation only.


### Physical Fastboot compatibility confirmed

2026-11-28: Physical unit enumerates via existing Micro-USB cable and Omarchy fastboot as regular user; read-only getvar product returns CHECKERS and lk_build_desc exactly 44072a3-20240709_170103. Stock Device Options confirmed first generation, build 6225. Correct earlier expectation that fastboot must print AEOCH: current Kiosk Satellite guide says AEOCH, but R0rt1z2 shared fastbrick script explicitly maps CHECKERS to Echo Show 5 first generation (https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh), and independent successful same-build physical H23K37 report records identical CHECKERS/LK values (https://www.mojowill.com/geek/echo-show-5-lineageos-macos-home-assistant/). Exact LK supported in guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md. Do not bypass any tool device guard. Before writes confirm physical label H23K37, read unlock_status and kaeru-version if supported, obtain exact first-gen amonet-checkers-v2.0.2.zip from maintainer XDA thread (direct fetch returned 502; archive not inspected yet), verify extracted device.prop/profile.sh, exact LK payload and bundled fastboot detection. No flash, no updates, no reset, no stock Wi-Fi, no private serial committed. Documentation checkpoint only.


### Unlock package extracted — pre-write check

2026-11-28: User confirmed unlock_status false and blank kaeru-version (no version reported). Downloaded/extracted named amonet-checkers-v2.0.2.zip on Omarchy; listing includes device.prop, profile.sh, fastbrick.sh, bundled fastboot binaries, fastbrick-20240709.img, checkers-kaeru.bin and twrp.img. Archive names alone do not prove provenance/integrity or exact device guard; next inspect device.prop, profile.sh and actual script, check bundled fastboot read-only product/LK, verify physical label if available. No firmware writes performed. Upstream guide reconfirmed https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md; upstream script maps CHECKERS https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh. Do not bypass device guards; keep power/USB stable and stock offline. No serial or local usernames recorded.


### Amonet profile and script preflight verified

2026-11-28: User supplied extracted amonet v2.0.2 device.prop/profile.sh/fastbrick.sh and bundled fastboot outputs. Profile DEVICE=checkers, explicit mapping of 44072a3-20240709_170103 to bin/fastbrick-20240709.img, script maps CHECKERS to 2019 first-gen, bundled binary reports exact same product/LK. User's observed locked state and earlier stock generation check match. No script changes or bypasses required; guide's AEOCH wording differs from actual CHECKERS recognized by maintainer script. Rechecked https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md and https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh. No independent archive checksum/signature verified; physical bottom label not yet explicitly confirmed. Next run original script from amonet directory using Bash, check exact product/LK/payload before YES; bootloader rewrite carries brick/data-loss risk, keep USB and power stable, no stock Wi-Fi. Script timeout is only probable success, not proof; successful TWRP 3.7.0_9-0 and adb recovery detection must be checked before proceeding to ROM installation. If failure or stock reboot do not blindly rerun or power-cycle mid-write. No writes performed as of checkpoint, no serials or private paths committed.


### TWRP reached after USB unlock

2026-11-28: User ran original amonet fastbrick.sh, correct CHECKERS/LK/payload detected, confirmed YES, reported likely successful exploit and photographed TWRP Unmodified System Partition prompt. Recovery visibly booted, confirming unlock procedure reached TWRP; exact recovery version and ADB status not yet measured. Next allow modifications for custom ROM, exit completed script, check adb devices and adb shell getprop ro.twrp.version (must be 3.7.0_9-0). Checked upstream first-gen guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md and release https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/releases/tag/checkers-2026.11.3 (27 Nov): lineageos-echo-kiosk-satellite-2026.11.3-checkers.zip SHA256 415b9e9621c2b012bfaa0e690bff8b7fc0e5c30a60b03fc67e7a14fec7fe68f2. Download on workstation, verify checksum, do not wipe until version and file verified. First install requires data/cache wipe (data loss), push image to /sdcard/update.zip, twrp install, stop on errors without reboot. Android and Wi-Fi/kiosk configuration still pending. No further device writes performed by assistant; no photos or serials committed.


### ROM pre-install verification passed

2026-11-28: User verified ADB recovery enumeration, ro.twrp.version exactly 3.7.0_9-0 and workstation ROM SHA256 exact match with published checkers-2026.11.3 release (415b9e9621c2b012bfaa0e690bff8b7fc0e5c30a60b03fc67e7a14fec7fe68f2). Rechecked upstream first-gen installation https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md and https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/releases/tag/checkers-2026.11.3. Ready for destructive initial install: twrp wipe cache, twrp wipe data (stock user data lost, /sdcard retained), adb push exact ZIP to /sdcard/update.zip, twrp install; inspect success before deleting ZIP and rebooting. Stop on any wipe/push/install error or assertion; leave recovery active, no blind retries. User to report install output before reboot. No device serial or personal file paths recorded, no actual ROM write yet confirmed. First boot ADB authorization, time sync, Wi-Fi, kiosk compatibility and trusted CA next.

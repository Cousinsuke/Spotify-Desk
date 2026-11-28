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


### LineageOS installation succeeded

2026-11-28: User successfully ran TWRP cache wipe, data wipe (retains /data/media), pushed verified checkers-2026.11.3 ZIP (432544228 bytes) to /sdcard/update.zip and installed via twrp install. Output reports target lineage_checkers Android 11 version 2026.11.3 and script succeeded result [1.000000], no errors reported. ROM installation accepted; first Android boot not yet confirmed. Next remove transferred update.zip only and adb reboot, allow initial boot, observe display and verify ADB/Android version after boot; authorize workstation ADB if prompted. Follow first-gen upstream guide for time/Wi-Fi and Kiosk Satellite configuration; no certificate trust bypass, no new pairing or live device access until verified TLS. Original Fire OS user data wiped. No private serials, raw logs or local paths committed; documentation only.


### Android first boot and ADB confirmed

2026-11-28: First Android boot verified after removing transferred ROM ZIP and rebooting. User approved USB debugging prompt; adb devices reports device, Android release 11, product checkers, sys.boot_completed=1. Next set time and zone using echo_service time sync, join trusted home Wi-Fi (prefer 5 GHz if split), observe automatic Kiosk Satellite installation using adb logcat -s ks-install and echo_service status. Upstream first-gen guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md confirms automatic install/device owner, no Home Assistant needed for our planned standalone URL (actual setup path to verify). Private CA documentation https://kiosksatellite.com/docs/tls/ confirms user-installed Android CAs trusted by app dashboard; restart app after installing. Transfer only verified public CA via USB, install through Android Security/Encryption & credentials; never ignore SSL errors, never copy private key. Confirm app installation and Wi-Fi first, then trust/pairing and fullscreen. No serial, fingerprint, Wi-Fi credentials or personal data committed; no new firmware changes.


### Echo time and offline status verified

2026-11-28: User verified echo_service time sync using Bash command `adb shell echo_service time sync "$(date +%s)" Europe/London`; prior Fish-style parentheses failed in actual Bash terminal, no device change from failed command. Status confirms 2026.11.3 KS, 542 MB available memory, 32.5 C, correct UK time and network time on, screen timeout never, USB ADB on/root off. Wi-Fi on but not connected, KS not installed, update hostname resolution fails; expected before joining network. Next use USB `adb shell echo_service adb wifi off` (documented in https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5.md) to restrict debugging to USB, open Android Wi-Fi settings with `adb shell am start -a android.settings.WIFI_SETTINGS`, join trusted home network via touchscreen, observe `adb logcat -s ks-install` and status. Installer should download after network connection, no manual APK or reflash yet. User CA transfer/trust and standalone kiosk path pending. No private device ID, network address, password, serial, or raw screenshot committed.


### Wi-Fi and Kiosk Satellite installation verified

2026-11-28: User connected Echo to home 5 GHz Wi-Fi, observed -63 dBm and automatic successful Kiosk Satellite 2026.11.36 download/install/device-owner/permissions via ks-install log. Status confirms 470 MB available RAM, 34.4 C, UK time and screen timeout never. Earlier DNS update-check failure still shown, likely prior offline check, installer clearly reached GitHub; not a blocker. Wi-Fi ADB still enabled; disable with documented echo_service adb wifi off while retaining USB. Next transfer only verified public CA via USB, Android Security > Encryption & credentials > Install a certificate > CA certificate; Kiosk Satellite documents user CA trust https://kiosksatellite.com/docs/tls/. No TLS bypass. Inspect actual Kiosk Satellite onboarding for standalone URL path: docs primarily describe HA, standalone setup not verified; do not install HA or enter tokens merely to advance onboarding. If no standalone option, consider separate lightweight kiosk browser/native wrapper. Do not enable lockdown until navigation/recovery verified. No SSID, IP, serial, host identifier, pairing codes or raw logs committed.


### Kiosk onboarding and certificate transfer

2026-11-28: User transferred public CA successfully (1537 bytes), opened Android Security settings, then launched Kiosk Satellite package me.jxl.kiosk_satellite. Photo confirms Welcome wizard with Connect (Home Assistant URL & token), Dashboard, Voice Satellite. Certificate installation not explicitly confirmed; Wi-Fi ADB off command returned nonzero, actual status not verified. Official https://kiosksatellite.com/docs/custom-pages/ supports external URLs as default dashboard after setup, but https://kiosksatellite.com/ documents HA connection/token for wizard and no standalone bypass has been verified. Next inspect Connect page for skip/standalone option, verify CA installed and wireless ADB status; no fabricated HA credentials or new HA deployment. If required connection cannot be skipped, use separate standalone kiosk browser or project-specific WebView wrapper that explicitly trusts the intended CA and rejects TLS errors; retain current ROM, avoid lockdown or removal until fallback tested. No sensitive data, screenshots, serials, addresses or tokens committed.


### Standalone kiosk direction after HA onboarding blocker

2026-11-28: Kiosk Satellite Welcome remote-admin password validation blocked progression with admin enabled and no password; advised disabling remote admin. User reached Connect screen showing mandatory Home Assistant base URL and long-lived token with Validate & continue, no visible skip. Upstream README https://github.com/jxlarrea/kiosk-satellite confirms reachable HA instance and token prerequisites. Custom pages support does not resolve initial onboarding. Recommend retain working LineageOS and build project-owned lightweight Android WebView wrapper (or standalone browser for interim test), no HA deployment. First inspect Android WebView provider, HOME activities, current device-owner/ADB state, local Java/Gradle/SDK availability; avoid removing current owner, changing launcher or locking down until replacement tested. App should use HTTPS-only trusted CA via Android network security configuration, no SSL bypass, no secrets in repo, persistent cookies, safe recovery/settings path; native volume/brightness and boot integration are later tests, not implemented. Public CA transfer confirmed earlier, trust installation remains unverified. No private logs or identifiers committed.


### WebView verified; HOME takeover recovery

2026-11-28: User verified current Android WebView com.android.webview 156.0.8078.47 enabled/valid, multiprocess enabled, 442 MB available memory, USB ADB on/Wi-Fi ADB off, root off. Launcher3 Quickstep and Kiosk Satellite HomeAlias both present; Home button stays in Satellite setup. Upstream https://kiosksatellite.com/docs/home-launcher/ confirms automatic HOME takeover on Echo image; first-gen guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/echo-show-5-1st-gen.md documents `adb shell setprop persist.echo.ks_install 0` to stop automatic installer. Try direct Launcher3 activity, stop automatic installer, set HOME with `adb shell cmd package set-home-activity com.android.launcher3/.uioverrides.QuickstepLauncher`, verify resolver and HOME behavior. If owner policy overrides, app provisioning home.enabled=false is a proposed inverse of maintainer's documented true example https://github.com/jxlarrea/kiosk-satellite/issues/947; not tested yet. No package removal, root or reset. Development host Bash has OpenJDK 27, no Gradle, SDK not detected. Choose separate JDK 17 and pinned compatible Android Gradle Plugin/wrapper, official SDK; avoid altering default Java or installing newest global Gradle arbitrarily. CA trust, launcher recovery and app build still pending. No private identifiers or network information committed.


### Launcher preference and JDK17 setup

2026-11-28: User confirmed persist.echo.ks_install=0 and set-home-activity Launcher3 returned Success; resolver query accidentally used HOME# rather than HOME, so actual resumed launcher remains unverified. Recheck corrected resolver and resumed activity before removing or disabling anything else. JDK17 installed alongside default JDK27 (17.0.21 verified). Next use official Linux Android command line tools package commandlinetools-linux-15859902_latest.zip (SHA256 4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583, https://developer.android.com/studio/#command-line-tools-only), user-local SDK, accept SDK licenses interactively, install platforms;android-35 and build-tools;34.0.0 for planned AGP 8.7.x/Gradle 8.9/JDK17 compatibility per https://developer.android.com/build/releases/agp-8-7-0-release-notes. Keep existing ADB and default Java unchanged. Development app not built yet; certificate trust and launcher recovery pending. No device or account identifiers committed.

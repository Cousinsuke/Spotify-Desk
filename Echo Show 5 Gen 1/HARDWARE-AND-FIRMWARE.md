# Hardware, purchasing and firmware research

Last reviewed 2026-11-26. Evidence is model-specific; recheck the upstream guide and release at installation time.

## Target hardware

| Item | Target |
| --- | --- |
| Device | Amazon Echo Show 5 first generation (2019) |
| Colour | Charcoal black |
| Label model | H23K37 |
| Codename | checkers |
| Fastboot product | AEOCH |
| Display | 5.5-inch, 960 x 480 |
| RAM | 1 GB |
| Power | UK 15 W adapter pictured with candidate; verify rating and inclusion |
| Data connection | Micro-USB, data-capable USB cable |

Alternative: second-generation Show 5 (2021), C76N8S / cronos, also has its own Kiosk Satellite image and unlock instructions; it is not the same as checkers and is not the current target. The first gen has a rear 3.5 mm audio jack, unlike the second. DSN is a unique device serial, not a model identifier; do not publish it. Third-generation support was not established. Larger 8-inch models rejected for size.

## Purchase history (not live stock information)

2026-11-26: User confirmed ordering an Echo Show 5. Delivery pending; the exact received device, final total and bootloader have not been verified. The discussed candidate is recorded below; the order details have not been independently inspected.

- Earlier eBay item 158301832586: £42.29, black H23K37, power supply pictured; subsequently reported sold.
- Current candidate eBay item 365443653119: £45.99, seller Excelstuff (99.2% positive, 31,731 feedback in screenshot), Very Good used condition, label H23K37 visible, UK 15 W plug pictured, two available at screenshot time, seller reportedly accepts returns in 30 days. Source: user screenshots/report. Actual purchase, postage, condition, accessories included and return eligibility are not independently verified. Multi-unit listing may not ship the exact photographed device.
- Direct listing: https://www.ebay.co.uk/itm/365443653119
- Preferred delivered price £25–40; £45.99 accepted as reasonable to consider if working and returnable, not a purchase confirmation. Historical prices and listings expire. Keep packaging; confirm screen/touch/Wi-Fi/speakers and adapter, check seller return terms. A normal return policy does not guarantee return eligibility after opening or flashing.
- No extra cable purchase yet; existing cables/adapter to test (see INSTALLATION-AND-USB.md).

## Firmware and bootloader evidence

Hardware support and installed bootloader exploitability are different. The Kiosk Satellite guide explicitly confirms 44072a3-20240709 and says Fastbrick USB cannot unlock the 2019 LK. It advises against updating stock Fire OS to obtain a newer bootloader. A motherboard test point method is mentioned in the XDA thread, but its applicability and risks for the actual unit are not verified.

Independent Firebreak analysis dated 2026-11-23 enumerates 23 archived checkers OTAs:

| Stock OTA build(s) | LK build description | USB assessment |
| --- | --- | --- |
| 6086 through 8851, except 8848 (21 archived builds) | 44072a3-20240709_170103 | LK family documented as supported by Kiosk Satellite guide; unit still needs checking |
| 8848 | fbacd25-20260415_104418 | Newer LK, Fastbrick compatibility not established; do not attempt |
| 2264 | cd178e6-20190703_190118 | Standard Fastbrick USB method unsupported |

Both 8848 and 8851 report Fire OS 6575.1, yet the archived 8851 image contains the older LK. A later build number therefore does not prove a newer LK. This is archived OTA composition evidence, not proof that a given device installed those partitions, and 21/23 is not a success probability. Firebreak is an analysis source, not an unlocking tool for this model. Community reports in November 2026 suggest the exploit was patched and then restored; an actual successful unlock on build 8851 was not independently verified in this project. Do not deliberately update or downgrade to it. No supported stock downgrade path has been established; signed firmware and rollback protections may prevent arbitrary flashing.

Prior research found recent community installation examples on the 2024 LK; they are anecdotal, not unit-specific guarantees. The original XDA thread was inaccessible in earlier research; check it again before any modification.

## Software choices

- Preferred candidate: model-specific Kiosk Satellite Edition of LineageOS 18.1 (Android 11); known release checkers-2026.11.2 (not asserted to be the latest at future install time). Guide requires amonet 2 and appropriate TWRP 3.7.0_9-0. The developer reports ~400 MB RAM available after an hour with the kiosk running, not a benchmark of our dashboard.
- Original Hardware Haven video uses the standard unofficial LineageOS port, Macro Deck, View Assist and its companion app. Kiosk Satellite was suggested in a viewer comment as easier to maintain. The comment is personal experience; no comparative benchmark exists.
- Kiosk Satellite custom pages can display external web pages; setup docs are Home Assistant oriented. Standalone use, certificate handling, and restart behavior must be tested. If Home Assistant dependency is unsuitable, evaluate a lightweight standalone Android WebView kiosk or standard LineageOS instead. TECHO5 is an alternative Linux project, not the same procedure as the video.
- Android 11/custom ROM security support is limited; keep device on a restricted network and maintain available patches.

## Sources

Rechecked 2026-11-26:
- [Kiosk Satellite model guide](https://kiosksatellite.com/docs/echo-show-5-1st-gen/)
- [Unlocking guide, exact bootloader check](https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md)
- [Firebreak archive analysis, checkers section](https://github.com/bboe/firebreak/blob/main/docs/devices.md#checkers)
- [Known release checkers-2026.11.2](https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/releases/tag/checkers-2026.11.2)
- [Custom pages](https://kiosksatellite.com/docs/custom-pages/)

Video description links transcribed from user screenshots (not all reopened this session):
- [Hardware Haven video](https://youtu.be/w4fUKE0RvS8)
- [XDA unlock/root/TWRP/unbrick checkers](https://xdaforums.com/t/unlock-root-twrp-unbrick-amazon-echo-show-5-1st-gen-2019-checkers.4762900/)
- [XDA unofficial LineageOS 18.1 for checkers](https://xdaforums.com/t/rom-unofficial-11-checkers-lineageos-18-1-for-the-amazon-echo-show-5-2019.4763475/)
- [Macro Deck](https://macro-deck.app/)
- [View Assist](https://dinki.github.io/View-Assist/docs/viewassist-setup)
- [View Assist companion](https://github.com/msp1974/ViewAssist_Companion_App/wiki/Getting-Started)
- [Kiosk Satellite second-generation guide](https://kiosksatellite.com/docs/echo-show-5-2nd-gen/)
- [TECHO5](https://github.com/HuskerMinion/techo5)
- [WebView Kiosk](https://f-droid.org/en/packages/uk.nktnet.webviewkiosk/)
- [Fire OS archive](https://ftvdb.com/echo/firmware/com.amazon.checkers.android.os/)
- [Community walkthrough previously found](https://note.com/axisrevo/n/n9d8e77e2750c?hl=en)


### Received Echo Show — stock firmware observed

2026-11-28: Echo Show arrived. User supplied stock Device Options photo confirming Echo Show 5 (1st generation), Fire OS 6.5.7.1 (NS6571/6225). No unlock/flash or read-only fastboot checks performed yet. Archived checkers OTA analysis includes build 6225 in 44072a3-20240709_170103 LK group (https://github.com/bboe/firebreak/blob/main/docs/devices.md#checkers); promising but not a measurement of this unit's actual LK. Current Kiosk Satellite guide confirms supported 2024 LK, exact product AEOCH, amonet-checkers-v2.0.2.zip for first generation only, warns against stock updates (https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md#echo-show-5-1st-gen). Keep offline and do not reset/update; next unplug power, hold all three top buttons while reconnecting power, enter fastboot, test cable and read product/LK; stop before writes and confirm exact result. Physical label and USB stability unverified. No private serial/photo committed; documentation only.


### Physical Fastboot compatibility confirmed

2026-11-28: Physical unit enumerates via existing Micro-USB cable and Omarchy fastboot as regular user; read-only getvar product returns CHECKERS and lk_build_desc exactly 44072a3-20240709_170103. Stock Device Options confirmed first generation, build 6225. Correct earlier expectation that fastboot must print AEOCH: current Kiosk Satellite guide says AEOCH, but R0rt1z2 shared fastbrick script explicitly maps CHECKERS to Echo Show 5 first generation (https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh), and independent successful same-build physical H23K37 report records identical CHECKERS/LK values (https://www.mojowill.com/geek/echo-show-5-lineageos-macos-home-assistant/). Exact LK supported in guide https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md. Do not bypass any tool device guard. Before writes confirm physical label H23K37, read unlock_status and kaeru-version if supported, obtain exact first-gen amonet-checkers-v2.0.2.zip from maintainer XDA thread (direct fetch returned 502; archive not inspected yet), verify extracted device.prop/profile.sh, exact LK payload and bundled fastboot detection. No flash, no updates, no reset, no stock Wi-Fi, no private serial committed. Documentation checkpoint only.


### Unlock package extracted — pre-write check

2026-11-28: User confirmed unlock_status false and blank kaeru-version (no version reported). Downloaded/extracted named amonet-checkers-v2.0.2.zip on Omarchy; listing includes device.prop, profile.sh, fastbrick.sh, bundled fastboot binaries, fastbrick-20240709.img, checkers-kaeru.bin and twrp.img. Archive names alone do not prove provenance/integrity or exact device guard; next inspect device.prop, profile.sh and actual script, check bundled fastboot read-only product/LK, verify physical label if available. No firmware writes performed. Upstream guide reconfirmed https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md; upstream script maps CHECKERS https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh. Do not bypass device guards; keep power/USB stable and stock offline. No serial or local usernames recorded.


### Amonet profile and script preflight verified

2026-11-28: User supplied extracted amonet v2.0.2 device.prop/profile.sh/fastbrick.sh and bundled fastboot outputs. Profile DEVICE=checkers, explicit mapping of 44072a3-20240709_170103 to bin/fastbrick-20240709.img, script maps CHECKERS to 2019 first-gen, bundled binary reports exact same product/LK. User's observed locked state and earlier stock generation check match. No script changes or bypasses required; guide's AEOCH wording differs from actual CHECKERS recognized by maintainer script. Rechecked https://github.com/jxlarrea/lineageos-echo-kiosk-satellite/blob/main/docs/unlocking.md and https://github.com/R0rt1z2/amonet/blob/mt8163-echo-show/fastbrick.sh. No independent archive checksum/signature verified; physical bottom label not yet explicitly confirmed. Next run original script from amonet directory using Bash, check exact product/LK/payload before YES; bootloader rewrite carries brick/data-loss risk, keep USB and power stable, no stock Wi-Fi. Script timeout is only probable success, not proof; successful TWRP 3.7.0_9-0 and adb recovery detection must be checked before proceeding to ROM installation. If failure or stock reboot do not blindly rerun or power-cycle mid-write. No writes performed as of checkpoint, no serials or private paths committed.

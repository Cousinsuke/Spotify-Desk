# Hardware — researched candidates, no approved wiring

**No final purchased bill of materials, electrical wiring/schematic or hardware runtime result has been accepted.** User has chosen **proposed parts for detailed verification**, not ordered them: Waveshare touch SKU **25948**, Adafruit push encoder **PID 377**, Waveshare AW9523B expansion **SKU 22132**. Read [ELECTRICAL review](HARDWARE-ELECTRICAL-REVIEW.md) (chip outputs/RESET, voltage, I²C adapter, proposed protected switch network) and [PRE-PURCHASE mechanical check](HARDWARE-PRE-PURCHASE-CHECK.md) before wiring/printing. The earlier costed proposals are in [HARDWARE-SHORTLIST.md](HARDWARE-SHORTLIST.md). Manufacturer-based technical research is available in **[HARDWARE-RESEARCH.md](HARDWARE-RESEARCH.md)** and the [model/expander comparison](HARDWARE-COMPARISON.md) (2026-10-20).

## Intended parts

| Part | Current direction | Status |
|---|---|---|
| MCU | ESP32-S3 integrated with Waveshare touch display | Candidate — exact Waveshare screen variant not yet user-accepted |
| Screen | Waveshare `ESP32-S3-Touch-LCD-4.3`, **SKU 25948** (capacitive touch) | **User-selected provisional part for verification; not ordered**. Manufacturer 106.1×67.8 mm full module, ~98×60 mm mount centres |
| Keys | **Three** of the user's four owned MX-style mechanical switches — Previous / Play-Pause / Next | Preferred mockup; 0.71 in (~18 mm) keycaps, switch mounting/spacing and wiring TBD |
| Knob | Adafruit **PID 377** 24-detent push encoder, 6 mm D shaft, plus **provisionally chosen Knob Zone KZ0087-01 flat ridged aluminium cap** (15.1 mm Ø × 15.2 mm total height) | **Not ordered**. KZ0087 grub-screw/6 mm round bore, max insertion 12.4 mm vs encoder nominal 15 mm shaft; press travel, exposed height and faceplate fit unverified |
| Case | 3D-printed | CAD/dimensions TBD |
| Power | USB-powered prototype preferred for simplicity | Electrical choice TBD |

## Revised front-panel concept (2026-10-20)

Three physical MX keys under the touchscreen and a rotary volume knob to its right. **Encoder press toggles PC/Wi-Fi mode.** Shuffle, repeat, settings and optionally PC/Wi-Fi remain touchscreen actions. The detached fourth-key icon was only a placeholder: **no fourth MX switch**. Required signals are **six**: three MX contacts, two encoder quadrature contacts (A/B), and its momentary push contact. See [DESIGN.md](DESIGN.md) for the tentative 0.71 in dimensions and mechanical checks. Earlier expander research assumed four keys; it remains useful but should not be mistaken for a finalized six-input requirement.

## Proposed simplest input module

User-selected provisional Waveshare **AW9523B IO Expansion Board SKU 22132**, about 38×23 mm, I²C address nominal 0x58, example UK £4.80, uses **six externally biased input signals** (3 MX, A/B, encoder push). A 5752 Adafruit QUAD encoder module with a real encoder counter is a more experimental alternative. Neither is purchased or wired. **AW9523B GPIO default to outputs (on 0x58, P0 LOW open-drain); internal RESET has 100k pull-down, so verify board-level reset pull-up**. A conditional 22k pull-up and 1k series-protected switch network for six inputs is documented in [HARDWARE-ELECTRICAL-REVIEW.md](HARDWARE-ELECTRICAL-REVIEW.md), **not signed-off wiring**. Display 4-pin I²C and expander 6-pin cable do not mate directly. Open electrical/mechanical risks are documented in [HARDWARE-PRE-PURCHASE-CHECK.md](HARDWARE-PRE-PURCHASE-CHECK.md). See [parts shortlist](HARDWARE-SHORTLIST.md).

## Critical researched constraint

The original 4.3 touchscreen uses most GPIO for RGB LCD and board peripherals. Its Waveshare guide lists onboard I²C addresses `0x20–0x27`, `0x30–0x3F`, `0x5D`, so **common MCP23017 expander address `0x20–0x27` conflicts**. An **AW9523 16-channel breakout (0x58)**, **TCA9539 (0x74–0x77)** or **Adafruit QUAD rotary breakout (0x49)** is a *candidate*, not a finalized part. The QUAD breakout could potentially read **three wired MX keys and the encoder push** from four switch contacts, plus one encoder's A/B signals; this off-label wiring still requires schematic and bench verification. Use the manufacturer's schematic and verify 3.3 V I²C power and hardware revision before wiring. See [detailed research](HARDWARE-RESEARCH.md) and its primary sources.

## Compatibility checks before buying

1. Identify exact Waveshare product page, board schematic, display/touch controllers and bus (RGB/SPI/etc.).
2. Check which signals occupy ESP32-S3 GPIO and which are truly free for keys/encoder; evaluate I/O expansion if necessary.
3. Confirm PSRAM/flash and LVGL/framebuffer support for 800 × 480 plus artwork, colour extraction and animation.
4. Verify safe logic levels, current requirements, reset/boot pin conflicts, USB wiring and cable lengths.
5. Check mount holes, glass visible area, touchscreen bezel thickness and case clearance.
6. Decide how firmware provisions network, stores pairing credentials, updates itself and recovers after a bad flash.
7. Determine whether the chosen display board already integrates MCU, PSRAM, USB and power to avoid unnecessary duplicate parts.

## Planned deliverables

Validated part/SKU shortlist, pinout table grounded in schematics, firmware framework decision, prototype wiring plan, mechanical CAD, software/hardware test checklist and procurement list with verified costs.

Do not confuse a demo 4.3-inch screen with another Waveshare 4.3-inch variant; resolution alone does not establish pin compatibility.

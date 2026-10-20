# Hardware — researched candidates, no approved wiring

**No final bill of materials, purchase or wiring/schematic has been accepted.** Manufacturer-based technical research is available in **[HARDWARE-RESEARCH.md](HARDWARE-RESEARCH.md)** and the [model/expander comparison](HARDWARE-COMPARISON.md) (2026-10-20).

## Intended parts

| Part | Current direction | Status |
|---|---|---|
| MCU | ESP32-S3 | Candidate |
| Screen | Waveshare `ESP32-S3-Touch-LCD-4.3`, **SKU 25948** (capacitive touch) | **Preferred research candidate**, not yet user-selected; B/C alternate boards documented separately |
| Keys | **Three** of the user's four owned MX-style mechanical switches — Previous / Play-Pause / Next | Preferred mockup; 0.71 in (~18 mm) keycaps, switch mounting/spacing and wiring TBD |
| Knob | **Push-capable** rotary encoder and ~18 mm outside-diameter knob right of display | Turn adjusts volume; **press toggles PC/Wi-Fi**. Encoder model/shaft/panel hole TBD |
| Case | 3D-printed | CAD/dimensions TBD |
| Power | USB-powered prototype preferred for simplicity | Electrical choice TBD |

## Revised front-panel concept (2026-10-20)

Three physical MX keys under the touchscreen and a rotary volume knob to its right. **Encoder press toggles PC/Wi-Fi mode.** Shuffle, repeat, settings and optionally PC/Wi-Fi remain touchscreen actions. The detached fourth-key icon was only a placeholder: **no fourth MX switch**. Required signals are **six**: three MX contacts, two encoder quadrature contacts (A/B), and its momentary push contact. See [DESIGN.md](DESIGN.md) for the tentative 0.71 in dimensions and mechanical checks. Earlier expander research assumed four keys; it remains useful but should not be mistaken for a finalized six-input requirement.

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

# Phase 6 — Proposed hardware shortlist (UK)

**2026-10-20 — user-selected provisional trio, not a purchase approval.** User chose Waveshare **25948**, Adafruit **377** and Waveshare AW9523B **22132** for pre-purchase verification. Research cost examples still apply; electrical wiring, CAD and firmware unvalidated. See [pre-purchase verification](HARDWARE-PRE-PURCHASE-CHECK.md). The confirmed interaction mapping is: **three MX keys** (previous, play/pause, next); rotary encoder clockwise/anticlockwise = volume, **integrated press** = PC/Wi-Fi mode. This is **six digital contact signals** including encoder A/B. Existing Phase 5.2 desktop code remains unchanged.

## Preferred compact prototype

| Component | Specific part | UK example price | Reason / caveat |
| --- | --- | ---: | --- |
| ESP32-S3 + touch display | Waveshare **ESP32-S3-Touch-LCD-4.3**, manufacturer **SKU 25948**, The Pi Hut WAV-25948 | **£31.70** | 800×480 touch; ~106.1×67.8 mm board; 270 cd/m²; 16 MB flash / 8 MB PSRAM. Be sure to select TOUCH, not no-touch 30493. |
| Knob with integrated push | Adafruit **Rotary Encoder + Extras PID 377**, The Pi Hut ADA377 | **£4.40** | 24-detent rotary, built-in momentary switch, 6 mm D shaft, supplied soft-touch knob; Adafruit-linked 450-BA761 *family drawing* indicates **~16 mm outside diameter**, close to 18 mm mockup; confirm actual supplied knob before CAD. |
| 16-input expansion | Waveshare **AW9523B IO Expansion Board SKU 22132**, The Pi Hut WAV-22132 | **£4.80** | Nominal I2C address **0x58**; ~38×23 mm, 3.3/5 V capable. Needs external bias resistors on switch/encoder contacts **and validated boot-time output/short-circuit protection**, and its 6-wire connector is NOT interchangeable with the display's four-wire I2C connector. |
| Keys | **3 owned MX switches**, plus 1u keycaps if not already available | Already owned switches | Use for previous/play-pause/next. |

**Base parts subtotal: £40.90**, before shipping, power/USB cable, cables/adapters, six external resistors, 1u keycaps if missing, solder/perfboard, fastening and printing. Values are observed example UK prices, not guaranteed stock quotes.

- Screen: https://thepihut.com/products/esp32-s3-4-3-touch-display-dev-board-800x480
- Encoder: https://thepihut.com/products/rotary-encoder-extras
- Waveshare AW9523B: https://thepihut.com/products/aw9523b-io-expansion-board

### Optional appearance change

- Adafruit 20 mm black aluminium knob, The Pi Hut ADA5527: **£2.90 observed**, but listing showed sold out. Fits a 6 mm shaft using set screw. Slightly larger than user's 18 mm concept; MUST verify push actuation is not obstructed by faceplate, and shaft fit, encoder push travel and knob weight.
- https://thepihut.com/products/anodized-aluminium-machined-knob-black-20mm-diameter

## Brighter-screen alternative

The **Waveshare ESP32-S3-Touch-LCD-4.3B**, **SKU 27848** (BARE, not factory-case SKU 28141) is rated **550 cd/m²** vs original **270 cd/m²**. Its module is **112.4×75.1 mm**, rather than 106.1×67.8 mm. At **~£35.60** (example), the difference is **£3.90**; paired with same encoder and AW9523B the base component subtotal is **£44.80**. It has the same ESP32-S3, 16 MB flash, 8 MB PSRAM, 800×480 display: no guaranteed FPS gain. The larger industrial-style PCB/terminals may complicate the 3-key/knob enclosure. Its I2C bus has extra onboard peripherals; verify its own schematic/address list, not only standard 25948 docs.

- Manufacturer: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B
- UK listing: https://thepihut.com/products/esp32-s3-development-board-with-4-3-capacitive-touch-lcd-display-800-x-480

## More reliable rotary-processing candidate

**Adafruit I2C Quad Rotary Encoder Breakout PID 5752**, **~£7.30**, default **0x49**. With Waveshare 25948 and encoder PID 377, component subtotal is **£43.40**. Firmware in its seesaw coprocessor accumulates rotary encoder counts. Potential off-label configuration: attach **three MX switches and the encoder's own push** to its four independent switch connections, and one physical encoder A/B to a single rotary footprint. Official guide reads four separate switch pins, but published pinout appears to assign seesaw pin 9 twice; must inspect actual PCB schematic and test each press **before approving this wiring**. The long four-encoder footprint may be difficult to conceal. Unlike standard AW9523B, seesaw board can count knob transitions without constant raw-state I2C polling.

- Product: https://thepihut.com/products/adafruit-i2c-quad-rotary-encoder-breakout-with-neopixel-stemma-qt-qwiic
- Guide: https://learn.adafruit.com/adafruit-i2c-quad-rotary-encoder-breakout/pinouts

## Mandatory checks before purchase or electrical hookup

1. **Exact display revision and geometry:** glass opening, full PCB (not just 4.3-in diagonal), back panel/screw holes, mounting height, USB, antenna and encoder/switch clearance.
2. **I2C address conflicts:** original Waveshare uses CH422G address ranges **0x20–0x27, 0x30–0x3F**, plus touch **0x5D**. Avoid MCP23017 at 0x20–0x27 or Adafruit single seesaw rotary breakout at 0x36–0x3D. AW9523B nominal **0x58** and Quad seesaw **0x49** avoid published reserved ranges; verify by 7-bit I2C bus scan before operation.
3. **3.3 V logic and connector pinout:** Waveshare original screen I2C 4-wire HY/PH2.0 vs AW9523B 6-pin PH2.0 or Adafruit JST-SH; connector plug formats/pin positions **do not match** automatically. Check SDA/SCL pullups, VCC selector, common GND with actual schematics; never wire 5 V directly to unprotected ESP32 GPIO.
4. **AW9523B input resistor bias:** chip does not have convenient internal switch pullups; plan external resistors for 3 MX + A/B + encoder press, debounce and test rotary steps under simultaneous Wi-Fi/LVGL/touch load. If it loses ticks, reconsider a dedicated counter such as QUAD.
5. **Encoder mechanics:** push-switch must work through the final knob, and intended ~18 mm visible outside diameter must not interfere with encoder nut/panel or nearby display.
6. **Firmware/software:** ESP-IDF+LVGL firmware and a secure device protocol are not yet implemented. Existing Flask/HTML/JS browser app cannot simply run on the ESP32-S3. Full screen rendering performance remains bench-untested.

**Provisional trio accepted for verification:** original Waveshare **25948**, Adafruit **377**, Waveshare **AW9523B 22132**. **No purchase authorization or validated harness/case**. Next gate is AW9523B-module startup/reset schematic review, 3.3 V 4-to-6 wire adapter, and internal CAD clearance; see [pre-purchase check](HARDWARE-PRE-PURCHASE-CHECK.md).

References:
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use
- https://www.waveshare.com/product/aw9523b-io-expansion-board.htm
- https://www.adafruit.com/product/377
- https://learn.adafruit.com/adafruit-i2c-quad-rotary-encoder-breakout/pinouts

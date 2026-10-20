# Phase 6 — Extended 4.3-inch screen and input-expander comparison

**Date: 2026-10-20. Research only.** This document assumed **four physical MX keys** at the time of investigation. The user's later mockup now prefers **three physical keys + one knob**; this remains valid expansion research but all required input-count comparisons are subject to that revised requirement. No hardware selected, ordered, wired or runtime-tested. Supplement to [HARDWARE-RESEARCH.md](HARDWARE-RESEARCH.md); the accepted software checkpoint remains Phase 5.2 / 7172c2e.

## Waveshare model comparison

| Board | SKU | Screen/physical | Notable hardware | UK example price | Fit for Spotify Desk |
|---|---|---|---|---|---|
| ESP32-S3-Touch-LCD-4.3 | **25948** | 800×480 capacitive touch, **270 cd/m²**, **106.1×67.8 mm** | 16 MB flash, 8 MB PSRAM, I²C extension, USB-C | **£31.70** at The Pi Hut | Best **compact** candidate; no six-pin free GPIO bank |
| ESP32-S3-Touch-LCD-4.3B | **27848** bare; 28141 with case | Same resolution, **550 cd/m²**, **112.4×75.1 mm** bare | 2 opto-isolated inputs and outputs, 7–36 V optional DC power | **£35.60** bare at The Pi Hut | Best if significantly brighter display matters; isolated digital inputs are not normal spare MCU GPIO |
| ESP32-S3-Touch-LCD-4.3C | **33799** bare; 33630 case | 800×480 touch; numeric brightness and board footprint **not confirmed from retrieved specs** | ES8311 audio codec, ES7210 ADC, microphone/speaker interfaces, 2 isolated inputs | **£36.91** at RobotShop UK | Only if built-in audio/voice is planned; audio circuitry alone does not enable Spotify protected streaming |

All use an ESP32-S3 and 16 MB flash/8 MB PSRAM, so none automatically produces smoother LVGL effects. For the album-colour glow, the Windows/Omarchy companion already generates sound-level data; screen audio I/O is not needed. The pre-built case variants are not proven to fit four additional MX switches and volume knob.

Official manufacturer sources:
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C

UK retail examples (prices and availability change):
- https://thepihut.com/products/esp32-s3-4-3-touch-display-dev-board-800x480
- https://thepihut.com/products/esp32-s3-development-board-with-4-3-capacitive-touch-lcd-display-800-x-480
- https://uk.robotshop.com/products/waveshare-esp32-s3-43-ai-voice-touch-display-development-board-800480-dual-microphones-wi-fi-bluetooth-5

## Original Waveshare 4.3 shared-I²C restriction

Manufacturer user guide reserves **0x20–0x27**, **0x30–0x3F** (CH422G), and **0x5D** (touch) on the original touchscreen's external I²C bus, SDA ESP32 GPIO8 / SCL GPIO9. **A default MCP23017 (0x20–0x27) and default Adafruit single rotary-encoder seesaw breakout (0x36–0x3D via jumpers) conflict.** Do not assume chip names or other Waveshare board revisions have the same exact wiring.

Original I²C VCC may be selected as 3.3 V or 5 V via hardware resistor/jumper. Before attaching an expander, verify the actual board revision, selector and voltage, ensure all I²C pull-ups are safe for 3.3 V ESP32 logic, and bridge the Waveshare HY2.0 connector to the breakout's JST-SH/STEMMA QT connector or header correctly. These connectors are **not plug-compatible** by default.

Waveshare guide: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use

## Expansion approaches for 4 owned MX keys + one volume encoder

**Updated physical concept:** three distinct MX switch inputs and two quadrature contacts = **five** required inputs, or **six** with optional encoder push. **Original research below was for four MX switches**, so some solutions are overprovisioned; no board must be bought for the obsolete key count.

| Candidate | I²C 7-bit address | Four keys + encoder? | Encoder handling | Prototype practicality |
|---|---|---|---|---|
| **Adafruit AW9523 16-GPIO breakout, PID 4886** | **0x58** default; selectable to 0x5B | Yes, six inputs | **Software reads raw A/B states**; polling may lose fast transitions | **Good compact/available first prototype**; ~£4.80 at The Pi Hut; requires **external pull-up/down resistors**, no internal selectable GPIO pulls |
| **Adafruit I²C QUAD Rotary Encoder breakout, PID 5752** | **0x49** default, configurable | **POTENTIALLY** one encoder plus four MX keys connected to four independent *push-switch pads* associated with the four encoder footprints | Onboard seesaw firmware counts rotation; more robust than raw-I²C edge polling | **Strong experimental all-controls option**, ~£7.30 UK; long PCB may be awkward in small case; wiring through otherwise-unused switch pads needs proof |
| **TI TCA9539**, suitable 3.3 V breakout/custom PCB | **0x74–0x77** | Yes, six GPIO | Raw input-state polling, no dedicated encoder counter | Clean custom design but more component/PCB work; needs external biasing |
| **Adafruit ATtiny817 seesaw generic breakout** | **0x49** | Four keys readily; encoder only if firmware supports/implements needed decoding | Extra firmware testing/custom work | Alternative input coprocessor, not easiest |
| **Adafruit SINGLE QT Rotary Encoder breakout**, PID 4991/5880 | **0x36–0x3D** stock | Encoder only, keys need more circuitry | Onboard rotation counter | **Conflicts** with original Waveshare CH422G at factory address; address can potentially be reprogrammed via seesaw EEPROM **off the shared bus**, but not plug-and-play |
| MCP23017 | **0x20–0x27** | Yes electrically | Raw input-state polling | **Conflicts**, exclude as normal recommendation |
| B/C built-in isolated digital inputs alone | Not standalone I²C expander | No: only two DI | Not enough | No |

### Option A details — AW9523

Adafruit's breakout supplies 16 GPIO input/output channels and interrupt line, but **no internal pull-ups or pull-downs**, requiring resistor bias networks on external MX/encoder contacts. A nominal 3.3 V input-high and grounded switch closure could use one appropriately selected resistor per input; component ratings and soldering plan remain unapproved. The Waveshare's four-wire external I²C connector does not expose a spare general purpose MCU interrupt pin by itself; absent an interrupt connection, poll the expander and test fast rotation while Wi-Fi, touchscreen and GUI run. Do not assume I²C polling is equivalent to a quadrature hardware counter.

Official: https://learn.adafruit.com/adafruit-aw9523-gpio-expander-and-led-driver/pinouts
UK listing: https://thepihut.com/products/adafruit-aw9523-gpio-expander-and-led-driver-breakout

### Option B details — Adafruit QUAD seesaw board as combined controller

The official Quad breakout has **four rotary footprints**, and **each has a separate switch contact/ground pair**. Hypothesis: wire the four MX switches to those four pairs, and attach *one* hand-rotated PEC11-style mechanical encoder to the A/B/ground pads of one encoder footprint. The onboard seesaw stores rotation counts and exposes all four switch inputs, potentially covering all desired physical controls using **one I²C board at 0x49** without an extra GPIO expander.

**Not yet proven:** this off-label use needs testing on actual hardware for all four switch contacts and independent encoder counting. The official online pinout lists 'pin 9' for *both* encoder #0 B and encoder #3 switch; **possible documentation inconsistency**. Before using that pin mapping, inspect the board's actual Eagle schematic and test a real unit; do not wire from that textual pin list. The full board has four spaced footprints, which may not fit our compact enclosure; wires from external switches can be used if electrically validated.

Official product: https://www.adafruit.com/product/5752
Official guide: https://learn.adafruit.com/adafruit-i2c-quad-rotary-encoder-breakout/pinouts
Hardware files: https://github.com/adafruit/Adafruit-I2C-Quad-Rotary-Encoder-Breakout-PCB
UK listing: https://thepihut.com/products/adafruit-i2c-quad-rotary-encoder-breakout-with-neopixel-stemma-qt-qwiic

### Option C details — TCA9539

Texas Instruments TCA9539 has 16 GPIO, four addresses (0x74–0x77), 1.65–5.5 V operation and an interrupt/reset facility. Like AW9523, it doesn't directly track encoder position; it reads GPIO state, so evaluate latency. Exact available easy-to-connect 3.3 V breakout/PCB is not identified.

Official https://www.ti.com/product/TCA9539

### Option D details — ATtiny817 seesaw

ATtiny817 seesaw generic breakout has 15 exposed GPIO and default address 0x49, but its GPIO breakout documentation does not establish that its **stock firmware** implements a quadrature counter appropriate for the future knob. It may require custom firmware.

Official https://learn.adafruit.com/adafruit-attiny817-seesaw/attiny817-breakout-pinouts

## Research-based recommendation, not selected hardware

For the first controlled prototype, compare:

1. **Waveshare 25948 + Adafruit AW9523** — compact, inexpensive board, straightforward four-switch inputs, but encoder performance must be measured and bias resistors added.
2. **Waveshare 25948 + Adafruit QUAD rotary breakout** — may combine four keys and one encoder into a single dedicated rotary-processing board, but only after verifying schematic pin independence, external MX wiring and enclosure fit.

Prefer Waveshare 4.3B if **brightness** significantly matters; 4.3C only if local microphone/speaker features matter. More inputs are not automatically accessible simply because B/C have isolated IO.

## Safe next research/bench checks (no purchase authorized)

- Clarify daytime brightness and custom enclosure priorities, and whether encoder push matters.
- Obtain exact Waveshare board revision and front/back mechanical drawings; measure actual glass/bezel and connector clearance before CAD.
- For AW9523: verify I²C bus logic voltage, GPIO input bias components and encoder step-loss under rendering/Wi-Fi load.
- For QUAD: inspect hardware Eagle schematic (especially duplicate numbered pin in published guide), bench-test all four switch pads and one encoder counter simultaneously, then consider its physical footprint.
- Verify HY2.0-to-STEMMA adapter/wires, shared bus occupancy with onboard touch/backlight controller, plus 3.3 V regulator and pullup requirements.
- Mark selection/implementation/runtime validation separately; none is yet accepted or ordered.

# Phase 6 hardware research — 4.3-inch ESP32-S3 compatibility

**Status:** Manufacturer-source research **completed 2026-10-20**. For a deeper comparison and additional readily-available input options, read [HARDWARE-COMPARISON.md](HARDWARE-COMPARISON.md). Findings and recommendations only; **no board, expander, firmware stack, wiring design or purchase is user-accepted yet**. Physical devices have not been tested.

## Constraints from the accepted project

- Display: 4.3-inch landscape touchscreen, 800 × 480; preserve Phase 5.2 artwork/progress/album-colour glow/controls visually when porting from the browser.
- Four existing MX switches: K1 previous, K2 play/pause, K3 next, K4 Wi-Fi/PC mode.
- Rotary encoder: two quadrature contacts; optional push switch (not yet assigned an action).
- 2.4 GHz Wi-Fi to the existing companion/API; likely USB 5 V for the first bench/desk prototype.
- Firmware is **not** the existing Flask/HTML/CSS/JS implementation. The ESP32 needs a separately implemented embedded display client (e.g. LVGL) and a secure protocol client. Existing audio meter originates on Windows/Omarchy, not from the screen's microphone.

## Screen shortlist (manufacturer documentation, not shopping approval)

| Exact board | Manufacturer SKU | Screen / memory | Footprint / distinguishing features | Research disposition |
|---|---|---|---|---|
| **ESP32-S3-Touch-LCD-4.3** | **25948** | 4.3-inch IPS RGB 800×480, capacitive 5-point touch, 16 MB flash, 8 MB PSRAM | **106.1 × 67.8 mm**, ~270 cd/m², USB-C 5 V input; I2C interface; no general-purpose header bank | **Preferred candidate** due to smaller size and no unused industrial/audio features. Not selected/purchased. |
| ESP32-S3-LCD-4.3 **without touch** | 30493 | 800×480, **no touchscreen** | 105.4 × 67.1 mm | Reject for the current interaction design. |
| ESP32-S3-Touch-LCD-4.3B | 27848; 28141 with factory case | Same resolution / 16 MB flash / 8 MB PSRAM | Standard 112.4 × 75.1 mm; case model 116.3 × 79 mm; brighter ~550 cd/m²; 7–36 V DC option and two **isolated 5–36 V / dry-contact digital inputs** | Alternative if the extra brightness or industrial hardware is needed. Do **not** mistake industrial input terminals for 3.3 V spare MCU GPIO. |
| ESP32-S3-Touch-LCD-4.3C | 33799 no case; 33630 with plastic case | 800×480 touch, 16 MB flash / 8 MB PSRAM | Has ES8311/ES7210 audio codec/microphone/speaker circuit | Only if built-in audio I/O becomes a requirement; it does **not** by itself provide Spotify streaming/playback rights or ability. |

Manufacturer references:
- Original: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3
- Original with touch product/sku: https://www.waveshare.com/esp32-s3-touch-lcd-4.3.htm?sku=25948
- 4.3B: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B
- 4.3C: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3C
- Original schematic and mechanical drawing: https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/manual/ESP32-S3-Touch-LCD-4.3-Sch.pdf

**Mechanical preliminary:** the original touch board drawing depicts roughly 106.1 × 67.8 mm module size, and dimension lines near 98 mm horizontal / 60 mm vertical between rear PCB mounting-hole features. This is a **provisional CAD reference, not an approved drilling pattern**: inspect actual revision, hole diameter, glass lip, front aperture, connector access and cable clearance when the part arrives. Do not copy B/C CAD dimensions.

**USB/power:** original manufacturer rating states 5 V, 450 mA (approximately 2.25 W nominal/rated consumption), *not* an independently validated maximum under Wi-Fi/backlight/animations or extra accessories. Use a suitable 5 V USB supply/cable with margin; measure actual peak consumption before finalizing. No battery is required for the desk prototype. The original has separate UART and native USB Type-C connections, with board-specific flashing instructions.

## Exact documented pin usage (original 4.3 touch board; this is NOT a free-GPIO map)

| Peripheral | ESP32-S3 GPIO |
|---|---|
| RGB LCD data/sync/clock | 0, 1, 2, 3, 5, 7, 10, 14, 17, 18, 21, 38, 39, 40, 41, 42, 45, 46, 47, 48 |
| Capacitive touch interrupt | 4 |
| I²C shared with touch, CH422G and breakout terminal | SDA **8**, SCL **9** |
| USB native | 19, 20 (shared/multiplexed on original board; do not repurpose) |
| microSD | 11, 12, 13 and CH422G-controlled CS |
| RS485 | 15, 16 |
| Backlight / touch reset / other onboard switching | via CH422G IO expander; these outputs are *not* generally free |

Source: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3 and schematic. **Critical:** manufacturer's old Wiki and current documentation appear to describe some CAN/USB mux signals differently. Treat exact CAN/RS485/non-display pin assignments as revision-dependent and verify from selected board schematic; *never* use these terminals as a shortcut to direct MX/encoder GPIO.

## CRITICAL: I²C address conflicts

Waveshare's **original-board user guide** explicitly reserves on its shared I²C bus:
- CH422G occupied addresses: **0x20–0x27**, **0x30–0x3F** (as shown in its bus-address table).
- Touch controller: **0x5D** (and potential alternate GT911 strap address 0x14 in other revisions).

Source: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use

**Do NOT use a standard MCP23017, MCP23008, PCA9535, TCA9555 or common PCF8574 breakout on this bus without carefully verifying nonconflicting addressing**: their typical configurable addresses collide. In particular, MCP23017 address 0x20–0x27 cannot be safely selected on this published bus. Merely seeing "I²C" and "GPIO expander" does NOT imply compatibility.

Two *research candidates* with nonconflicting nominal addresses:
1. **Texas Instruments TCA9539**: 16 GPIO over I²C; selectable addresses **0x74–0x77**, outside listed occupied ranges. Has interrupt and reset. **Requires suitable 3.3 V breakout/PCB**, stable pull-ups on each switch/encoder input, address-pin straps, and confirmation that the I²C pull-up/bus voltage is 3.3 V. Bare IC is SMD; no off-the-shelf plug-and-play module has been selected. Datasheet: https://www.ti.com/lit/ds/symlink/tca9539.pdf and https://www.ti.com/product/TCA9539
2. **Adafruit ATtiny817 breakout running seesaw**: nominal **0x49** address and 15 GPIO with configurable logic; a possible *prototyping alternative*. Confirm specific board availability, firmware features, rotary reading latency/implementation, and voltage before purchasing. Source: https://learn.adafruit.com/adafruit-attiny817-seesaw/attiny817-breakout-pinouts

Do not attempt to assign CH422G outputs already used for LCD backlight/reset as physical-key inputs. Even where a board has isolated *dry-contact* inputs (4.3B), only two are documented and electrical/interface behavior differs from an unrestricted digital input.

### Provisional logical mapping for a 16-bit compatible I²C expander (NOT physical wiring)

| Logical port | Intended signal | Needed |
|---|---|---|
| P00 | MX K1 previous | Yes |
| P01 | MX K2 play/pause | Yes |
| P02 | MX K3 next | Yes |
| P03 | MX K4 PC/Wi-Fi | Yes |
| P04 | Encoder A | Yes |
| P05 | Encoder B | Yes |
| P06 | Encoder push | Optional / no action selected |
| P07–P17 | Spare | Future |

For the TCA9539, provide **external GPIO input bias resistors** appropriate to the circuit rather than assuming MCP23017-like software-selectable pullups; scan/debounce input states and decode quadrature transitions. A fast-rotated encoder may need a dedicated rotary decoder or smarter I²C secondary MCU if bus polling misses edges. **Do not solder from this table.**

### Board power and I²C connector

- Original schematic explicitly depicts an I²C VCC selection between **3V3 and 5V** (H8). For a 3.3 V expander prototype, verify and select 3V3 and assess the logic/pullup network before connecting peripherals; never tie 5 V directly to ESP32 GPIO.
- The external terminal is **HY2.0/PH2.0 4-pin I²C**, not a standard Qwiic socket. Confirm the connector pin order **from the target PCB silk/schematic**, and use the included matching pigtail or an adapter.
- Shared bus already runs touch/control: test additional devices with a **7-bit I²C bus scan** before any permanent wiring.

Source: original schematic and manufacturer user guide.

## Memory, screen renderer and animation feasibility

- RGB565 full framebuffer: 800 × 480 × 2 = **768,000 bytes** (~750 KiB). Double buffer ~1,536,000 bytes (~1.46 MiB), before decoded artwork, LVGL heaps, network buffers and firmware. 8 MB PSRAM is plausibly sufficient for a carefully managed build, **not** a promise of zero stutter.
- Manufacturer reports example ESP-IDF v5.3/LVGL benchmark ~26 FPS single-core with a 21 MHz pixel clock (their example, **not** a Spotify Desk measurement). A lightweight, capped animated glow and partial/incremental redraws are safer than trying to reproduce Chromium CSS/JS directly.
- Espressif RGB driver supports PSRAM framebuffers and bounce buffers; Wi-Fi/flash bandwidth and cache interruptions can cause artifacts. Test artwork decode/refresh, touch, and continuous RGB redraw together.
- Firmware stack to **evaluate**: **ESP-IDF + LVGL** first, using Waveshare's official board example as hardware bring-up baseline. Arduino + compatible ESP32 display libraries is a valid alternate; no framework is formally selected.
- Existing Python PC audio meter should send only modest-level/smoothed audio amplitude samples via device bridge to make the LED-like glow react to PC audio. No PCM streaming to screen, no microphone required.

Sources:
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use
- https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Resources-And-Documents

## Open tasks BEFORE buying or printing

1. User confirms the preferred board (25948 standard touch, or 27848 B for brightness/industrial use, or 33799 C if sound actually needed). **No purchase yet.**
2. Download matching exact PCB revision/schematic and double-check all connector pinouts and I²C VCC selector. Do not accidentally order the no-touch 30493.
3. Choose a physically obtainable expander/breakout at a confirmed nonconflicting address, and test whether encoder polling is smooth. Budget at least six digital inputs and common ground.
4. Measure display PCB, visible glass, fixing-hole pitch/diameter, USB access, antenna keepout and rear clearance; then begin CAD.
5. First device proof: ESP-IDF/LVGL display + touch, Wi-Fi connection, basic text/status, input events. Only then integrate artwork caching, glow, pairing/security.
6. Review credentials/secure provisioning and define "Wi-Fi-only without PC" as *Spotify Connect remote control* versus local playback; no assumption that MCU decodes protected Spotify audio.

**State classification:** hardware researched and documented only. No accepted schematic, BOM, pin assignments, firmware, real device or hardware runtime test.

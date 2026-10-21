# Phase 6 — Pre-purchase electrical and mechanical verification

**Orientation update (2026-10-21, manufacturer STEP):** This document was written using component photographs from the *rear* of the PCB; front-view left/right placements were assumed. The actual 693-solid manufacturer's STEP puts **USB-C1/USB-C2 at the RIGHT edge when looking at the display glass**, and the **four-pin I2C H7 at the LEFT edge**. Historical right-I2C-to-encoder or left-USB-to-wall calculations below are **hypothetical mirrored scenarios**, not the verified component layout. See [Waveshare STEP inspection and corrected front-view drawing](HARDWARE-WAVESHARE-STEP-INSPECTION.md). Mating plugs and cable paths still unverified; no original CAD models have been changed.

**Date:** 2026-10-20. **Status:** Manufacturer document check + preliminary enclosure fit assessment. **Extended faceplate/cable fit and corrected Bourns shaft dimensions are in [HARDWARE-MECHANICAL-LAYOUT-STUDY.md](HARDWARE-MECHANICAL-LAYOUT-STUDY.md).** **Further chip/boot safety findings and provisional six-input resistor network are now in [HARDWARE-ELECTRICAL-REVIEW.md](HARDWARE-ELECTRICAL-REVIEW.md).** **No real device or wiring was tested**; no purchases authorized or final circuit verified. User has explicitly chosen these *proposed* parts for further checks (not yet bought):

1. Waveshare **ESP32-S3-Touch-LCD-4.3 / SKU 25948**, **WITH capacitive touch** (do not substitute no-touch SKU 30493).
2. Adafruit **Rotary Encoder + Extras / PID 377** (physical rotary plus integral normally-open press).
3. Waveshare **AW9523B IO Expansion Board / SKU 22132**.
4. Three of the user's existing MX switches, previous/play-pause/next, plus a 3D printed custom enclosure.

**The user-accepted input mapping** is encoder rotation = volume, encoder push = PC/Wi-Fi mode. This is **6 logical input channels**, consisting of 3 MX + encoder A/B + encoder push, all referenced to common ground.

## 1. Evidence tiers

- **Manufacturer verified:** nominal board sizes, 800×480 resolution, ESP32-S3 memory, general I²C pins, AW9523B connector functions, encoder contacts, and specified mechanical parameters below.
- **Engineering proposal:** input-port allocation, 3.3 V wiring concept, external bias resistors, interface adapter, boot safety and case envelope. No reviewed final schematic.
- **Awaiting physical verification:** specific board revisions, input address straps/reset bias, pullup selection, actual voltage and bus scan, rotary missed-pulse behavior, exact supplier-provided knob and available rear mounting space.

## 2. Original Waveshare screen: schematic and CAD facts

Manufacturer touch-product specs: **800×480**, **270 cd/m²**, **16 MB flash**, **8 MB PSRAM**, **5 V USB-C input**, **5 V / 450 mA published consumption figure**, 2.4 GHz Wi-Fi; *450 mA is not measured maximum with custom animations and Wi-Fi*.

From manufacturer schematic PDF **page 3** drawing:
- Touch panel/front module overall **106.10 ±0.10 mm wide × 67.80 ±0.10 mm high**.
- Display drawing labeled **95.54 ±0.15 mm horizontal × 54.36 ±0.15 mm vertical**. The drawing labels these with dimension arrows around the inner visible rectangle; before manufacturing confirm if these represent **viewing aperture or active-pixel area**, and do not conflate a 4.3-in diagonal with complete board.
- Approximate front dark-border offsets: **5.33 mm at right**, **9.09 mm bottom**; left 106.10−95.54−5.33≈**5.23 mm**, top 67.80−54.36−9.09≈**4.35 mm**.
- Rear PCB overall **106 × 68 mm** drawing, four fixing points shown at **98.00 mm horizontal × 60.00 mm vertical centers**, each nominally **4.00 mm inboard** from PCB edges. **Hole bore/fastener size not signed off**.
- Side drawing indicates **8.80 mm assembly depth** at one shown section, plus nearby 4.00 mm dimension; don't treat either as a guaranteed total cable/USB/screw clearance. Leave *additional* space for ports, rear pigtails, standoffs and airflow/antenna.
- Rear **left edge USB and UART USB-C ports**, **right edge sensor/CAN/I²C/RS485 sockets**, microSD near upper-right and 2.4 GHz ESP32 antenna area. Case must not cover programming/service access or place metal directly against PCB Wi-Fi antenna.

Source **schematic including dimensions**: https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/ESP32-S3-Touch-LCD-4.3-Sch.pdf
Manufacturer product docs: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3

**Critical prototype-clearance warning:** user's 1:1-like mockup positions 18 mm MX keys immediately under the *visible screen rectangle*, and the knob close to the screen's right visible edge. The actual module extends ~9 mm **below** and ~5 mm **right** of that rectangle, with rear hardware further into the body. Thus the full screen/module likely overlaps the proposed key/encoder mounting bodies in the same plane. *Avoid claiming mockup already fits physically*. Solutions to evaluate: wider/taller front panel, move keys farther down, move knob farther right, use offset/lower-level mounting planes if depth permits, and check holes near edges.

**Preliminary extra room estimates, not minimum manufacturer requirements:** start CAD exploration around **140–150 mm front-panel width × 100–110 mm height** to give the 106×68 mm module, 18 mm keys, ~16–18 mm knob, fixing hardware and wiring independent space. The original mockup may be smaller, but it is not a manufacturable dimensioned drawing. Confirm a CAD cross-section and exact parts before freezing any external measurements.

## 3. Manufacturer screen I²C power/connector

- Display uses **GPIO8 = SDA** and **GPIO9 = SCL** shared with existing touch and CH422G. Manufacturer publishes occupied I²C **0x20–0x27, 0x30–0x3F, 0x5D** on standard board. Proposed AW9523B default nominal **0x58** does not overlap.
- LCD schematic **page 1** draws external I²C connector signals **VCC, GND, SDA, SCL** and an **H8 selector** mapping external I²C VCC to **3V3 or 5V**. Verify the shipped board's selector is on 3V3 and *measure it* before connection.
- Screen's I²C connector is **4-pin HY2.0/PH2.0** and factory kit includes **HY2.0 4P to four 2.54 mm male wires** (check pin names and actual supplied harness before wiring).
- Do not directly tie a 5 V pullup rail to ESP32-S3 GPIO8/GPIO9. A nominal 3.3 V expander should share **3.3 V / GND / SDA / SCL** with screen only after confirming both ends' pullup voltages and common return.

Sources:
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use
- https://www.waveshare.com/esp32-s3-touch-lcd-4.3.htm?sku=25948
- https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/ESP32-S3-Touch-LCD-4.3-Sch.pdf

## 4. Waveshare AW9523B module 22132 — what is/ isn't verified

Manufacturer product lists:
- **38 × 23 mm** module, **16 configurable GPIO**, I²C control, onboard level-shifting, compatible 3.3 V or 5 V supply, programmable I²C address jumpers A0/A1; **INT** on port state change.
- A **6-pin PH2.0** interface **VCC, GND, SDA, SCL, INT, RST**, plus solder pads; one 6-pin pigtail included.
- **Default nominal device address 0x58** according to AW9523 silicon/typical unstrapped configuration; **actual board's straps and physical address must be checked before use**.
- LCD has **4-pin** interface while AW9523B has **6-pin**. Supplied plugs/harnesses **cannot mate directly**, despite similarly named connector families. A carefully labelled 4-signal wiring harness/adapter is needed; do NOT match wire colors blindly.
- **INT** is an optional change alert but display's four-wire connector provides *no spare INT GPIO*; initial prototype can read by **polling**. **RST** pin must be maintained inactive/high by module circuit; Waveshare's module demo allows optional no-connect for INT/RST, **but the module's own schematic/pullup circuit has not been independently reviewed**. Confirm before relying on unconnected reset; never leave a bare AW9523B RSTN floating by assumption.
- AW9523B **does not provide internal selectable pullups/pulldowns** for its GPIO. Plan **six externally biased input channels**; 3.3 V, for example one resistor per contact (10 kΩ is only a *starting design value*, not an approved BOM).
- **IMPORTANT chip boot behavior:** AW9523B datasheet says **all 16 GPIO default as outputs** on power-up, whose initial levels depend on address inputs. On 0x58 straps, port P0 outputs default LOW open-drain, suitable for an externally protected input design **after early firmware reconfiguration**. Actual AW9523B chip **RSTN has an internal 100k pulldown**: the module must provide an appropriate separate pull-up/drive as implied by Waveshare's 'RST could NC' example. Do not assume safe high-impedance inputs at boot: configure six selected pins as inputs at startup and consider **series current-limiting resistors / switch contact power-up safety** in the final circuit. Review exact board schematic and the datasheet before soldering keys tied straight to ground.
- Manufacturer specs say module has onboard level translator, but its precise voltage domains, pullups, signal route and power-up RST status cannot be certified without successful inspection of the **module schematic** and an actual board. The manufacturer's PDF is referenced but could not be fully retrieved; **no final connector-level wiring should be issued yet**.
- Rotary encoder mechanical contacts bounce and produce faster A/B transitions than ordinary keys. Poll expander reasonably fast during LCD+Wi-Fi workload, implement valid quadrature transition decoding/debounce, and verify direction/click count. If fast turns are missed, reevaluate a seesaw/hardware-counter input board.

Manufacturer:
- https://www.waveshare.com/product/aw9523b-io-expansion-board.htm
- https://www.waveshare.com/wiki/AW9523B_IO_Expansion_Board
- AW9523B silicon data: https://files.waveshare.com/upload/3/34/AW9523B-EN.pdf
- Module schematic listing: https://www.waveshare.com/wiki/File:AW9523B_IO_Expansion_Board_SCH.pdf (PDF retrieval currently blocked; **open item for further verification**)

### Logical six-pin input map (example, NOT final module pinout)

| AW9523B logical input | Function | Input circuit proposal |
|---|---|---|
| P0_0 | MX Previous | Input with pullup/bias and normally-open switch to common GND |
| P0_1 | MX Play/Pause | Same |
| P0_2 | MX Next | Same |
| P0_3 | Encoder A | Quadrature signal A, external input bias |
| P0_4 | Encoder B | Quadrature signal B, external input bias |
| P0_5 | Encoder press → PC/Wi-Fi toggle | Normally-open momentary switch to common GND; external input bias |

**No physical GPIO mapping/harness/pullup/series resistor values are user-accepted.**

## 5. Adafruit Rotary Encoder + Extras PID 377 — original datasheets verified

Adafruit 377 includes **24-detent / 24-pulse mechanical encoder** and a **separate normally-open momentary switch**. Encoder pins **A, C(common), B** plus two push-switch contacts = **five external signal terminals**; together with three MX keys this is six logical sensed inputs plus ground returns. The kit contains nut, washer and soft-touch knob.

Adafruit lists **PEC11-4215F-S24** datasheet. Decoding the Bourns PEC11 code:
- **L1 shaft length 15 mm**, **6 mm D-flat** shaft, **M7 × 0.75 threaded mounting bushing**. Importantly, the Bourns dimensional drawing also gives **l = 7.0 mm**, the bare shaft past the bushing end, for L1=15 mm; this is the pertinent insertion comparison with KZ0087's 6.0–12.4 mm shaft bore, not the full 15 mm L1 code.
- **Encoder body around 13.2 × 13.2 mm** (see mechanical drawing; PCB/side terminals extend farther).
- Momentary switch travel **0.5 ± 0.2 mm**. Don't allow the 3D-printed faceplate or knob to bottom out before activation; require axial clearance.
- Separate push switch is **normally open**; design click debounce and distinguish from rotation to avoid accidental volume change on mode press.

**Included knob drawing:** Adafruit's linked 450-BA761 family document depicts a **16 mm maximum flange/outside diameter** and **~14.5 mm knob height**, for a 6 mm D shaft. This is ~2 mm smaller in diameter than the user's rough **18 mm design circle** and can be evaluated *without* buying a replacement knob. But linked datasheet is a *family document* and seller kit may supply varying knob color/design; verify actual included piece once delivered.

Sources:
- https://www.adafruit.com/product/377
- Encoder datasheet https://cdn-shop.adafruit.com/datasheets/pec11.pdf
- Included knob family drawing https://cdn-shop.adafruit.com/datasheets/EPD-200732.pdf

## 6. Case/keys mechanical check

- User mockup: three ~18×18 mm 1u-style keycaps below the screen, right knob ~18 mm circular. Common MX-style **plate cutout about 14×14 mm**, **19.05 mm** keyboard pitch, but the final keycap type/switch plate and stabilizing/support material need confirmation. The case does not use the cap footprint as a through-cutout by default.
- The case must accommodate at least a **106.1×67.8 mm display module**, rear stand-offs and cables, **13.2 mm encoder body plus solder legs**, three switches + keycaps, a 38×23 mm AW9523B breakout and extra resistors/wiring. The same X/Y front-panel regions **cannot** contain two boards occupying the same mounting layer.
- Plan board/enclosure with correct attachment hole centers 98×60 mm *per PDF*, verify hole diameter, 2D positions, 3D offsets, connector envelopes and antenna clearance.
- **No realistic enclosure thickness/depth has been computed or accepted** without PCB + switch/keycap rear drawings and component placement. Do not order a custom PCB, machine panel holes or print final case based on the current sketch.

## 7. Acceptance gates

| Gate | Evidence | Present state |
|---|---|---|
| G1: Exact SKU and architecture selected as *proposed* | User selected 25948 / ADA377 / WAV22132 for verification | **Yes, conceptual proposed parts** |
| G2: Manufacturer interface / nominal supply compatibility | I²C bus 8/9, 3V3 select, AW9523B accepts 3.3 V, nominal address 0x58, encoder separate switch | **Verified in reference documents**, not by measurement |
| G3: Safe boot/reset behavior and module-specific schematic/adapter | Review expansion **module** PDF, resistor domains and reset pullups; explicitly draw 4→6-pin harness | **OPEN** |
| G4: Input-circuit design and fast quadrature tracking | Review resistor network/series protection; measure under LCD+Wi-Fi | **OPEN** |
| G5: 3D model case fit and mounting | Lay out 106×68 module + screws/cables + 3 MX + 16–18 mm knob/encoder + 38×23 breakout with real standoff depths | **OPEN** |
| G6: Physical hardware acceptance | Breadboard/bench test, screen/touch, keys, knob rotation/press, safe Wi-Fi | **OPEN** |
| G7: Firmware performance and LAN security | ESP-IDF/LVGL bring-up and companion communications tested | **OPEN** |

**Recommendation:** Proposed component combination is sound enough for a *controlled first-prototype direction*, but **not a final wiring/soldering guide or a validated enclosure**. Before buying, ideally retrieve Waveshare AW9523B module schematic (not only chip datasheet), define 3.3 V-safe breakout adapter and safe input boot strategy, and create a revised larger mockup/CAD cross-section. If early hardware buying is preferred, it carries residual risk of changing input module or printed case.

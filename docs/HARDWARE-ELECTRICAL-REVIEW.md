# Phase 6 — Electrical compatibility review: proposed Waveshare 25948 + Adafruit 377 + Waveshare AW9523B 22132

**Research date:** 2026-10-20. **Status:** Verified datasheet/interface logic + **conditional six-input circuit proposal**; no physical wiring, oscilloscope, bus scan, real-board test or final safety review. No purchase authorized. User has selected this *provisional trio* and a provisional Knob Zone KZ0087 cap.

## A. Findings now supported by primary documents

- Waveshare **ESP32-S3-Touch-LCD-4.3 SKU 25948** shares an I²C bus on ESP32-S3 **GPIO8 SDA / GPIO9 SCL** with its GT911 touch and CH422G; external HY2.0 **four-pin header has VCC, GND, SDA, SCL**. Display schematic H8 provides a choice of **3V3 or 5V I²C_VCC**; select and measure **3V3** for this prototype. Screen schematic shows a discrete bus level-shifting/bias network, so check *actual bus voltage* before connection.
- The **Waveshare AW9523B IO Expansion Board SKU 22132** manufacturer confirms **six-pin PH2.0 interface: VCC, GND, SDA, SCL, INT, RST** and separate I/O breakout pins; 3.3V/5V power and 38×23 mm physical size. A screen four-pin peripheral cable and module six-pin cable **are not plug-compatible**, despite nominal 2.0 mm pitch. Use independently identified wires/solder pads or a keyed custom adapter **only after verifying physical orientation and PCB revision**, not matching colours.
- Chip AW9523B default I²C 7-bit address **0x58 when AD0/AD1=0**. The screen documents occupied addresses **0x20–0x27, 0x30–0x3F and 0x5D**; no documented collision at 0x58 on this exact screen. The expansion module's A0/A1 jumpers and bus scan must still be checked.
- Adafruit **PID 377** is a quadrature rotary encoder with **A/B/C(common)** rotation contacts and a separate **normally-open push switch**. It does not require a separate 5 V logic supply. Three MX keys + 2 quadrature contacts + encoder push = **six sensed signals**, plus shared ground.

Primary sources:
- Waveshare screen board/schematic: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3 and https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/ESP32-S3-Touch-LCD-4.3-Sch.pdf
- Waveshare expander product and manufacturer wiki: https://www.waveshare.com/product/modules/others/interface-expansion/aw9523b-io-expansion-board.htm and https://www.waveshare.com/wiki/AW9523B_IO_Expansion_Board
- Waveshare module schematic official file entry: https://www.waveshare.com/wiki/File:AW9523B_IO_Expansion_Board_SCH.pdf and indexed mirror https://www.waveshare.net/w/upload/2/28/AW9523B_IO_Expansion_Board_SCH.pdf
- Chip AW9523B v1.5 datasheet: https://files.waveshare.com/upload/3/34/AW9523B-EN.pdf
- Encoder: https://www.adafruit.com/product/377 and datasheet https://cdn-shop.adafruit.com/datasheets/pec11.pdf

## B. GPIO startup and reset behaviour — critical

Verified AW9523B **silicon** datasheet:
1. **All GPIO reset to output**, configuration registers **0x04/0x05 default 0x00**. With address straps AD1=AD0=GND (nominal **0x58**), **P0_0..P0_7 start as output LOW and open-drain**, while P1 starts push-pull LOW. Other address straps cause different default outputs/high-impedance combinations; verify actual module selection.
2. Software sets P0 input direction by setting its configuration bits **1=input**. For six inputs on P0_0..P0_5, writing **0xFF to 0x04** puts all P0 pins in input mode, including unused P0_6/P0_7 (ignored by application). Software should never drive the external switch pins as outputs. **0x10 reads fixed chip ID 0x23**.
3. Data **0x00 reads P0 input states**. AW9523B **has no GPIO internal pull-up/pull-down selection**, so external bias is needed. Datasheet shows **VIL max 0.4 V; VIH min 1.4 V**.
4. On power, datasheet recommends ~**100 µs before release of RSTN** and **at least 5 ms before first I²C communication**. AW9523B has **internal RSTN 100 kΩ pull-down** (not pull-up). An independent external RESET pull-up/drive arrangement is therefore required. Waveshare's manufacturer **module wiki explicitly says RST may be NC**, and online-indexed manufacturer module schematic text shows several 10 kΩ resistors and RESET net; this *suggests* a board-level pull-up. However the full AW9523B **module** PDF could not be rendered/visually traced: **RESET pull-up/net connectivity and correct power-up timing remain unverified on actual module**. Do not conflate the Adafruit AW9523 breakout's documented 10 kΩ pull-up with verified details of the *Waveshare* module.
5. The Waveshare module manufacturer wiki says the **INT pin may also remain unconnected**; the screen's I²C connector does not provide a spare GPIO for interrupt. For the initial version **poll P0**; disable interrupt enables in software if necessary. Be aware this means encoder steps could be missed while ESP32-S3 is rendering or busy with Wi-Fi.

Chip datasheet (default behaviour, logic thresholds, reset timing):
https://files.waveshare.com/upload/3/34/AW9523B-EN.pdf
Manufacturer module wiki (INT/RST NC):
https://www.waveshare.com/wiki/AW9523B_IO_Expansion_Board

## C. Proposed protected input cell (DESIGN EXAMPLE, not approved soldering schematic)

For **each** P0_0..P0_5:

- External resistor **Rp = 22 kΩ** from AW9523B **P0_x signal node to measured 3.3 V**.
- External resistor **Rs = 1 kΩ** **in series** between AW9523B P0_x node and a normally-open MX/encoder contact; other side of contact to common GND.
- When released, signal approaches **3.3 V**; when pressed, resistor divider yields approximately **3.3 × 1/(22+1) = 0.143 V**, well below the silicon's **0.4 V max LOW** input threshold. Pull-up-only boot current with P0 output LOW is about **3.3/22,000 = 0.15 mA/channel**. If firmware mistakenly drives pin HIGH while contact held, 1 kΩ limits the approximate pin-to-GND current to less than **3.3 mA** (plus leakage/pull resistor path). **These are preliminary calculated bounds**, not proven board-current/EMI tests. Resistor tolerances, wiring, bounce, switch/encoder form and chip current ratings must be reviewed.
- This network specifically avoids *directly shorting* any potentially high-driving output to ground. On the normal 0x58 / P0 LOW boot setting, the external pull resistor creates only a modest load. Do not substitute P1 pins or move address jumpers without reconsidering boot drives.
- **Six identical networks** plus common ground: P0_0=MX previous, P0_1=MX play/pause, P0_2=MX next, P0_3=encoder A, P0_4=encoder B, P0_5=encoder integrated push (PC/Wi-Fi). Encoder C(common) and one terminal of push switch connect to ground; three MX switch other terminals also to ground. This is **logical pin choice only**, and does not authorize physical wiring until board/schematic confirmation.
- No diode is required for three independently wired switch GPIOs in this design. Hardware debounce/EMI capacitors **not chosen**; software debounce for MX & encoder press and quadrature state tracking required.

### Register-level firmware bring-up idea (NOT implemented)

1. Wait for stable supply and chip reset release; allow at least the datasheet's **5 ms** before I²C.
2. Probe I²C 0x58 (and verify no conflict with touch); read device ID register **0x10 → 0x23**.
3. Set port P0 to GPIO mode (default LEDMODE P0 register **0x12 = 0xFF**), configure direction **0x04 = 0xFF (inputs)** as early as possible.
4. Poll P0 input register **0x00** and mask **0x3F** for six required signals. Optionally disable unused interrupts; do not rely on unsupported GPIO interrupt routing. Ignore transient initial samples until stable.
5. Verify key presses, mode push, clockwise/counter-clockwise encoder steps under **display rendering + active Wi-Fi**. Fast turns must be tested; quadrature polling can miss pulses. If loss is frequent, a dedicated encoder-decoding controller such as Adafruit QUAD seesaw **0x49** is the fallback.

Firmware cannot run existing Flask HTML directly on ESP32-S3; ESP-IDF/LVGL and device protocol implementation are separate future development.

## D. Module schematic source status

**Progress:** The original manufacturer AW9523B module schematic is findable and indexed on Waveshare's file page, including nets and component values (R1–R4 **10k**, jumpers JP1/JP2 **0R**, R5/R6 **NC** in search index), and H3/H4 six-pin interfaces. However the PDF bytes from Waveshare files/waveshare.net were blocked in the available viewer. Therefore **the full board-specific connectivity could not be visually traced/certified**: which 10k resistor pulls RESET/INT/SDA/SCL, A0/A1 strap topology, connector orientation and actual level translator supply domains remain open. The module's PCB revision may differ from the indexed document.

Do **not** assert that Waveshare's RESET is safely pulled up without validating the circuit or measuring the powered board. The chip itself has an internal **pull-down** on RESET, so the correct board-level pull-up is important.

## E. Gate status before physical build

| Gate | Status | Needed next |
|---|---|---|
| Product identification | **Pass on paper** | 25948 touch + ADA377 + AW9523B 22132 + chosen KZ0087 cap |
| I²C address compatibility | **Pass on paper** | I²C scan on actual unit confirms 0x58, 0x5D and CH422G addresses |
| Nominal 3.3 V connection | **Pass in specs** | Set H8 to 3V3; measure power and SDA/SCL when powered |
| Four vs six wire connector | **Adaptation required** | Check actual connector pin-1 orientation; make verified labelled 4-signal adapter |
| Reset/level shifter/module schematic | **OPEN** | Visually obtain and inspect full manufacturer module PDF, especially RESET pull-up and startup |
| Six input electrical protection | **Proposed and mathematically checked only** | Test 22 kΩ + 1 kΩ network on actual hardware; power-on with contacts open/pressed |
| Encoder pulse retention | **OPEN** | Test slow/fast clockwise/counterclockwise rotation with simultaneous UI and Wi-Fi |
| Case/knob geometry | **OPEN** | Check 106×68 mm screen rear PCB vs 18 mm MX and 15.1 mm KZ0087; verify KZ0087 max insertion 12.4 mm versus encoder nominal 15 mm shaft and push travel |
| Hardware procurement | **Not authorized** | Finish module schematic verification and CAD clearance or explicitly accept prototype residual risks |

**Bottom line:** The proposed trio is viable and shares suitable control-voltage and bus specs. The real outstanding work is **Waveshare module schematic/reset/pin-1 proof**, then physical resistor/bus/encoder validation. The circuit above is **an engineered proposal only**, not guaranteed safe instructions for directly hooking up boards sight unseen.

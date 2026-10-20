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

## F. Continued research — module schematic index, newer chip datasheet and connector caveats (2026-10-20)

**NEW SOURCE:** A web-indexed *copy of the exact Waveshare board schematic PDF* provides more net names than the product datasheet, although the PDF server displays an anti-bot gate and its **graphical wiring was not visually accessible**. Indexed extracted text identifies:
- Chip U1 **AW9523B**, H3/H4 **six-pin duplicated external interfaces** with terminal labels in listed order: **VCC, GND, SDA, SCL, INT, RESET** (corresponding H3/H4 connectors). **Physical plug orientation and pin-1 marking still must be checked on PCB before wiring.**
- **R1, R2, R3, R4 = 10 kΩ**; R5 and R6 **not populated (NC)**; **JP1/JP2 = 0 Ω** address pads; C2 **100 nF**. The search-extracted netlist places R1/R2 on **VCC** and a RESET label nearby, strongly supporting *some onboard reset/pullup network*, but the exact **which-resistor-to-which-net** graph still cannot be certified from text extraction alone.
- The indexed schematic footer misleadingly says **MCP23017 IO Expansion Board** even though U1 is AW9523B. Treat the component and silkscreen details as board-version-specific and inspect shipped revision; do not substitute an MCP23017 breakout merely from document footer.
- Waveshare's own **product/wiki examples explicitly allow INT/RST NC** on the module's 6-pin external harness. This is stronger module-level evidence of autonomous reset behavior than the silicon datasheet alone, but does not conclusively prove the precise RST pull-up resistor topology.

Exact indexed manufacturer PDF: https://www.waveshare.net/w/upload/2/28/AW9523B_IO_Expansion_Board_SCH.pdf
Manufacturer file-list page: https://www.waveshare.com/wiki/File:AW9523B_IO_Expansion_Board_SCH.pdf
Official board product: https://www.waveshare.com/product/aw9523b-io-expansion-board.htm
Board wiring guide: https://www.waveshare.com/wiki/AW9523B_IO_Expansion_Board

**NEW CHIP DOCUMENT:** Awinic's **March 2024 v2.4 AW9523B datasheet** (newer than Waveshare's archived 2019 v1.5) reconfirms the default 16 GPIO **outputs**, port P0 **open-drain**, RSTN **internal 100 kΩ pull-down**, input **VIL max 0.4 V / VIH min 1.4 V**, and the standard port-control register addresses. The previously proposed 22k/1k contact-bias calculation still meets these *nominal* chip thresholds at 3.3 V. The new datasheet does **not** validate assembled module resistors, startup timing, EMI, switch bounce or hardware rotary counting.

Chip v2.4: https://doc.awinic.com/doc/202403/deffbf3b-7e7b-4ff6-8e91-fd85e2d845d5.pdf

**Important screen-side condition:** the Waveshare screen schematic's I2C connector H7 and voltage jumper H8 show the external 4-signal order **VCC/GND/SDA/SCL** by labels. H8 default diagram indicates 3V3, but measure it and SDA/SCL logic before connection. Screen PCB **I2C connector is on the right edge**, where the chosen encoder would sit. Check physical plug exit and routing rather than assuming clearance from front view.
Screen schematic page 1 plus geometry page 3: https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/manual/ESP32-S3-Touch-LCD-4.3-Sch.pdf

### More precise first hardware bring-up gate

1. With **nothing connected to I2C**, power the exact Waveshare 25948 and record H8 setting plus voltage of I2C VCC and idle SDA/SCL relative to GND. Power from a suitable 5 V USB source.
2. Before joining two modules, read printed pin labels and verify both supplied 4-pin and 6-pin harness conductors using a multimeter/continuity check, **not wire colors**. Only the four *named* signals VCC, GND, SDA, SCL will be joined after 3.3V verification; leave INT/RST unused only if actual board confirms autonomous reset.
3. Verify expander **VCC to RESET level** with a high-impedance meter during isolated power-up, or inspect board traces/schematic properly; confirm device acknowledges address **0x58** and returns expected ID **0x23**. If it remains in reset, **do not connect directly to ESP32 GPIO without reviewing reset circuit**.
4. Only after expander register test, separately test protected switch inputs and quadrature tracking. No hardwired 6-input contact harness approved yet.
5. Simultaneously test LCD, touch and Wi-Fi while polling A/B at provisional **2–5 ms** intervals; rotary contact bounce can itself be up to **5 ms** per Bourns PEC11 datasheet. Count detents vs observed volume steps; if unreliable, consider dedicated seesaw decoder.

**No soldering recipe was signed off.** Missing proof is now narrowed to the exact H3/H4 orientation, actual RESET pull-up circuit/module PCB revision, 3.3V measurement, and real encoder edge retention; manufacturer materials otherwise support the architecture. Pair with [the mechanical fit study](HARDWARE-MECHANICAL-LAYOUT-STUDY.md).

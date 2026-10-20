# Phase 6 — Faceplate / clearance study (not final CAD)

**Research update 2026-10-20. Status: manufacturer-dimension-based 2D exploration only.** No physical 3D parts measured, case printed, enclosure approved or hardware purchased. User's accepted physical controls: **3 MX keys** (previous/play-pause/next) beneath touchscreen and **Adafruit 377 push encoder** right of screen, with **KZ0087-01** flat black aluminium knob selected provisionally (press = PC/Wi-Fi). The detached fourth icon is not a control.

## Grounded hardware dimensions

| Component | Manufacturer documented | Important clarification |
|---|---|---|
| Waveshare ESP32-S3-Touch-LCD-4.3 with touch SKU 25948 | Glass/face module **106.10 ±0.10 mm W × 67.80 ±0.10 mm H**; inner display rectangle **95.54 ±0.15 × 54.36 ±0.15 mm** | The **4.3-inch** description is diagonal of inner active screen, not the complete casing/PCB. |
| Screen glass outer to visible rectangle | Left ~5.23 mm, right **5.33 mm**, top ~4.35 mm, **bottom 9.09 mm** | Derived from manufacturer dimension arrows; inner display rectangle offset **cannot** be treated as mounting hole position. |
| Rear PCB | Roughly **106 × 68 mm**, mounting-hole centre pitch **98 × 60 mm** | Four screw/hole features inset ~4 mm from PCB edge. Actual hole diameter/stand-offs require revision check. |
| Rear connectors | USB-C UART and USB on **left**, I2C/sensor/CAN/RS485 connectors on **right** | Crucial: **I2C cable plug and bend compete for space at right of LCD where user wants knob**. Do not put the knob PCB immediately against the right edge. |
| Adafruit PID 377 encoder | Bourns PEC11 body **13.2 × 13.2 mm**, **M7 × 0.75** bushing, **0.5 ± 0.2 mm push travel** | Body dimensions **exclude solder legs, PCB and any switch mounting parts**. A 7 mm threaded hole is *not* necessarily final tolerance; washer/nut, panel thickness and service access matter. |
| Adafruit PID 377 shaft | Bourns PEC11 15 mm shaft code **L1 = 15 mm**; same drawing shows **l = 7.0 mm for 15 mm model**, i.e. shaft beyond end of threaded bushing | **CORRECTION:** prior comparisons erroneously treated '15 mm shaft' as a 15 mm shaft requiring insertion inside knob. Usable bare projection past bushing is about **7 mm**, which falls within KZ0087 maker's **6.0–12.4 mm insertion** spec. This improves plausibility, but still does not prove grub screw can engage/knob clears mount or push works. |
| Knob Zone KZ0087-01 | **15.1 mm outside diameter × 15.2 mm overall height**, **6 mm round bore with grub screw**, inserted shaft range 6.0–12.4 mm | *Knob overall height* is not *height exposed above case*. The latter depends on recess, panel plane, encoder/washer/nut location and permitted push travel. User wants RK M75-like low exposed height. |
| Cherry MX-style keys | ~**18×18 mm cap** from user's mockup, nominal **14×14 mm plate cutout**, **19.05 mm standard pitch** | Switch exact manufacturer/model and whether plate-mounted / PCB-mounted not identified; under-panel switch body, wiring and keycap travel need actual part measurement. |
| Waveshare AW9523B expansion PCB | **38×23 mm**, six-pin PH2.0 I2C cable and 16 GPIO | Needs mounting/insulation + six 22k and six 1k resistors if proposed protected circuit retained. Not assumed to fit directly behind display without clearance verification. |

Manufacturer reference Waveshare original schematic **page 3** (actual dimensioned drawing): https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/manual/ESP32-S3-Touch-LCD-4.3-Sch.pdf
Adafruit-listed Bourns drawing: https://cdn-shop.adafruit.com/datasheets/pec11.pdf (page 2/3 depending PDF page numbering; push-switch drawing with table L1=15, LB=5, l=7)
Knob details: https://knobzone.co.uk/products/kz0087
Keyboard switch references: https://www.farnell.com/datasheets/1792245.pdf and https://wiki.ai03.com/books/case-and-plate-design/page/switch-dimensions-and-physical-specifications

## Two provisional top-face layouts (all x/y in millimetres from top-left)

These rectangles are **illustrative starting points**, not confirmed ergonomic spacing or manufacturable 3D case geometry. Touch glass dimensions here are modelled as full 106.1×67.8 footprint; faceplate and glass should not be drilled using active-pixel dimensions.

| Position | More compact trial | Comfortable cable-clearance trial |
|---|---|---|
| Front panel outside | **150 W × 105 H** | **165 W × 110 H** |
| Screen module top-left | x=8, y=7 | x=11, y=8 |
| Screen module right/bottom | x=114.1 / y=74.8 | x=117.1 / y=75.8 |
| Key cap centre X (Prev/Pause/Next) | x=39,69,99 | x=40,70,100 |
| Key cap centre Y | y=86 | y=91 |
| Keycaps physical bounding y | y=77–95 | y=82–100 |
| Minimum 2D vertical gap between screen bottom and top edge of keycaps | **2.2 mm** | **6.2 mm** |
| Knob centre x,y | x=131, y=41 | x=142, y=44 |
| Knob rim (diameter=15.1) closest horizontal distance to screen full module edge | **9.35 mm** | **17.35 mm** |
| Knob rim distance from right outside panel edge | **11.45 mm** | **15.45 mm** |

The *comfortable trial* appears better for servicing/mounting and routing a right-side I2C plug, but even **17 mm clearance is not a proven cable-bend allowance**. The plug may exit in a direction that conflicts with the encoder body; judge with PCB photo, connector direction and a physical prototype. The compact trial may require an angled pigtail or relocating the knob/connector.

For the comfortable trial, module visible rectangle would begin approximately at **x=16.23, y=12.35**; the more prominent **9.09 mm bottom black bezel** means artwork appears vertically offset within the module compared with a perfectly centred 4.3-inch screen rectangle. This can affect proportions of the front mask.

## Additional unresolved mechanics

1. **Left USB-C service access:** 25948 has both native USB and USB-to-UART Type-C ports on **left PCB edge**, which may require openings/accessibility through outer case wall or internal USB-C extension. Do not permanently seal flash/recovery port.
2. **Right-side I2C:** route the included four-wire pigtail away from the encoder, with enough clearance for unplugging and bending without stressing the PCB; reserve separate power/GND/SDA/SCL wires to AW9523B's six-wire connector.
3. **Depth:** panel/front shell must support 13.2 mm encoder housing, switch bodies/contacts, ~8.8 mm display assembly feature, rear PCB components, standoff lengths, AW9523B daughterboard and wiring; no single verified depth yet.
4. **Plate cutouts:** verify whether the user's MX switches are plate-mounted and if 3D-printed switch-latch design can support repeated clicking. Hole tolerance 14×14 mm is a *nominal* keyboard-guide starting point and should be tested on a printed plate coupon.
5. **Push knob travel:** ensure KZ0087 grub screw can hold onto 6 mm D shaft with accessible 7 mm projection beyond bushing and still move the shaft axially ~0.5 mm. Recess walls must not obstruct pressing or rotating.
6. **No interference with screen antenna, SD slot, LCD ribbon or reset/boot controls.**

## Next concrete design/prototype steps

- Obtain actual dimensions of the user's **MX switches + keycaps** (brand/model and height), or test the exact owned switches against the first printed mounting coupon.
- Obtain manufacturer/board-revision STEP/CAD if offered, or model screen PCB/glass and screw centres from schematic, separately modelling LCD connector/ribbon, expansion module, USB and encoder.
- Create an adjustable 2D parameterized model for 150×105 and 165×110 front covers, then a section view of underside components, cable and screw placements.
- Prototype a test faceplate before full case; **do not print final or purchase enclosure fasteners based solely on 2D sketch**.
- Finish electrical schematic/RESET/harness review and encoder quadrature sampling tests as separate gates.

**Acceptance:** the user chose the exact provisional part models and input functions; **neither outer faceplate dimensions nor physical KZ0087↔Adafruit 377 fit is accepted**. This is research/CAD-preparation only, no generated finished STL.

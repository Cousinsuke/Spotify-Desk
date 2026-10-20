# Faceplate layout reference — Spotify Desk Thing

**Status:** Phase 6, editable envelope study. NOT a final case, 3D-print-ready model, production cut file or validated electrical design. Created from the chosen provisional Waveshare 25948 touchscreen, Adafruit PID 377 push encoder, KZ0087 knob and three existing MX keys.

## Source files

- [Parametric OpenSCAD layout](faceplate_layout_reference.scad) — change `trial` from `1` (roomy) to `0` (compact). Shows separate component-depth envelopes; NOT mechanically functional.
- [Roomier front view SVG](faceplate_roomy.svg) — millimetre-scale vector, 165 × 110 mm panel.
- [Compact front view SVG](faceplate_compact.svg) — millimetre-scale vector, 150 × 105 mm panel.
- [Dimensioned coordinate table](layout_coordinates.csv) — mm measured from front-view top left, positive Y downward.

The ChatGPT deliverable includes an **A3 three-page PDF**, CAD DXF files, SVGs and previews. The GitHub files contain the source-of-truth parametric envelope model; a full enclosure/STEP/STL is not yet designed.

## Manufacturer-grounded dimensions

| Item | Dimensions |
| --- | --- |
| Touch display complete | 106.10 × 67.80 mm |
| Active screen rectangle | 95.54 × 54.36 mm (approx. +5.23 left, +4.35 top) |
| Rear board hole pitch | approx. 98 × 60 mm; **projected reference markers only**, hole bore unspecified |
| Adafruit encoder body XY | 13.2 × 13.2 mm, depth/lead allowance TBD |
| Knob Zone KZ0087 cap | diameter 15.1 mm, height 15.2 mm, **actual visible height TBD** |
| Owned MX keycaps | nominal 18 × 18 mm each, exact model and plate retention TBD |
| AW9523B board | 38 × 23 mm, located on a separate Z plane in drawing |

Primary drawings: [Waveshare screen schematic + mechanical page](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/manual/ESP32-S3-Touch-LCD-4.3-Sch.pdf), [Bourns encoder mechanical](https://cdn-shop.adafruit.com/datasheets/pec11.pdf), [Knob Zone KZ0087](https://knobzone.co.uk/products/kz0087), and [AW9523B board](https://www.waveshare.com/product/modules/others/interface-expansion/aw9523b-io-expansion-board.htm).

## Layout geometry (top-left origin, mm)

| Reference | Compact | Roomier |
| --- | --- | --- |
| Front face | 150 × 105 | 165 × 110 |
| LCD top-left | (8, 7) | (11, 8) |
| K1/K2/K3 centres | (39,86), (69,86), (99,86) | (40,91), (70,91), (100,91) |
| Knob centre | (131,41) | (142,44) |
| LCD outer bottom | 74.8 | 75.8 |
| Gap from LCD outer bottom to keycap top | **2.2** | **6.2** |
| Gap from LCD outer right to knob left edge | **9.35** | **17.35** |

**Important:** Orange side rectangle in SVG/OpenSCAD is an explicitly *invented 14 mm trial cable corridor*, **not an actual Waveshare connector specification**. Compact leaves **-3.7 mm** clearance between that assumed corridor and encoder body; roomier leaves **+4.3 mm**. Neither proves a bendable I²C cable or connector will fit.

## Outstanding physical gates

1. LCD rear hole diameters/standoff bosses, board stack-up, antenna clearance and USB port access.
2. Actual I²C plug exit direction/bend radius at right of display and entire AW9523B connector layout.
3. Exact owned MX switch and cap geometry and usable 3D printed mounting clip/cutout tolerances.
4. KZ0087 set-screw fit on Adafruit 377's approx. 7 mm exposed shaft beyond bushing and push travel.
5. Case interior depth, assembly order, fastener/boss walls and ventilation.
6. AW9523B safe startup/RESET circuitry and 3.3 V wiring remain separately **unapproved**; see [electrical review](../docs/HARDWARE-ELECTRICAL-REVIEW.md).

**Research preference:** roomier 165 × 110 mm for CAD iteration, not a user-approved manufacturing dimension or purchase.

# Rev B — Compact centred-button wedge CAD

**Status: provisional dimensioned CAD study, not fabrication approved.** 2026-10-21. This revises the former **165 x 110 mm** front and its wedge enclosure after the user requested three changes based on both visual renders:

1. Centre the three square MX keys **exactly under the LCD**.
2. Reduce unused width around the knob and right-hand panel.
3. Compare **sharp** and **rounded** external shell corners using identical component dimensions.

## Exterior dimensions — both variants

| Parameter | Rev B | Source/status |
| --- | ---: | --- |
| Faceplate width | **156 mm** | Trial chosen for tighter right-hand space |
| Sloped face length | **110 mm** | Retained from previous layout |
| Sloped face angle from desk | **55°** | Previous concept; not user-final |
| Raised vertical front chin | **16 mm** | Assumed clearance choice |
| Rear horizontal roof | **20 mm** | Assumed clearance choice |
| Desk footprint depth | **83.0934 mm** | `110 cos(55°) + 20` |
| Maximum exterior height | **106.1067 mm** | `16 + 110 sin(55°)` |
| Nominal case wall | **3 mm** | Prototype assumption |
| Rounded edition external fillet | **R5 mm** | Aesthetic design choice |
| Rounded edition display aperture fillet | **R2.5 mm** | Aesthetic design choice |
| Sharp edition | No exterior fillet | Aesthetic design choice |

Both versions use the same nominal rear-shell bottom access opening as a **cutout demonstration without finished hatch fasteners**, not a printable final enclosure.

## Front face coordinates (top-left of angled face, mm)

Axes are **X rightward**, **V down the sloping front plane**, not desk Y:

| Feature | X centre/origin | V centre/origin | Size / definition |
| --- | ---: | ---: | --- |
| LCD complete module top-left | 8.00 | 8.00 | 106.10 W x 67.80 along face |
| Display active rectangle relative to module | +5.23 | +4.35 | 95.54 x 54.36 approx |
| LCD centre | **61.05** | 41.90 | 106.10-wide module |
| MX Previous centre | **31.05** | 91.00 | 18 x 18 cap |
| MX Play/Pause centre | **61.05** | 91.00 | 18 x 18 cap |
| MX Next centre | **91.05** | 91.00 | 18 x 18 cap |
| Rotary encoder knob centre | 138.00 | 44.00 | 15.1 mm outer diameter, KZ0087 |

**Exactly centred:** the arithmetic mean of MX X coordinates is **61.05 mm**, matching the LCD module centre exactly. Each successive key is **30 mm** apart centre-to-centre. The active visible region centre differs by just ~0.05 mm because of bezel asymmetry.

**Narrower case:** the original trial was 165 mm wide. This revision is **156 mm**, 9 mm less, while retaining panel angle and height. The knob's outside edge is at **X = 145.55**, leaving **10.45 mm** to outer right edge. Horizontal gap from *full LCD module right edge X=114.1* to the knob rim *X=130.45* is **16.35 mm**.

Other important frontal gaps: LCD bottom V=75.8 to nearest keycap top V=82 is **6.2 mm**. Right-hand encoder body assumed square 13.2 mm, left X=131.4; under the previously hypothesized **14 mm-wide** LCD I2C connector/cable horizontal band ending X=128.1, remaining lateral gap would be just **3.30 mm**. **That 14 mm band is not manufacturer-specified or electrically verified. Do not claim actual cable clearance.**

## Confirmed versus proposed

**Source-grounded:** Waveshare SKU 25948 LCD complete module 106.1 x 67.8, nominal visible rectangle 95.54 x 54.36, rear fastening pitch about 98 x 60 (but **hole bores unknown**); three user-set 18 x 18 mm keycaps; KZ0087 15.1 mm diameter; Adafruit encoder body approx 13.2 x 13.2 mm and its push-click feature.

**Unverified and parameterized:** 156 x 110 panel and 55° wedge, R5 fillets, 3 mm shell wall, 14 x 14 mm switch mounting cutouts (nominal, untoleranced), ~7.3 mm encoder bushing aperture, LCD visible-window aperture, trial rear module depth 6.8 mm, switch body inward depth 16.8 mm, knob exposed ~8 mm, cable routing, removable bottom hatch and wall fastening. The **rotary push switch must still work through the chosen knob and front panel**.

The demonstration shell STEP and assembly STEP are real editable boundary-representation CAD solids; their walls, apertures, fasteners and joints are not approved by a physical fitting test and should **not be used as final manufacturing geometry**.

## Generated drawings and model formats

The user received a ZIP named **Spotify_Desk_RevB_CAD_Shared_Package.zip** containing:

- **Four-page A3 PDF** `Spotify_Desk_RevB_dimensioned_CAD_comparison.pdf`, including both earlier concept images, true-XY-scale frontal/side dimension sheets for each version and confirmed-versus-assumed matrix. Print on **A3 at 100%** if physical scale is needed.
- **Sharp and rounded DXF** measured front and side orthographic drawings with dimensions/layers.
- **Sharp and rounded STEP case solids** and **STEP multi-part reference assemblies** (screen, three keycaps, knob, switch envelopes, AW9523B board at trial location).
- A **Python generator `build_cad.py`**, based on CadQuery, ezdxf, ReportLab, Shapely and Pillow, with geometry dimensions exported to `dimensions.json`.
- Actual 3D CAD-based PNG previews for each variant and a side-by-side comparison (distinct from image-generation aesthetic references).

Because the GitHub connector can create text assets but not binary CAD files directly, the STEP/DXF/PDF/ZIP are **conversation attachments**; they are **not claimed as GitHub-hosted binary files**. GitHub's current reference remains the original [`mechanical/wedge_packaging_concept.scad`](../mechanical/wedge_packaging_concept.scad) for earlier Rev A, not this new Rev B.

## Next design gates

1. Ask user to compare **sharp vs R5 rounded** actual CAD views and confirm if the 156 mm narrower shell and centred key row look correct.
2. Obtain actual owned MX switch model, keycap height and locking mechanism; build/test a switch coupon. 14 x 14 mm holes are **not a fit guarantee**.
3. Inspect actual Waveshare board hole bores, right-side I2C connector, cable bend and left USB-C access; the 3.3 mm estimated encoder body-to-I2C band is very tight.
4. Finish genuine 3D clearances: screen rear components, standoffs, encoder bushing and push travel, cable strain relief, AW9523B supports and bottom-hatch screw bosses.
5. Validate the separate electrical input-expander boot, 3.3 V and reset concerns before changing from wires to a custom input PCB.
6. **Only after these gates** produce fitted print-ready STL/STEP enclosure and KiCad carrier-board design.

Current accepted software remains Phase 5.2 and was **not changed** by this CAD work.

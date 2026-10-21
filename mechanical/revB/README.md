# Spotify Desk — Rev B dimensioned CAD coordinates

**Concept revision (2026-10-21). Not printable or electrically validated.**

Current physical components and approved interaction are unchanged: Waveshare 25948 capacitive LCD, 3 MX media keys (previous/play-pause/next), Adafruit PID 377 turn-for-volume/push-for-PC-Wi-Fi mode encoder, and KZ0087-01 flat aluminium cap; WAV AW9523B expander is provisional.

The user asked for exactly LCD-centred MX keys, a narrower knob-side case and sharp vs R5-rounded comparisons. **Both CAD alternatives now live in GitHub**. The [`cad/`](cad/) folder contains STEP cases, STEP assemblies, DXF dimension drawings, A3 PDF, PNG previews, `dimensions.json` and the editable [`build_cad.py`](cad/build_cad.py) generator. The [original ZIP](Spotify_Desk_RevB_CAD_Shared_Package.zip) is preserved alongside them. Commit [`6ae257e`](https://github.com/Cousinsuke/Spotify-Desk/commit/6ae257e2ce01256b320417fd21e14d9339bd9ed1), verified byte-for-byte against all 13 ZIP entries. Both are **design references**, not approved printed enclosures.

## Current model dimensions (mm)

| Datum | Value |
|---|---:|
| Faceplate X width | **156.000** |
| Faceplate V length down slope | **110.000** |
| Face tilt from desk | **55 degrees** |
| Front chin | **16.000** |
| Rear roof | **20.000** |
| Footprint depth | **83.093408** |
| Maximum height | **106.106725** |
| Outer edge fillet rounded alternative | **R5** |
| Body reference wall | 3 (ASSUMED; not manufactured) |
| LCD module origin (X,V) | (8,8) |
| LCD module XY size on face | (106.1,67.8) |
| Visible LCD origin | (13.23,12.35) |
| Visible LCD size | (95.54,54.36) |
| Key centres | (31.05,91), **(61.05,91)**, (91.05,91) |
| Key caps | 18x18 nominal, with 30 mm X pitch |
| Knob centre | (138,44) |
| Knob diameter | 15.1 |
| Nominal encoder body behind front | 13.2x13.2, Z unknown |
| Knob rim to outer right side | **10.45** |
| Full display module to knob rim horizontally | **16.35** |
| Display module bottom to keycap top | **6.20** |
| Hypothetical I2C cable clearance corridor | 14.0 (UNVERIFIED) |
| Nominal encoder body to hypothetical I2C corridor | **3.30** (NOT a verified fit) |

**Coordinate system:** front X increases from left to right; front V increases down the **sloping front face**, not vertically. Deskside Y and Z refer to depth and absolute vertical height. Upper/rear end of sloping face is at local Y = 110 cos 55° = **63.093408** and Z = **106.106725**. Lower/front end at desk Y=0, Z=16. Rectangular side section is extended by a 20 mm horizontal roof behind the upper end to a desk Y=83.093408.

**Models:** Sharp STEP is crisp outer case. Rounded STEP is a separate valid solid with nominal R5 exterior fillets (not simply a rounded JPEG). Both contain **conceptual** front LCD/keyboard/encoder cutouts and a bottom service opening but no verified screw hardware, LCD mounting standoffs, port openings, cable paths or official switch tolerances. The multi-part STEP contains schematic component envelopes as separate editable bodies and may include intended contacts/overlaps pending design of supports and real thicknesses.

**Important:** the previous [mechanical/wedge_packaging_concept.scad](../wedge_packaging_concept.scad) is **Rev A**, with 165 mm width and non-centred key row. It has NOT been silently overwritten. Use Rev B coordinates from [the CSV](layout_revB.csv), [the checked-in CAD files](cad/) and [the dimensioned design note](../../docs/HARDWARE-WEDGE-REV-B-CAD.md) for future editing.

## Checks before manufacturing

1. Confirm exact MX switch model and actual depths/mount clips.
2. Check LCD module rear hole bores and right-side I2C/connector/cable requirements. The 14 mm band was invented for a clearance study.
3. Verify KZ0087 real exposure and ability to press Adafruit 377 through front wall, and assembly order.
4. Confirm 3.3 V electrical protection and AW9523B reset/gpio behaviour; no approved circuit layout yet.
5. Iterate latch/screw bosses, bottom hatch, USB power opening and real tool tolerances, and perform true 3D collision checks.

**Source:** [mechanical study](../../docs/HARDWARE-MECHANICAL-LAYOUT-STUDY.md), [wedge case proposal](../../docs/HARDWARE-WEDGE-CASE-PROPOSAL.md), [new Rev B detailed CAD report](../../docs/HARDWARE-WEDGE-REV-B-CAD.md).

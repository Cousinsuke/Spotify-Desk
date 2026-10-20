# Phase 6 — Angled wedge enclosure + internal packaging proposal

**Date:** 2026-10-20. **Status:** 3D packaging **concept**, not accepted final case, engineering-certified depth, printable STL, purchased hardware, or PCB fabrication. User supplied a reference photograph of a freestanding sloped/triangular wedge desk housing to guide overall form. Reference was about **shape and viewing/press angle**, not a wood material requirement.

**Retained accepted controls:** Waveshare touchscreen 25948 (provisional), 3 existing MX media switches beneath display, Adafruit PID 377 rotary with **push = PC/Wi-Fi mode**, provisional flat KZ0087 knob. Proposed AW9523B 22132 input expander. Existing 165×110 mm *faceplate layout* is reused, not user-approved as production size.

## Recommended first shape: raised-front wedge with shallow rear roof

A pure sharp triangle runs out of depth at the bottom where MX switches need their bodies and solder tails, and at the apex behind the top edge of the display. Solve both with a **raised 16 mm front chin** and **20 mm hidden rear roof/shelf**. Use a true sloping main face (not a hinged display); add rounded external corners later, when fasteners and supports are engineered.

| Dimension | Trial value | Derivation / status |
| --- | ---: | --- |
| Width | **165 mm** | Existing roomier faceplate, tentative |
| Sloped face length | **110 mm** | Existing faceplate measured *along* slope |
| Angle from horizontal desktop | **55°** | Concept choice, **35° recline from vertical**, not measured from photo |
| Front vertical chin | **16 mm** | Added for MX switch clearance, entirely assumed |
| Top flat rearward roof | **20 mm** | Added behind upper LCD, entirely assumed |
| Total desktop footprint depth | **83.1 mm** | \`110 cos(55°)+20 = 83.09\` |
| Maximum case height | **106.1 mm** | \`16+110 sin(55°) = 106.11\` |
| First model shell walls | **3 mm** | **Unapproved** visual/model assumption |
| KZ0087 visible knob protrusion | **~8 mm** | Desired low-profile look, **not an installed/verified fit** |
| Service access | **Removable bottom hatch** | Hatch lips/bosses, fasteners, feet undecided |

**Alternative angle envelopes** if face/chin/roof remain unchanged:

| Front angle above desk | Approx. footprint depth | Approx. height |
| --- | ---: | ---: |
| 50° (more reclined) | 90.7 mm | 100.3 mm |
| **55° — leading starting point** | **83.1 mm** | **106.1 mm** |
| 60° (more upright) | 75.0 mm | 111.3 mm |

This case depth is **larger than the earlier 55–75 mm rough guess**: the extra ~20 mm rear shelf is a deliberate engineering packaging allowance behind the display. Do not mistake front sloping 110 mm for vertical height.

## Face positions carried directly from the existing design

Local front-plane coordinates measured from the top-left of the **sloping front face**, with +v down the face:

- Full Waveshare 25948 module **106.1×67.8 mm**, starting \`(x=11, v=8)\`; visible panel **95.54×54.36 mm**, inner offset ~\`(+5.23,+4.35)\`. Fixing pitch approximately 98×60 mm, **hole bores/standoffs unverified**.
- Approximate **18×18 mm MX keycaps**, centres \`(40,91)\`, \`(70,91)\`, \`(100,91)\`. Exact switch brand/mounts missing.
- **KZ0087 Ø15.1 mm** knob centre \`(142,44)\`, Adafruit 377 encoder body 13.2×13.2 mm nominal X/Y below it.
- WAV AW9523B **38×23 mm** experimental position horizontal just above the *removable base*, model global x=24–62, depth y=43–66, z≈10 mm. **Component Z and harness clearances not confirmed**.
- **Right-side I2C connector** next to encoder remains a bottleneck. Previously drawn **14 mm clearance corridor is an unmeasured design assumption**, not a real plug/cable bending specification.

## Three-dimensional assembly idea

**Front/upper shell:** one wedge-shaped housing with face opening, proper LCD seats/standoffs, MX clips or plate, encoder bush/push clearance, and rounded external transitions only after CAD fit checks. The current reference SCAD **has no certified component cutouts**.

**Base:** separate bottom hatch removable for repair/programming and resistors. In final design use defined bosses/heat-set inserts/captive nuts, secure PCB supports, insulated wiring, and non-slip feet; none are dimensioned or tested yet.

**Interfaces:** retain left screen USB-C flashing/power service access, allow right I2C cable/strain relief, keep antenna/microSD and reset/boot usable. USB power exits rear or left via suitable protected aperture or extension only after actual port locations measured. No battery/charger required for first USB-powered bench device.

**Inside:** LCD attached to sloped face, MX housings retained under lower portion of sloped face, encoder body under right knob. I2C expander on an accessible, insulated mount near floor. Short, labelled wires from six protected switch inputs to AW9523B, with the **four-wire 3.3V/GND/SDA/SCL link** to screen. Final electrical connectors/RESET/startup protectors are *still unapproved*; see [HARDWARE-ELECTRICAL-REVIEW.md](HARDWARE-ELECTRICAL-REVIEW.md).

**Why a raised chin matters:** if the front face ends directly on the desk, the keycaps near face coordinate v=91 leave little room for their housings behind the face before the case floor. With a 16mm raised toe, at the centre of those keys the outside face is ~31.6mm above the desktop. An illustrative 20mm inward-normal housing length leaves ~17mm above an assumed 3mm floor at the key centre; the lowest keycap edge at v≈100 leaves ~9.7mm after the same normal depth. **These are planar envelope calculations, NOT switch mechanical clearance certification**. No latching or solder tail shape has been verified.

## Custom PCB versus wires: staged design

**Do not replace the Waveshare motherboard.** It already contains the ESP32-S3, display support, RAM and USB. A custom *input carrier board* will eventually be valuable:
- One possible **L-shaped carrier** behind the lower 3 MX switches and right encoder could route all 6 digital contacts on copper and incorporate AW9523B + bias/current-limit resistors and 4-wire I2C header. A short screen cable remains necessary.
- It may be mechanically easier to have a narrow **3-key PCB** and a separate **encoder mini-PCB**, then a small expander section/carrier: different mounting depths and right-side cable corridor can prevent one flat PCB.
- **First build with prototyping harness and external expander**, validate I2C 3.3V/reset, encoder fast rotation with display/Wi-Fi, and physical positions; **then** design a custom carrier in KiCad after the layout is measured and approved.
- No real routed PCB or manufacturing Gerbers; no guarantee of fewer total parts or smaller size until body clearance and connector choice are validated.

## Deliverables produced

- **Editable 3D parametric envelope** \`mechanical/wedge_packaging_concept.scad\` (parameter \`tilt_deg\`, \`front_chin\`, \`rear_roof\`, \`mode\`).
- Companion ZIP made in chat with OpenSCAD source, exterior/cutaway/ghost PNG previews, annotated side section and SVG, angle comparison image, possible carrier PCB zone image/SVG, and illustration source scripts.
- **Static checks only:** OpenSCAD rendered successfully in exterior, ghost, cutaway modes; formula-derived dimensions checked; generated ZIP integrity-tested. No fit/assembly test, CAM manufacturing model or production CAD.

## Remaining clearance and electrical gates before buying/printing

1. Identify the exact three MX switch models, type of mount, keycap heights and mounting plate geometry; make a **small switch test coupon**.
2. Confirm actual screen board revision, 98×60 pitch mounting bores, connectors, USB left access, antenna keepout and **right I2C plug/cable bend**.
3. Confirm KZ0087 grip onto encoder's **~7mm shaft beyond bushing** and push-travel clearance under faceplate (visible cap height is not the catalogue's full 15.2mm).
4. Confirm AW9523B assembled module RESET bias, GPIO output-at-boot protection, 3.3V level, I2C connector pin 1, and encoder pulse tracking under UI load.
5. Compare the 50/55/60-degree silhouettes **with the user**; do not label 55° or 165×83×106mm as accepted final exterior until they approve.
6. After physical measurements, create *real* 3D assembly / cutouts / mounts, print iterative case, then consider a custom input PCB and final BOM.

**Preferred next task:** user reviews exterior 3D style and 55° profile; acquire actual switch dimensions and I2C/USB cable directions to evolve envelope into printable, screw-attached, serviceable case.

Primary manufacturer dimension sources already recorded in [HARDWARE-MECHANICAL-LAYOUT-STUDY.md](HARDWARE-MECHANICAL-LAYOUT-STUDY.md) and [HARDWARE-PRE-PURCHASE-CHECK.md](HARDWARE-PRE-PURCHASE-CHECK.md). No new external part specs are implied by this geometry exercise.

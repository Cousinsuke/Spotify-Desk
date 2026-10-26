# Spotify Desk — Rev B dimensioned CAD coordinates

**Concept revision (2026-10-21). Not printable or electrically validated.**

Current physical components and approved interaction are unchanged: Waveshare 25948 capacitive LCD, 3 MX media keys (previous/play-pause/next), Adafruit PID 377 turn-for-volume/push-for-PC-Wi-Fi mode encoder, and KZ0087-01 flat aluminium cap; WAV AW9523B expander is provisional.

The user asked for exactly LCD-centred MX keys, a narrower knob-side case and sharp vs R5-rounded comparisons. **Both CAD alternatives now live in GitHub**. The [`cad/`](cad/) folder contains STEP cases, STEP assemblies, DXF dimension drawings, A3 PDF, PNG previews, `dimensions.json` and the editable [`build_cad.py`](cad/build_cad.py) generator. The [original ZIP](Spotify_Desk_RevB_CAD_Shared_Package.zip) is preserved alongside them. Commit [`6ae257e`](https://github.com/Cousinsuke/Spotify-Desk/commit/6ae257e2ce01256b320417fd21e14d9339bd9ed1), verified byte-for-byte against all 13 ZIP entries. Both are **design references**, not approved printed enclosures.

**Manufacturer-model orientation update:** The official STEP was uploaded and parsed on 2026-10-21. Looking at the display from the **front**, USB Type-C1/Type-C2 are on the **right** (toward knob), and I2C H7 plus other peripheral sockets on **left**. Prior `right I2C 14mm gap` in the coordinate table and the earlier fit-audit were **hypothetical rear-view-mirrored studies, not accurate USB/I2C case routing**. Source-dimension overlay and checks: [Waveshare STEP inspection](../../docs/HARDWARE-WAVESHARE-STEP-INSPECTION.md) and [`cad/waveshare_step_front_overlay.svg`](cad/waveshare_step_front_overlay.svg). Original case shape untouched.

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
| Old rear-view-mirrored hypothetical I2C corridor | 14.0 mm (OBSOLETE as front connector location; scenario only) |
| Old theoretical encoder-to-right-I2C margin | **3.30 mm** (HISTORICAL/HYPOTHETICAL; actual right-side connector is USB) |

**Coordinate system:** front X increases from left to right; front V increases down the **sloping front face**, not vertically. Deskside Y and Z refer to depth and absolute vertical height. Upper/rear end of sloping face is at local Y = 110 cos 55° = **63.093408** and Z = **106.106725**. Lower/front end at desk Y=0, Z=16. Rectangular side section is extended by a 20 mm horizontal roof behind the upper end to a desk Y=83.093408.

**Models:** Sharp STEP is crisp outer case. Rounded STEP is a separate valid solid with nominal R5 exterior fillets (not simply a rounded JPEG). Both contain **conceptual** front LCD/keyboard/encoder cutouts and a bottom service opening but no verified screw hardware, LCD mounting standoffs, port openings, cable paths or official switch tolerances. The multi-part STEP contains schematic component envelopes as separate editable bodies and may include intended contacts/overlaps pending design of supports and real thicknesses.

**Important:** the previous [mechanical/wedge_packaging_concept.scad](../wedge_packaging_concept.scad) is **Rev A**, with 165 mm width and non-centred key row. It has NOT been silently overwritten. Use Rev B coordinates from [the CSV](layout_revB.csv), [the checked-in CAD files](cad/) and [the dimensioned design note](../../docs/HARDWARE-WEDGE-REV-B-CAD.md) for future editing.

## Rev B fit study tools (2026-10-21)

- [Read the physical fit audit, scenarios, references and measurement gate](../../docs/HARDWARE-REV-B-FIT-REVIEW.md).
- [`cad/fit_audit.py`](cad/fit_audit.py) evaluates a range of **assumed** I2C cable-extension scenarios and can export an SVG front projection; it does not test actual 3D clashes.
- [`cad/fit_coupons.scad`](cad/fit_coupons.scad) is the parametric OpenSCAD source for small test-print MX and encoder mounting plates, preserving the original 156mm enclosure models.
- [`cad/test_fit_audit.py`](cad/test_fit_audit.py) covers the dimensions arithmetic. Initial 5 tests passed and an STL sample was rendered in OpenSCAD **without physically printing or testing it**.

## Independent 3D internal packaging reference

- [3D packaging study and Windows instructions](../../docs/HARDWARE-REV-B-INTERNAL-PACKAGING.md).
- `cad/internal_packaging.py`: Python-only parameterised X/V/inward-W 3D box overlap and nominal case-inner-boundary calculations; optional OpenSCAD and JSON export.
- `cad/internal_packaging_view.scad` and `cad/internal_packaging_params.scad`: conceptual shell/part/cable view in OpenSCAD. For scenario variants, run Python `--out-dir` and inspect generated files.
- `cad/internal_packaging_assumptions.json`: explicitly unmeasured component envelopes. `cad/test_internal_packaging.py`: eight tests passed assistant-side **and on user's Windows 11 machine**; actual component fit and user OpenSCAD review remain unverified.
- **No changes to original sharp/R5 B-Rep CAD, part fit or manufacturing status.**

## Official Waveshare 3D drawing — pending archive verification

[Waveshare's hardware resources](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Resources-And-Documents) link an original ESP32-S3-Touch-LCD-4.3 3D Drawing ZIP. Its contents, units, 25948 touch SKU compatibility, USB/I2C socket detail and reuse permissions have not been verified. Run [`scripts/inspect-waveshare-3d-reference.ps1`](../../scripts/inspect-waveshare-3d-reference.ps1) on Windows to download/list the archive into Downloads before relying on any manufacturer geometry.

**Official ZIP download checkpoint:** Windows download/extraction verified by user, 2026-10-21. Sole file is `esp32-s3-touch-lcd-4_3.stp` (31,338,066 bytes), ZIP SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`. **Geometry not inspected; no modification to Rev B case yet.** Await source ZIP upload to chat to inspect board geometry in an isolated reference study.

## Manufacturer STEP reference (2026-10-21)

- [Official STEP part measurements, orientation correction, trial fit results and Windows commands](../../docs/HARDWARE-WAVESHARE-STEP-INSPECTION.md).
- [`cad/waveshare_step_reference.json`](cad/waveshare_step_reference.json) records manufacturer model SHA, part bounding boxes, glass-facing coordinate signs, USB/H7 and 98×60 standoffs. Raw Waveshare STEP/ZIP intentionally remains out of public GitHub.
- [`cad/manufacturer_fit_compare.py`](cad/manufacturer_fit_compare.py) calculates trial mating-cable extension overlap and outputs a vector layout; [`cad/waveshare_step_front_overlay.svg`](cad/waveshare_step_front_overlay.svg) is the checked-in front-view reference. Ten assistant-side tests passed in [`cad/test_manufacturer_fit_compare.py`](cad/test_manufacturer_fit_compare.py); Windows user acceptance pending.
- **16.906mm** complete STEP depth includes rear PCB, supports and sockets; it is not a per-component or mounted-case allowance. No real plugs modelled and no final port cutouts/bosses.

## Alternative physical 180° touchscreen orientation (under evaluation)

- [Original vs flipped-in-plane comparison and installation tradeoffs](../../docs/HARDWARE-WAVESHARE-ROTATION-180-STUDY.md) uses `cad/orientation_180_study.py` and `cad/test_orientation_180_study.py`; 12 assistant-side tests passed, Windows test pending.
- Physical 180° rotation (glass stays facing user) makes **USB-C on LEFT** and **I2C on RIGHT**. Nominal screen aperture must move **+4.74mm down V** (and 0.10mm right X), without moving the three key centres, original face size, or 98×60 mounting hole pitch.
- A **left USB-C power access slot/tunnel** must be modelled, as its mating plug is not included in manufacturer STEP; right-side I2C cabling and encoder body may still interfere under longer cable assumptions. Firmware LVGL display and GT911 touch rotation untested. Existing sharp/R5 STEP source remains unchanged until user chooses preferred layout.

## Separate 180° experimental CAD case shells (new design alternative)

- The Windows user ran the **12 original-vs-180° study tests successfully**. The [new rotated-180 shell prototype report](../../docs/HARDWARE-REV-B-ROTATED180-CASE-PROTOTYPE.md) explains the two **experimental B-rep STEP shell versions** (sharp/R5) with a **LEFT USB-C1 wall opening** and visibly shifted screen cutout (X+0.10, V+4.74), retaining 156mm width and centred keys.
- Source checked in: [`cad/rotated_case_prototype.py`](cad/rotated_case_prototype.py), [assumptions JSON](cad/rotated_case_parameters.json), and [ten geometry tests](cad/test_rotated_case_prototype.py). Assistant-side 10/10 pass; **Windows user checks 8 passed, 2 skipped** (optional CAD dependencies missing), with report-only overview generated. **Pre-generated experimental STEP assemblies/shells live only in delivered chat ZIP**, original Rev B STEP/DXF/PDF and source ZIP are unchanged.
- Experimental W=3.25mm glass datum and USB-C1 wall slot (X=-2..9.244, V=36.073..49.655, W=8.889..17.051mm) are **not verified plug, mounting or manufacturing dimensions**. Neither optional UART service nor LCD bosses/hatch/actual connector is engineered.

## Rounded USB-left media keycaps and recessed switch mounting (experimental)

- User visually selected rounded R5 corners and left-side USB as design direction; not print signoff. [Three media cap designs, full-press clearance and supplier shortlist](../../docs/HARDWARE-REV-B-MEDIA-CONTROLS-FIT.md).
- `cad/media_controls_fit_study.py` and `cad/keycap_mount_assumptions.json`: trial 18mm 1U keycaps with white icon masters, 19.2mm wells and 0.6mm nominal lateral clearance each side. The MX switch clips to an integral **1.5mm local plate at W=11.5mm behind face**, with nominal 14mm mounting cutout, rather than the 3mm case front wall. Cap sits 2mm above surface at rest, assumed 4mm travel, 8mm cap depth. This is not a real fit verified by physical parts.
- `cad/test_media_controls_fit_study.py`: **15 assistant-side checks pass**, including actual CadQuery R5 shell validity and STEP roundtrip. Windows and actual cap fit pending; optional CAD tests skip without CadQuery. White standalone SVG icon drafts in `../revB/keycaps/`. Separate ZIP delivered contains new STEP shell, complete cap/knob reference assembly, drawings and vector icons. Earlier CAD files are preserved.

## Separate actual CAD models for 2mm, 4mm, 6mm media-keycap heights

- [Three-height rounded CAD comparison, Windows instructions, status and mechanical assumptions](../../docs/HARDWARE-REV-B-KEYCAP-HEIGHT-CAD-COMPARISON.md).
- Generator `cad/media_controls_height_variants.py`, config `cad/keycap_height_variant_parameters.json`, tests `cad/test_media_controls_height_variants.py`; saved comparison SVGs `cad/media_controls_2_4_6_front_comparison.svg` and `cad/media_controls_2_4_6_section_comparison.svg`. **20/20 assistant-side tests PASS** including CadQuery single-solids + multibody STEP assembly checks; user Windows test pending.
- Actual experimental STEP files supplied in a **separate chat ZIP** for FreeCAD: each of 2/4/6mm has single-solid R5 shell and cap/switch/knob envelope assembly. All retain rounded 156mm USB-left 180° Waveshare layout and 3 MX key centres. To keep assumed stem engagement and full-stroke 1.5mm plate guard constant, MX retaining plates change **11.5/9.5/7.5mm inward**. Profiles, safety margin, snap clips, male USB and print tolerances remain hypothetical; no purchase or print approval.

## Experiment: Removable underside cover and screen brackets (4mm, R5)

- [Engineering note and known insertion/access risks](../../docs/HARDWARE-REV-B-REAR-COVER-AND-SCREEN-MOUNTS.md). New CAD supplied as separate chat ZIP, **not** a replacement for existing Rev B source files.
- Case support lip and four physical cover-screw bosses added; separate inset 2mm service lid, 0.4mm nominal all-edge clearance, four M2.5 candidate clearance holes and *untested* 2mm pilot bosses. Four cantilevered screen alignment brackets match 98x60mm 2023 Waveshare STEP standoff centres. **16 assistant-side tests pass** and lid has zero computed intersection with case. Screen installation through ~59mm underside hatch and cable/tool reach **unresolved**; not fabrication ready.
- **Source publishing status:** [`cad/rear_cover_screen_mount_study.py`](cad/rear_cover_screen_mount_study.py), [settings](cad/rear_cover_screen_mount_study.json), [16-case regression suite](cad/test_rear_cover_screen_mount_study.py) and the two SVGs are now natively tracked. User can `git pull` and use `--report-only` without CadQuery; two to four optional B-Rep tests skip when optional CadQuery/Shapely are absent. Full STEP case/cover/assembly files remain in the separate chat ZIP.

## Screwless sliding underside cover (next experimental alternative, 2026-10-26)

- Following user preference, the bottom lid is now a **screwless slide-in cover**, not the older four-screw lift-out hatch. The Waveshare screen retains **four nominal M2.5 screw locations**, based on 98×60mm manufacturer centres. See [CAD study and cautions](../../docs/HARDWARE-REV-B-SCREWLESS-SLIDING-COVER.md).
- Source `cad/slide_in_rear_cover_study.py`, spec `cad/slide_in_rear_cover_study.json`, tests `cad/test_slide_in_rear_cover_study.py`; plans `cad/slide_cover_underside_plan.svg`, `cad/slide_cover_rail_section.svg`. Two side captured guide tracks, opening through the rear underside wall and small rear thumb tab permit Y-axis insertion; 0.4mm nominal side gap, 2mm cover thickness. No lid screws or lid screw bosses.
- **21 assistant-side tests passed** including four CAD-specific cases and 10 sampled zero-overlap slide positions; downloadable STEP assemblies in a separate conversation ZIP. **WARNING:** no positive detent has yet been verified, so lid can potentially slide out unintentionally. Print-test catch/tolerance, rear-wall strength and screen insertion/access before accepting.

## Screwless underside closure options review (2026-10-26)

The [bottom-cover mechanisms comparison](../../docs/HARDWARE-REV-B-BOTTOM-COVER-ALTERNATIVES.md) compares six choices. Current rail lid has no positive latch. **Recommended concept only:** two rigid front hooks and one accessible rear click latch, which would avoid cutting a rear-wall slide-through slot. Alternative: keep rails and add positive detent, or use tabs/magnets. User mechanism decision pending; no case geometry changed, no measured material-fit acceptance or guarantee that the Waveshare display fits through the bottom access hole.

## User-selected hook-and-click underside cover CAD alternative (2026-10-26)

- [Full mechanical study, STEP assets and no-false-fit warnings](../../docs/HARDWARE-REV-B-HOOK-CLICK-COVER.md). Two front 10mm locating tongues engage shallow slots; one rear integral 26×2.2mm horizontal flexure operates a ~7mm local keeper pocket, replacing long slide-in feed slot. No bottom cover screws; **four nominal M2.5 LCD screw target locations kept** at 98×60mm.
- Files: cad/hook_click_cover_study.py, cad/hook_click_cover_parameters.json, cad/test_hook_click_cover_study.py, cad/hook_click_underside_plan.svg and cad/hook_click_operation.svg. **29 assistant tests pass (9 CadQuery/STEP)**; Windows user checks pending. Pre-generated STEP pair and assembly files delivered in chat ZIP. Earlier screwed and sliding covers remain unchanged.
- **Physical latch elasticity, repeated service, printer tolerances, module installation path and exact screw access not proven.**

## Hook-and-click refined V2 testable latch (2026-10-26)

- [V2 guide and physical coupon procedure](../../docs/HARDWARE-REV-B-HOOK-CLICK-LATCH-V2.md). New source files `cad/hook_click_latch_refinement_v2.py`, `cad/hook_click_latch_refinement_v2.json`, `cad/test_hook_click_latch_refinement_v2.py` and `cad/hook_click_latch_v2_design.svg`. Reuses existing hook-click generator as dependency without modifying it.
- Rounded R0.68 spring-beam root, top cam retreat 1.50mm, lower square retention shoulder and reachable underside pad. Original 26×2.2mm nominal beam/1.6mm trial release and case unchanged; case boolean difference 0mm³. **26 local checks pass incl. 10 optional STEP/B-Rep**, Windows unrun.
- The downloadable chat ZIP contains separate full-size lid and case STEP (the latter matches V1), installed/exploded assemblies, **two STL small coupon parts cropped from the actual keeper and actual latch**, and documentation. No cover screws; LCD mounting screws retained. Real spring click force/durability/filament/print tolerance/installation path unproven.


## Waveshare board installation screening (2026-10-26)

- [Independent screen insertion projection, 27 pose checks and screwdriver access report](../../docs/HARDWARE-REV-B-WAVESHARE-SCREEN-INSTALLATION-PATH.md) with `cad/screen_install_path_study.py`, `cad/screen_install_study_parameters.json`, `cad/test_screen_install_path_study.py` and `cad/waveshare_{underside_projection,installation_side_section}.svg`.
- User V2 latch Python suite: **16 passed / 10 optional CAD skips** on Windows. New installation screening: **20 assistant-side tests PASS** including 5 actual pre-existing case STEP collision checks; Windows user tests not yet run. Nominal full board bounding prism projects **53.01mm desk Y** inside 59.09mm Y underside hole, but its seated alignment overhangs rear opening ~4.04mm. 27 sampled rigid pose checks have clashes, 4mm trial shaft collides near two bracket axes. Actual 693-solid board **not** moved/collision-tested. No insertion path certified and no shell edits.
- Chat ZIP contains unchanged current case with simplified board/glass *envelopes* at seated and staged positions, plus report/drawings, no manufacturer raw STEP. Four screwed LCD support target positions and zero bottom-lid screws remain intact. Real screw head direction and tool length, component physical revision and mating cables still unknown.



## Checks before manufacturing

1. Confirm exact MX switch model and actual depths/mount clips.
2. Check LCD module mount bore/thread details and **front-left H7 I2C connector** plus **front-right USB-C1/USB-C2** mating plugs/cable paths; ZIP-derived socket positions alone don't establish cable clearance.
3. Verify KZ0087 real exposure and ability to press Adafruit 377 through front wall, and assembly order.
4. Confirm 3.3 V electrical protection and AW9523B reset/gpio behaviour; no approved circuit layout yet.
5. Iterate latch/screw bosses, bottom hatch, USB power opening and real tool tolerances, and perform true 3D collision checks.

**Source:** [mechanical study](../../docs/HARDWARE-MECHANICAL-LAYOUT-STUDY.md), [wedge case proposal](../../docs/HARDWARE-WEDGE-CASE-PROPOSAL.md), [new Rev B detailed CAD report](../../docs/HARDWARE-WEDGE-REV-B-CAD.md).

# Rev B — separate experimental 180° touchscreen case prototype

**2026-10-21. Status: source-generated B-rep STEP design alternatives, NOT verified physical fit, print approved or user-accepted final orientation.** These files preserve the original 156 mm sharp and R5-rounded Rev B source STEP files, generator, CAD package ZIP, original-window location and previous scripts. Nothing has been overwritten. The user suggested physically rotating the entire touchscreen module 180 degrees to move the USB power port from the right (near encoder) to the left, then compensating LCD pixels and touch input in firmware. This study illustrates that alternative; choosing it is still pending.

## Implemented in this **separate** case study

- **Exterior:** the same 156 mm wide, 110 mm long sloped front, 55° inclination, 16 mm front chin, 20 mm rear roof and nominal 3 mm wall. Keeps both original-design **sharp** and **R5 rounded** aesthetic variants and nominal three MX switch openings, centred key positions and knob mounting aperture. These are *experimental derived models*, not replacements for source Rev B STEP.
- **Physical board orientation:** entire Waveshare module rotates 180° around the *front plane* centre, leaving glass facing the user. From the glass-front viewing position, **USB-C1 main port is LEFT**, auxiliary USB-to-UART C2 is also LEFT, and **four-pin I2C H7 is RIGHT**. Positions derived from extracted bounding boxes of the manufacturer's user-uploaded 2023 STEP (not raw STEP redistributions).
- **Visible screen opening:** centre placement adjusted for asymmetric bezel: nominal top-left **(X,V)=(13.33,17.09) mm**, shifted +0.10 mm right and **+4.74 mm down** from original. Nominal visible aperture 95.54 × 54.36 mm with **zero** manufacturing clearance (placeholder; tolerances not signed off). Nearest keycap top remains **10.55 mm** below the nominal visible-window bottom. The 106.1 × 67.8 mm complete glass placement and centred three keys remain unchanged.
- **USB-C1 LEFT side-wall passage:** trial geometry cuts a port through the *left sidewall*, **not through the front panel**. The bounding cut is in local front-face coordinates X=**−2.000..9.244**, V=**36.073..49.655**, W=**8.889..17.051** mm *at the chosen mounting datum*. It includes **2 mm added V and W clearance** around the manufacturer bare USB-C1 housing and reaches 1 mm past the housing's nearest X edge. **This is not a male USB-C plug/cable cutout or a validated minimum clearance.** External plugged cable can leave left side without being forced past encoder in this conceptual arrangement; physical clearance remains unverified.
- **Assumed screen mounting datum:** top of glass is provisionally **W=3.25 mm** inward from front exterior in local case coordinates (0.25 mm behind a nominal 3mm panel), making the farthest source STEP feature approximately W=**20.153 mm** inward. No actual standoff-bearing ledge, screws, touch access margin or clip mechanisms are designed.
- **Existing conceptual apertures:** nominal square 14mm MX through-cutouts, 7.3mm encoder bushing through-cutout, bottom-service opening **without fastener/lid**. These are placeholders and not print-toleranced. No extra cut is included for USB-UART C2. No genuine USB-C socket/grub-screw/standoff collision model is included in these generated new assemblies; only rectangular source-bound boxes are present.

## Outputs and implementation

- `mechanical/revB/cad/rotated_case_prototype.py` — Python/CadQuery source generator. Always outputs to an explicitly supplied **separate output folder**; never writes or changes the source ZIP or the existing `spotify_desk_sharp_case_reference.step` or rounded counterpart.
- `mechanical/revB/cad/rotated_case_parameters.json` — assumptions controlling left USB wall cut, angle-independent mounting datum, nominal aperture and existing rear access.
- `mechanical/revB/cad/test_rotated_case_prototype.py` — 10 unit checks: physical 180° geometry, aperture offsets, socket sides, left slot location, retained footprint/key centres, B-rep validity and actual volume removed by USB wall slot in both variants. **10/10 passed assistant-side** with CadQuery/Shapely. **User Windows validation (2026-10-21): 10 discovered, 8 passed and 2 skipped** because optional CadQuery/Shapely were unavailable. Skipped: `test_sharp_and_rounded_are_valid_brep_solids` and `test_left_usb_cut_removes_wall_material_both_variants`. These are not Windows-validated solid tests; assistant-side B-Rep validation passed independently.
- `spotify_desk_rotated180_sharp_experimental.step` and `spotify_desk_rotated180_rounded_experimental.step` — new editable solids (both opened and checked valid, 156 × 83.09 × 106.11 mm outer bounding boxes). Also two **experimental multi-solid STEP envelope assemblies** (shell + simple LCD bounding box + USB-C1/USB-UART/I2C socket bounding prisms) and a diagnostic front-view SVG/PNG. **The new experimental case STEP binaries are available in the separately delivered ZIP attachment**, not necessarily in the GitHub repository; source and parameters are in GitHub.
- Not a separate module manufacturer STEP: original third-party source ZIP remains outside GitHub.

### Windows — review without installing CAD packages

After pulling GitHub changes from the project root:

```powershell
python -m unittest discover -s mechanical\revB\cad -p test_rotated_case_prototype.py -v
python mechanical\revB\cad\rotated_case_prototype.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Rotated180-Prototype"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Rotated180-Prototype\rotated_case_front_overview.svg"
```

**Optional full CAD generation** (requires `cadquery` and `shapely` in a compatible local Python environment; it can be more difficult to install on Windows):

```powershell
python mechanical\revB\cad\rotated_case_prototype.py --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Rotated180-Prototype"
```

Alternatively use the pre-generated STEP ZIP delivered with this chat and open in FreeCAD or another STEP viewer; it does **not** need CadQuery on the user's Windows PC.

## User Windows design-tool validation (2026-10-21)

The user fast-forwarded to commit `f186eac`, ran the rotated-case unit suite (**8 PASS, 2 SKIP**) and successfully generated the report-only SVG. It returned a 156mm body, visible aperture X=13.33, V=17.09, size 95.54×54.36mm; assumed left USB-C1 wall slot X=-2…9.244, V=36.073…49.655 and W=8.889…17.051mm. The SVG was opened using `Invoke-Item` without a reported error. These checks establish Windows script execution and parameter consistency, **not** user inspection of both STEP solids, actual cable fit or fabrication approval.

The next step is to inspect the **already-generated** rotated sharp/R5 STEP shells and reference assemblies in FreeCAD or another STEP viewer. Installing CadQuery is **optional**, not needed simply to view the supplied ZIP. Do not misreport skipped Windows B-Rep checks as passing.

## Later visual choice and separate recessed button investigation (2026-10-21)

The user **viewed the R5 rounded variant** and confirmed rounded corners and USB on LEFT are their desired visual direction; this does **not** validate the port, model geometry or printability. Three visible keycaps with previous/play-pause/next symbols and a 15.1mm knob were requested before proceeding. A **separate experimental recessed-keycap R5 STEP model and cross-section** has now been produced as [media controls fit study](HARDWARE-REV-B-MEDIA-CONTROLS-FIT.md). The old experimental STEP models are retained. User has not yet approved specific keycaps/switches, recess machining or full press/return fit.

## Remaining gates before a prototype print

1. Confirm user's preferred physical orientation and sharp versus rounded exterior. **This step is a review study only, not implicit acceptance of 180°.**
2. Acquire exact 3D geometry or measurements of the **USB-C1 *male plug and cable* including cable-strain relief, actual insert direction, support/clearance around its socket and wall thickness**. Verify that side slot plus proper insertion/removal finger clearance fits without interference with PCB or mounting boss.
3. Check I2C H7 4P plug and cable path near encoder, rotary body/terminals/bushing and knob press motion. Preserve debugger access to USB-UART C2 or deliberately choose alternate programming workflow.
4. Integrate real 98×60mm mounting supports/fasteners, glass recess or flush mount, LCD touch exposure, Wi-Fi antenna keepout and meaningful access to boot/reset/SD card. Note that the 2023 STEP model may differ from an actual purchased touch SKU 25948 revision.
5. Replace arbitrary MX 14mm square openings with switch-specific clip-bearing local 1.5mm plate supports, check push-encoder panel nut and service hatch screw structure, set print-specific clearances/material wall strength.
6. Later implement/bench-test a 180° 800×480 framebuffer/LVGL and capacitive touch coordinate transform (conceptual `(x,y) → (799−x,479−y)`); not currently implemented in ESP32 firmware.

**No firmware, desktop app or physical parts were changed or tested. No purchasing or printing is authorised by this note.**

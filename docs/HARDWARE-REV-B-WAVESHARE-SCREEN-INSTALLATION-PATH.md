# Rev B R5 — Waveshare screen installation and screw access screening

**26 October 2026.** Based on the user-selected rounded 156mm, USB-left, physically rotated-180° Waveshare screen, 4mm media caps and **hook-and-click V2** underside cover. The cover has **zero screws**, and the *screen support* retains **four provisional M2.5 screw locations**. This is a **mechanical screening report only**, not a solved physical insertion path or manufacturable case.

## Executive result

**The earlier claim “68.3mm board is wider than a 59.1mm underside opening, so it might not enter” was too simplistic.** The board's 68.268mm dimension is measured along its *inclined front face*, not along desktop Y. Its **conservative manufacturer-derived 3D bounding box**, in the intended 55° tilted installed pose at provisional glass W=3.25mm, projects to about **53.01mm of desk Y**. The open underside hole measures about **59.09mm desk Y**, nominally leaving 6.09mm total front/back clearance after shifting, and the module's **106.106mm X width** is narrower than the hole's **134mm X width**. This necessary footprint test does **not** prove that the module can pass through a real three-dimensional enclosure.

At its nominal *seated* position, that whole rectangular envelope extends to desktop **Y=75.135mm**, but the hatch rear edge is at **Y=71.093mm**, so an upright-underneath approach at the seated Y cannot pass the hatch projection. For a box of the same orientation to fit in the aperture's Y footprint, a temporary forward translation in desk Y in the rough range **−10.13mm to −4.04mm** would be needed. **The final aligned position is NOT within this entry projection.** A combined shift/tilt then raising/positioning may be needed. These numbers are *staging hypotheses*, not collision-free paths.

## Source geometry and coordinates

- **Case:** unchanged pre-exported `SpotifyDesk_R5_hook_click_v2_CASE.step`; **unchanged** R5 hook-click V2 lid. Full outer size ~156 × 83.093 × 106.107mm, existing underside rectangular opening **X=11…145, desk Y=12…71.093mm**, nominal cut extends up to Z=8mm from desk plane.
- **2023 Waveshare assembly:** manufacturer's original 31,338,066-byte `esp32-s3-touch-lcd-4_3.stp`, from official ZIP SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`. We use the **previously extracted dimensions of the real 693-part assembly** from `mechanical/revB/cad/waveshare_step_reference.json`; original 693-solid STEP **was NOT used as the moving solid in these checks** and is not redistributed in the resulting ZIP.
- **Screen mounting:** four standoff centres at **98 × 60mm pitch**, face local points X≈12.05/110.05mm and V≈11.8/71.8mm; nominal support rear face W≈18.65mm. Face local W is the inwards normal, distinct from vertical desk Z. USB power front-left, I2C front-right after physical 180° rotation.
- **Module envelopes:** full 106.106 × 68.268 × 16.906mm assembly **bounding prism** (conservative occupied solid, includes large empty spaces); touch-glass bounding prism separately. Provisional installed glass offset **W=3.25mm inward**, unchanged from previous R5 CAD and not physically measured.

## Summary of actual CAD checks (not 693-solid full-board checks)

| Check | Sampled result | How to interpret it |
|---|---|---|
| 2D X footprint | 106.106mm board vs 134mm hatch | Fits in X projection, not proof of full 3D clearance |
| 2D desk-Y footprint | ~53.01mm module prism vs ~59.09mm hatch | Fits after shifting; **68mm face-side comparison was not decisive** |
| Nominal seated Y bound | module rear Y≈75.135mm, hatch rear Y≈71.093mm | **4.04mm rear overhang** in projection at seated alignment |
| Sampled straight vertical approach | Nominal 0° tilted body, Z offsets −110…0mm; several clash points | **This particular direct path isn't clear** under simplified prism modelling |
| Sampled ±15° temporary approaches | 27 sampled poses total across ±15° and 0° | Several bounding-prism/case overlaps; **not exhaustive motion planning**, cannot declare any/all angled paths impossible |
| Full rectangular assembly prism at nominal seat | ~**689.22mm³** overlap with **unchanged real case STEP** | A *conservative false-positive-prone solid box*: may represent unused volume rather than real PCB/part clash |
| Touch-glass prism at nominal seat | **0.00mm³** overlap | Glass-only volume clears in this trial; mount location and real glass shape still need measuring |
| Provisional screwdriver shaft 4mm diameter, length 40mm | Two W-axis support locations around face V≈11.8mm show ~**46.27mm³** shell intersection each; two around V≈71.8mm ~0.25mm³ | Potential access obstacle at the upper/rear screen mounting row, but screw head orientation/tool body are not known; not definitive |

**Do not read any of these results as the actual full 693-body STEP tested against the case.** Full STEP import was attempted but exceeded this environment's run time; these checks deliberately use manufacturer-extracted box bounds instead. As a result a collision *can be conservative/false* and a noncollision may omit real cables, fastener heads or board variations.

## Recommended engineering decision (before cutting any new case)

1. **Keep the 4mm R5 case and hook-click V2 latch unchanged for now.** The hatch could be adequate for a *carefully tilted and shifted* insertion, but a collision-free rigid 3D trajectory has not been demonstrated. Keep the case's original strength and appearance until we find a concrete reason to change it.
2. **Verify the actual fastening direction** from the Waveshare board's real fasteners. The support pads model drilled through-holes but **we have not established which side receives screw heads** or whether a screwdriver can approach squarely after the module is seated. A 4mm shaft cylinder in positive-W is merely a trial access route, not the manufacturer's assembly instruction.
3. **Prefer an assembly-first mechanical mock-up**: cardboard/acrylic full-size module envelope and enclosure opening, or 3D printed display template and separately printed mounting-corner gauges (requires printer). Test insertion at a shallow tilt, translate the board in desktop Y, rotate it to the 55° seating plane and attempt screwdriver access. Confirm cables and fasteners using purchased exact revision before print signoff.
4. **If physical installation is impossible**, trial one of these as *separate* CAD alternatives: **A. removable front bezel/frame** fitted after inserting board from above; **B. split rear shell and face structure** joined at a subtle concealed seam so screen can drop into the front before the shell closes; **C. adjust/enlarge underside hatch + provide accessible screw corridors**, but this could compromise the two front hooks and one rear catch. The entire shell should not be split solely because face dimension 68.3 > desk-Y hatch 59.1.
5. **Printability/electrical gates remain**: full chosen keycap profile, visible aperture alignment, touch ribbon and antenna keepout, USB-C power cord and I2C connectors, hole clearance and thread depth, screen screw torque, screen assembly access, case deformation and PETG latch fatigue.

## Deliverables

- **Source:** `mechanical/revB/cad/screen_install_path_study.py` and `screen_install_study_parameters.json` (Python standard library for measurement and SVG; optional CadQuery with pre-generated STEP to run B-Rep trial). Does not rewrite earlier CAD.
- **Regression suite:** `test_screen_install_path_study.py`: **20 new assistant-side checks passed**, consisting of 15 ordinary geometry/guard tests and 5 real-CAD tests (using existing hook-click V2 STEP). On the user's Windows setup without CadQuery or the optional source STEP path, **five B-Rep tests skip**. More importantly, passing tests **does not prove assembly**.
- **Drawings:** `waveshare_underside_projection.svg` shows bottom hatch Y vs board envelope; `waveshare_installation_side_section.svg` shows an illustrated vertical cross-section and rough screw shaft directions.
- **Reference STEP assemblies in separate conversation ZIP:** unchanged V2 case plus simplified nominal-position full module box and touch glass box; separate reference with board bounding box staged 60mm beneath case. These are not modified manufacturing shells or the redistributed manufacturer board.
- **Report:** `screen_installation_2023_reference_report.json` includes optional 27 sampled 3D clearance poses, tool cylinders and explicit warnings; `--report-only` output includes 2D measures and warnings without importing CAD.

## Windows PowerShell

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_screen_install_path_study.py -v
python mechanical\revB\cad\screen_install_path_study.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-ScreenInstall"
Invoke-Item "$HOME\Downloads\SpotifyDesk-ScreenInstall\waveshare_underside_projection.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-ScreenInstall\waveshare_installation_side_section.svg"
```

Optional actual geometry checks, if CadQuery is installed and a verified pre-generated **V2 hook-click case STEP** is available locally:

```powershell
$case = "$HOME\Downloads\SpotifyDesk-HookClick-V2\SpotifyDesk_R5_hook_click_v2_CASE.step"
python mechanical\revB\cad\screen_install_path_study.py --case-step $case --out-dir "$HOME\Downloads\SpotifyDesk-ScreenInstall-CAD"
$env:SPOTIFY_HOOK_CLICK_V2_CASE_STEP = $case
python -m unittest discover -s mechanical\revB\cad -p test_screen_install_path_study.py -v
```

If `$case` is located elsewhere (for example after extracting the earlier V2 ZIP), change the path; this snippet does not assume that file was generated by `--report-only`. **Do not install CadQuery merely to open the provided STEP reference assemblies in FreeCAD.**

**Status:** installation *screened*, not solved. No structural/latch/electrical CAD geometry edited; no approval to print a functioning finished unit.

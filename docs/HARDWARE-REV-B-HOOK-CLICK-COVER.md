# Rev B — hook-and-click screwless underside cover (experimental CAD)

**2026-10-26. Requested by user.** Preferred design branch: R5 rounded exterior, 156 mm wide, physically flipped Waveshare display with USB-C left, three nominal 4 mm-at-rest MX controls, volume encoder unchanged. The user explicitly wants **zero screws in the underside cover**, while **keeping screw-fastened LCD supports**. The previously committed four-screw lift-off cover, slide-through rail lid, 2/4/6 mm keycap cases and original Rev B CAD were **not modified or deleted**.

## New mechanism

1. A **separate printed ~133.2 × 58.29 × 2.0 mm underside plate** fits inside the original X11..145, Y12..71.093 mm hatch. Trial clearance is 0.4 mm per side. Plate flush position remains approximately Z=0.55..2.55 mm.
2. **Two rigid front locating tongues** (10 mm wide) project ~2.2 mm past the front underside opening. The case has **two narrow roofed receiving pockets**. These mechanically locate and restrain the front lip of the plate against straight downward removal.
3. A **single integral rear spring beam** in the removable cover (26 mm across X, ~2.2 mm wide in Y, 2 mm thick Z) terminates in a small raised nose. A ~7 mm wide **localised case pocket**, not a full-width rear-wall slide-through opening, captures the end above a keeper shelf. The user can press the finger-accessible free end **toward the front (negative Y)**, then lower the rear and unhook the front.
4. **No lid screws, lid screw bosses, magnets or separate hardware**. **Four manufacturer-reference LCD mounting holes** remain aligned to 98 × 60 mm and nominal Ø2.9 mm through-holes for M2.5 candidate fasteners. Screen retaining screws remain an intended separate assembly choice.

This is an **actual CAD solids study**, not a rendered mock-up. It does **not** yet establish that the rear spring will flex far enough (nominal 1.6 mm release stroke), click reliably or avoid fracture when printed. The generated lid is static/unflexed. No true elastic FEA, dynamic insertion sweep with deformed latch, or printed-material test was run. The root of this spring is still simplified/has square corners and is **not fatigue-validated**. Do not print the entire controller as a functional assembly from this design without a smaller tolerance/clip test.

## Trial measurements (mm)

| Dimension | Value |
|---|---:|
| Case overall width | 156.0 |
| Access opening (unchanged, bottom XY) | 134.0 × 59.09 |
| Separate cover plate | 133.2 × 58.29 × 2.0 |
| Trial perimeter clearance | 0.4 each side |
| Front hook X centres | 46.5 and 109.5 |
| Front tongue width | 10.0 each |
| Front tongue front extension | 2.2 beyond opening |
| Rear spring arm span | 26.0 |
| Spring arm width (horizontal XY) | 2.2 |
| Local rear notch width | 7.0 |
| Rear engagement reach into solid wall | 1.1 |
| Trial release deflection | 1.6 |
| Bottom lid screws | 0 |
| Screen screw targets | 4 at 98 × 60 pitch |

The 0.4 mm nominal clearance is **not a material-certified print setting**. It may be too small or large depending on material, layer/line width, slicer shrink, chamfers and actual printer calibration.

## CAD validation and limits

- **29 local Python tests passed**, with **9 CadQuery/STEP-specific checks** (same execution environment). Real CAD source and generated solids reopen as **two individually valid, single-solid B-Reps**, with zero volumetric overlap when the lid is seated.
- All four historical bottom screw holes remain solid in the new cover. CAD samples verify actual material at both front hooks and that pulling the unflexed lid downward by 0.65 mm causes mechanical collision with the frame (as intended), not a free-falling panel. This is a **geometric interference** result, not measured holding force.
- The new case retains the original **156 mm R5 body**, nominal left-side USB opening, nominal 4 mm media-key retainer layout and **four screen mounting-arm screw locations**. The earlier upper/lower cover screw boss code is **not** imported into this new shell.
- Important unresolved gate: the real Waveshare board is ~106.1 × 68.3 mm, while the underside opening has only ~59.1 mm depth along the desk axis. LCD insertion, fastening/driver access, proximity to antenna, USB/C cable strain relief and full component collision **have not been proven**. Current manufacturer STEP from 2023 may not match purchased revision.
- Print orientation and material decisions (especially layer direction across the flexible beam) can be decisive. **PETG is a sensible trial for a clip coupon**, not a guarantee of suitable stiffness/strength. A small hook/catch coupon with 0.25/0.4/0.55 mm wall/fit variants is the next physical step after user visual acceptance.

## CAD assets

Under `mechanical/revB/cad/`:

- `hook_click_cover_study.py`: parametric report + separate CadQuery STEP build; `--report-only` requires standard Python only.
- `hook_click_cover_parameters.json`: all test dimensions and engineering warnings.
- `test_hook_click_cover_study.py`: 29 regression checks, nine requiring optional CadQuery + Shapely.
- `hook_click_underside_plan.svg` and `hook_click_operation.svg`: checked-in reference views.

A separate downloadable chat ZIP contains two actual STEP solids, assembled and removed STEP assemblies, CAD-derived perspective PNGs, reference SVGs, JSON and a complete offline source copy including local imports. No third-party Waveshare STEP bytes are redistributed.

## Windows PowerShell validation

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_hook_click_cover_study.py -v
python mechanical\revB\cad\hook_click_cover_study.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-Hook-Click"
Invoke-Item "$HOME\Downloads\SpotifyDesk-Hook-Click\hook_click_underside_plan.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-Hook-Click\hook_click_operation.svg"
```

On Windows without CadQuery/Shapely **9 of the 29 tests will skip**. This still checks standard-library geometry, output consistency, four screen screw targets and basic catch release arithmetic. The pre-generated STEP files in the chat ZIP can be inspected in FreeCAD **without** installing CadQuery.

Optional CAD regeneration with CadQuery installed:

```powershell
python mechanical\revB\cad\hook_click_cover_study.py --out-dir "$HOME\Downloads\SpotifyDesk-Hook-Click-STEP"
```

## Successor CAD: improved V2 latch and matching trial coupons (2026-10-26)

After reviewing this original concept, the user asked for refinement. A new **independently generated [V2 latch design](HARDWARE-REV-B-HOOK-CLICK-LATCH-V2.md)** rounds the spring-beam root, adds an *upper entry cam* while retaining the lower catch, and provides an underside press pad. Full case geometry, four screen screw mounts and two front hooks are identical to this V1 model, but the removable lid now has improved latch features. **Two separate small STL coupons** are true CAD crops of that latch and its case keeper for later printer tests. The present V1 model and the older screw/slider options are preserved. V2 is not print/elastic/fit approved; Windows and physical sample results pending.


## Next acceptance gates

1. Review the bottom closed/open STEP assemblies in FreeCAD. Confirm the style and location of the fingertip release versus the two hooks; the new pocket is only 7 mm wide, avoiding the long rear-wall slot.
2. Improve the spring root radii and test a **small replaceable PETG catch-and-keeper coupon**. Verify flex deflection, push force, audible/tactile engagement and at least repeated opening/closing, including changing temperatures. Do not assert the latch reliably clicks based on current rigid geometry tests.
3. Model the actual insertion sequence with a *deformed* spring and test whole Waveshare board insertion and screw-driver access. Be prepared to split the enclosure body if the screen cannot enter through the underside hatch.
4. Only after actual printed coupons and manufacturer PCB revision/cable geometry are checked, advance toward fabrication-ready shell tolerances. Tech Toppers keycaps remain awaiting supplier's response.

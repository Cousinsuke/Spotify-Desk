# Waveshare true-solid STEP pose screening

**Status: manufacturer-model Windows run completed; nominal final seated position fully evaluated and clear above 0.05 mm³ penetration threshold (693/693 booleans). Screen installation and fastening are still unverified. NOT fabrication approved.** This is a separate study: the accepted R5 case, four LCD mounts, 4 mm keycaps, left USB-C and hook-click V2 lid remain unchanged.

## Scope and interpretation

- The new `mechanical/revB/cad/waveshare_true_solids_pose_study.py` imports real solid bodies from the 2023 Waveshare 31,338,066-byte STEP using OpenCascade STEPControl. It checks its extents against existing reference measurements, requires all 693 expected solids, and applies the documented 180-degree physical screen rotation and 55-degree enclosure orientation.
- It checks six **discrete** staged Y/Z poses against the original V2 case STEP. Bounding boxes are used only to eliminate impossible collisions; the remaining potential overlaps undergo exact CAD solid intersections.
- Reports only the first proven positive collision per pose. If an intersection operation fails or the default 160-per-pose boolean budget is exhausted, the status is **INDETERMINATE**. `SAMPLED_POSE_CLEAR` means one pose was tested completely, **not** that a moving screen fits through the hatch.
- The local JSON contains source hashes, number of model solids and per-pose evidence. Manufacturer STEP, existing case STEP and generated reports are never committed.

**Not modeled or established:** continuous motion, arbitrary rotations, preassembled carrier rails, USB/I2C plugs and wiring, screws, tool heads, board-revision differences or 3D-print tolerance. A failed chosen approach does not prove that no approach exists.

## User's first real 693-solid Windows run (2026-10-26)

- User ran the **8 existing regression tests: 8 passed, 0 failed** with CadQuery on Windows. Note these are synthetic/reference tests; the separate CLI did the actual manufacturer-geometry work.
- Source STEP loaded **693 solids**. Actual extent matched reference within **0.0031 mm**. Input STEP SHA-256: `d535d0e3b561c8f3d45a39f51eb2f1210d5e1d4875d104c339eb33e190a161c2`; original V2 case SHA-256: `87bf153a0bd2c48f1e896d8d84b6cd88f77e74aa3c8eaa4440c1669148f72b73`.
- `dy=-7,dz=-110`: **SAMPLED_POSE_CLEAR** (0 case/solid candidate overlaps; screen is below case).
- `dy=-7,dz=-75`: **SAMPLED_SOLID_COLLISION**, first component intersection **49.6198 mm³**, index 0.
- `dy=-7,dz=-40`: **SAMPLED_SOLID_COLLISION**, **44.2904 mm³**, index 0.
- `dy=-7,dz=-20`: **SAMPLED_SOLID_COLLISION**, **347.2754 mm³**, index 0.
- `dy=-7,dz=0`: **SAMPLED_SOLID_COLLISION**, **4354.9805 mm³**, index 0.
- `dy=0,dz=0` (nominal seated): **INDETERMINATE_LIMIT** after **160 of 693 candidate solid intersections**. Cannot call final fit clear or blocked from this unfinished position check.
- The -7mm vertical staging approach is demonstrably blocked at sampled points; this does not rule out different translation/rotation paths. The initial case/model pairing is not a final assembly placement qualification.

## Focused follow-up: resolve nominal seated collision and report WHERE

The diagnostic now accepts `--seated-only` to check only `dy=0,dz=0`, avoiding repeated stages. Use `--max-booleans-per-pose 1000` to cover up to all 693 candidate solids; an exact solid intersection may conclude sooner. Any first real intersection now includes **world-coordinate XYZ bounding boxes** for the colliding solid and the intersection volume, to pinpoint where the clash occurs. The positive-collision threshold remains 0.05 mm³; a pose otherwise called clear is only clear relative to that threshold and this historical CAD model. This follow-up has **not yet been run by the user**.

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
$cadPython = "$HOME\Documents\SpotifyDesk-CAD\.venv\Scripts\python.exe"
$case = "$HOME\Documents\SpotifyDesk-CAD\References\HookClick-V2\output\SpotifyDesk_R5_hook_click_v2_CASE.step"
$manufacturer = "$HOME\Downloads\SpotifyDesk-Waveshare-Official-3D\extracted\esp32-s3-touch-lcd-4_3.stp"
$outSeated = "$HOME\Documents\SpotifyDesk-CAD\Waveshare-Seated-Only"
& $cadPython -m unittest discover -s mechanical\revB\cad -p test_waveshare_true_solids_pose_study.py -v
& $cadPython mechanical\revB\cad\waveshare_true_solids_pose_study.py `
  --manufacturer-step $manufacturer `
  --case-step $case `
  --out-dir $outSeated `
  --seated-only `
  --max-booleans-per-pose 1000
Get-Content "$outSeated\waveshare_true_solids_pose_report.json"
```

## Nominal seated clearance confirmed by Windows (2026-10-26)

- User pulled `bdbc5ad`, then re-ran `test_waveshare_true_solids_pose_study.py` on Windows: **8/8 passed**, no skipped or failed tests.
- User ran `--seated-only --max-booleans-per-pose 1000` on the official local 693-solid 2023 manufacturer STEP and unmodified V2 R5 case STEP. Result: **`SAMPLED_POSE_CLEAR`**, **693/693 exact solid intersections completed**; **no model-material intersection above 0.05 mm³** for the final position `(dy=0,dz=0)` with assumed 3.25 mm glass recess.
- SHA-256 values match the earlier recorded manufacturer STEP `d535d0e3b561c8f3d45a39f51eb2f1210d5e1d4875d104c339eb33e190a161c2` and baseline V2 case `87bf153a0bd2c48f1e896d8d84b6cd88f77e74aa3c8eaa4440c1669148f72b73`; case/manufacturer reference bounds unchanged.
- The earlier `INDETERMINATE_LIMIT` at 160 of 693 booleans is **resolved for nominal seating only**. This does *not* prove there is a continuous installation path or safe fastener access; zero or near-zero surface clearance, optional rails, cables and hardware revision are not established.
- **Next experimental stage:** inspect sampled near-seat extraction motions in [the separate path probe](HARDWARE-REV-B-WAVESHARE-EXTRACTION-PATH.md). Keep baseline enclosure, mounts and V2 lid intact.

## Windows PowerShell

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main

$cadPython = "$HOME\Documents\SpotifyDesk-CAD\.venv\Scripts\python.exe"
$case = "$HOME\Documents\SpotifyDesk-CAD\References\HookClick-V2\output\SpotifyDesk_R5_hook_click_v2_CASE.step"
$manufacturer = "$HOME\Downloads\SpotifyDesk-Waveshare-Official-3D\extracted\esp32-s3-touch-lcd-4_3.stp"
$out = "$HOME\Documents\SpotifyDesk-CAD\Waveshare-True-Solid-Study"

& $cadPython -m unittest discover -s mechanical\revB\cad -p test_waveshare_true_solids_pose_study.py -v

& $cadPython mechanical\revB\cad\waveshare_true_solids_pose_study.py `
  --manufacturer-step $manufacturer `
  --case-step $case `
  --out-dir $out `
  --max-booleans-per-pose 160

Get-Content "$out\waveshare_true_solids_pose_report.json"
```

The standalone regression suite uses synthetic geometry and reference metadata; it does not require the 31MB manufacturer model. The CLI uses the actual original file on Windows and refuses mismatched size/bounds/part count. Increase `--max-booleans-per-pose` (up to 1000) only when an output is INDETERMINATE_LIMIT; never treat a time or computational budget as proof of clearance.

## Previous verified baseline

The user ran **20/20 Windows case/bracket tests with CadQuery 2.8.0, Shapely 2.2.0, 0 skipped**. The *earlier conservative rectangular-prism* study reported **214.56 mm³ case/rail clash per bar**, **0 mm³ two trial vertical tool-cylinder clashes**, and no certified continuous entry route. See [screen assembly options](HARDWARE-REV-B-SCREEN-PREASSEMBLY-AND-ENTRY-OPTIONS.md).

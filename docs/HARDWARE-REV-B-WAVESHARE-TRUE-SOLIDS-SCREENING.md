# Waveshare true-solid STEP pose screening

**Status: code committed, user-local execution pending. NOT fabrication approved.** This is a separate study: the accepted R5 case, four LCD mounts, 4 mm keycaps, left USB-C and hook-click V2 lid remain unchanged.

## Scope and interpretation

- The new `mechanical/revB/cad/waveshare_true_solids_pose_study.py` imports real solid bodies from the 2023 Waveshare 31,338,066-byte STEP using OpenCascade STEPControl. It checks its extents against existing reference measurements, requires all 693 expected solids, and applies the documented 180-degree physical screen rotation and 55-degree enclosure orientation.
- It checks six **discrete** staged Y/Z poses against the original V2 case STEP. Bounding boxes are used only to eliminate impossible collisions; the remaining potential overlaps undergo exact CAD solid intersections.
- Reports only the first proven positive collision per pose. If an intersection operation fails or the default 160-per-pose boolean budget is exhausted, the status is **INDETERMINATE**. `SAMPLED_POSE_CLEAR` means one pose was tested completely, **not** that a moving screen fits through the hatch.
- The local JSON contains source hashes, number of model solids and per-pose evidence. Manufacturer STEP, existing case STEP and generated reports are never committed.

**Not modeled or established:** continuous motion, arbitrary rotations, preassembled carrier rails, USB/I2C plugs and wiring, screws, tool heads, board-revision differences or 3D-print tolerance. A failed chosen approach does not prove that no approach exists.

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

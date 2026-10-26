# Rev B — full Waveshare screen extraction waypoint probe

**26 October 2026 — new CAD script pending user-local Windows execution.** The user's nominal seated screen assembly cleared **all 693/693** real 2023 manufacturer-model solids against the unchanged V2 R5 case, using a **0.05 mm³ penetration threshold**. This verifies only the single assumed seated pose (3.25 mm front-glass recess); it does not verify assembly, touching surfaces, printed tolerances, brackets or cables.

## Why this follow-up exists

The former model was represented by a filled outer bounding prism and incorrectly suggested possible body clashes at nominal seating. Real part-by-part booleans showed **no solid penetration above threshold when seated**. The earlier shifted vertical insertion samples at Y=-7 mm failed, however. The remaining question is whether a **short rigid-body motion from the seated position toward the underside** can be found. If so, a later study can extend and *sweep* that candidate route. No case or lid CAD should be replaced until assembly and fasteners are supported.

## New source and behaviour

- `mechanical/revB/cad/waveshare_extraction_path_probe.py` — separate diagnostic. It loads the unchanged case and 693 manufacturer STEP solids from local files, verifies the manufacturer reference dimensions, and tests three short candidate **reverse extraction** directions from the clear seated pose. For rigid-body screen geometry, reversing a valid extracted trajectory would give an insertion candidate, but physical cabling and fastener requirements are absent.
- Default profiles: vertical translation; 8 mm forward / 28 mm down; and the same translation with up to +12° world-X pitch. Optional `forward_pitch_minus` and `rearward` profiles are also defined. Seven positions per profile (including the shared starting position) are sampled over the 28 mm travel. A maximum of 20 **unique** poses are considered by default; repeated starting poses are cached.
- Each step rotates/translates the complete 693-solid model together and uses bbox-only elimination followed by true CAD intersection checks. On the first positive collision or incomplete calculation, that path stops. Result statuses distinguish `SAMPLED_SOLID_COLLISION`, `INDETERMINATE_LIMIT`, `INDETERMINATE_BOOLEAN_ERROR`, `POSE_BUDGET_EXHAUSTED`, and `ALL_SAMPLED_WAYPOINTS_CLEAR_NOT_SWEPT`.
- Six local synthetic unit tests passed during development, including two-body CadQuery rigid rotation; full manufacturer/case execution is **not yet tested on the user's PC**. Each runtime path may stop early once a collision is found.

**Important limitations:** Even seven clear poses cannot establish that any motion *between* them is collision-free. There is no continuous swept-body clearance certification, proof of positive clearance to adjacent surfaces, pitch-axis optimisation, male USB-C plug, I2C harness, screws, case carrier rails, or printer tolerances. This is an investigation, not a fabrication-approved solution.

## Windows PowerShell

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
$cadPython = "$HOME\Documents\SpotifyDesk-CAD\.venv\Scripts\python.exe"
$case = "$HOME\Documents\SpotifyDesk-CAD\References\HookClick-V2\output\SpotifyDesk_R5_hook_click_v2_CASE.step"
$manufacturer = "$HOME\Downloads\SpotifyDesk-Waveshare-Official-3D\extracted\esp32-s3-touch-lcd-4_3.stp"
$out = "$HOME\Documents\SpotifyDesk-CAD\Waveshare-Extraction-Path"

& $cadPython -m unittest discover -s mechanical\revB\cad -p test_waveshare_extraction_path_probe.py -v
& $cadPython mechanical\revB\cad\waveshare_extraction_path_probe.py `
  --manufacturer-step $manufacturer `
  --case-step $case `
  --out-dir $out

$report = Get-Content "$out\waveshare_extraction_waypoint_report.json" -Raw | ConvertFrom-Json
$report.path_results | Select-Object profile,status,waypoints_tested | Format-Table -AutoSize
```

To inspect an interruption, use `$report.path_results | ConvertTo-Json -Depth 8`. Optional extra profiles can be supplied with `--profiles vertical forward forward_pitch_plus forward_pitch_minus rearward` and `--max-total-poses 35`. Do not call any series of discrete clear samples a verified continuous entry route.

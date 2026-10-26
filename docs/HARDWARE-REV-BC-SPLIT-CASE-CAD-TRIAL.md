# Rev B-C — split front carrier, rear shell and L controls PCB CAD trial

**26 October 2026. Separate experiment, user authorised the prototype. NOT print-ready, electrically reviewed or physically assembled.** This alternative responds to the proposal to assemble the screen/three controls/knob from the fully open rear instead of inserting the whole Waveshare through a small bottom hatch. The old hook-click V2 case/lid and their source files are unchanged.

## What was made

The separate generator `mechanical/revB/cad/split_case_control_pcb_study.py` produces a fully closed-bottom **two-piece split** version of the original 156×83.093×106.107 mm R5 wedge and one **unpopulated custom control PCB outline**. It uses the same 55° front face, front-visible Waveshare screen aperture rotated in-plane 180° for USB-left, three 30mm-pitch MX key centres (31.05/61.05/91.05 at V=91), 4mm nominal cap rest, and knob centre (138,44).

Chosen trial **front-plane inward-W seam**: 24.0mm behind the sloped face, with 0.4mm nominal gap between the front and rear solids. This is a flat partition of the outer hollow wedge and leaves a **removable rear half** instead of a small bottom-access hatch. The split currently has **no locating ribs, lock tabs, clip flexures, seals or service screws**. The rear shell is deliberately not retained by anything yet.

**Trial PCB envelope:** one L-shaped planar polygon in front-face X/V coordinates: `[[17,80],[117,80],[117,36],[149,36],[149,57],[124,57],[124,105],[17,105]]`. Thickness 1.6mm, W offset 18mm behind the front face. This reaches the three lower keys then routes behind the knob at the right side while staying outside the rectangular screen footprint in front projection. It represents **neither a manufactured PCB nor a mounted board**: it has no drill holes, traces, switch footprints, encoder pads, I²C port, AW9523 circuitry, standoffs or solder-side keepouts. Actual switch/encoder installed depths remain unknown.

The original Waveshare is a **full ESP32-S3 display controller board**, not a bare LCD that must connect to a second MCU. It is intended to screw to a **structural front support** (not unsupported copper-plated PCB holes). The current CAD DOES NOT YET HAVE that support, retaining fasteners, correct switch-retention plate or installed Waveshare body. The screen mounting targets of 98×60mm are documented in the report only. The 19.2mm wells in the first trial case are preliminary cap openings, **not MX retention holes**.

## Local geometry evidence

- Assistant CAD environment used CadQuery 2.8.0 + Shapely and generated **three independent valid single-solid B-Reps**: front carrier shell, rear shell and flat L-shaped control PCB reference. Each independently exported and reimported as STEP successfully.
- Full shell dimensions match Rev B. Modelled front/rear solid material overlap **0mm³**, control PCB/half-shell overlap **0mm³**. These tests do not certify positive clearance for assembled electronics; neither true manufacturer STEP nor populated switches/encoder were included.
- Local tests checked selected dimensions and positions, rotated visible screen window X=13.33,V=17.09, safety guards on invalid seam/PCB settings, valid CAD solids and zero intersections. **No Windows user runtime validation yet**, and the separately committed unit test suite must still be run on the user's Python environment.
- Binary STEP references, CAD diagram and rendered previews are delivered as a chat ZIP; GitHub stores **generator, parameters, tests and documentation**. No modified original V2 binary STEP, Waveshare vendor CAD, account credentials or prototype PCB Gerbers are committed.

## Generated files (separate ZIP)

- `SpotifyDesk_RevBC_FRONT_CARRIER_TRIAL.step` — new front shell, no real screen bosses or clips
- `SpotifyDesk_RevBC_REAR_TUB_TRIAL.step` — new removable back and base, no closure latch
- `SpotifyDesk_RevBC_CONTROL_PCB_OUTLINE_ONLY.step` — single L-shaped empty board reference
- `SpotifyDesk_RevBC_REFERENCE_ASSEMBLY.step` — all three assembled at their intended coordinates
- `split_case_control_pcb_concept.svg`, `split_case_control_pcb_report.json`, CAD preview PNGs

## Regenerate on Windows — PowerShell

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
$cadPython = "$HOME\Documents\SpotifyDesk-CAD\.venv\Scripts\python.exe"
$out = "$HOME\Documents\SpotifyDesk-CAD\Split-Case-RevBC"

& $cadPython -m unittest discover -s mechanical\revB\cad -p test_split_case_control_pcb_study.py -v
& $cadPython mechanical\revB\cad\split_case_control_pcb_study.py --out-dir "$out"
Invoke-Item "$out\split_case_control_pcb_concept.svg"
Invoke-Item "$out"
```

The script's `--report-only` mode generates JSON and SVG with standard Python and no CadQuery requirement. The actual STEP export mode expects the already configured Windows CadQuery/Shapely virtual environment.

## Next engineering pass

1. Place the actual **693-solid** local Waveshare STEP into this **separate** proposed front carrier (use exact 2023 file/revision; screen-inward W=3.25mm assumption) to map true collisions with shell and trial PCB, including USB plug corridor, right I²C connector and antenna keepout.
2. Dimension the **rigid four-point screen mount**, M2.5 thread/head direction and rear-access screwdriver shafts. The bare full screen outer box can give false-positive overlaps; test the true solids.
3. Resolve three MX **1.5mm mechanical retention plate**, switch contacts and four-mm cap height/stroke, plus encoder M7 nut, press travel and PCB plane/pads. Then choose single L-board or 2 compact linked boards based on actual mechanical envelope.
4. Engineer the shell joining seam with structural locating tongues and two accessible latches or removable underside screws; verify shell movement/assembly without snagging the USB power connector or cables; print test coupons before entire housing.
5. Only after physical stack and location verification design a **real KiCad circuit**, keeping the existing Waveshare ESP32-S3, six signals, verified 3.3V I²C and AW9523 safe power-up/reset/pull resistor network.

**Not approved** for ordering PCB fabrication or printing a complete production enclosure. The current STEP shapes establish **separable geometry and a provisional controls-board footprint**, not a finished front electronics assembly.

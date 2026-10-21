# Rev B — Parametric 3D internal packaging study

**2026-10-21. Status: design-only envelope modelling, not verified physical fit, wiring, or manufacturing geometry.** The original 156 mm sharp and R5-rounded STEP CAD cases and their associated files are **not edited**. This adds an independent, approximate **sharp-outline** 3D visualization and calculation of rectangular part envelopes. The original R5 fillet is **not represented** by the exploratory shell and may reduce local clearances.

## Inputs and scope

- [CAD original dimensions](../mechanical/revB/cad/dimensions.json): 156×110 mm 55° front, 16 mm chin, 20 mm roof, 3 mm **assumed** wall; module 106.1×67.8 mm at X=8,V=8; 3 MX centres X=31.05,61.05,91.05, V=91; knob X=138,V=44.
- [Scenario assumptions](../mechanical/revB/cad/internal_packaging_assumptions.json) are deliberately editable and **not manufacturer dimensions** unless separately identified in the CAD original references: LCD rear depth/offset, 14×14×16.8 mm trial switch block, encoder rear depth/pins, I²C cable position and bend, USB port/plug region, fixing marker sizes, AW9523B location, hatch clearance. Changes here **do not** automatically change the stored official CAD STEP shell.
- [`internal_packaging.py`](../mechanical/revB/cad/internal_packaging.py) (Python standard library) converts the 55° front local X (right), V (down face) and W (inward normal) coordinates to world desk Y/Z; calculates conservative rectangular three-axis box intersections and signed clearance to the trial sharp wedge's nominal 3mm inner boundary; exports configurable OpenSCAD parameters and machine-readable JSON report.
- [`internal_packaging_view.scad`](../mechanical/revB/cad/internal_packaging_view.scad) visualizes a **separate conceptual thin-wall 156mm wedge**, three switches, encoder body and terminal prism, display envelope, provisional cable envelopes, placeholder board, screw-location markers, and bottom access region. Red indicates any simulated encoder-body/I²C-envelope overlap. `internal_packaging_params.scad` is generated from the JSON to keep its constants aligned. Preview in OpenSCAD with **F5**; F6 renders the *study solids*, not a real case for printing.
- [`test_internal_packaging.py`](../mechanical/revB/cad/test_internal_packaging.py) verifies nominal layout, X/V/W mapping, collision scenario branching, left wall clearance, and parameter file synchronization.

## Current trial calculations (not measured hardware)

| Scenario | Simplified 3D result |
|---|---|
| 14 mm right-side assumed I²C cable projection | No encoder-body overlap in X/V/W; nominal X gap **3.3 mm**. Still not proof an actual plug/cable fits. |
| 20 mm right-side assumed I²C projection in same V and inward-W range | **2.7 mm X overlap**, with **13.2 mm V**, **13.1 mm inward-W** overlap against the trial encoder body. Terminal region also overlaps by **0.9 mm W**. This is *hypothetical*. |
| 20 mm I²C projection moved to trial start V=60 | No **encoder body** AABB overlap because V regions become separated. Cable path and board socket have **not** been reoriented or checked; this is not an approved reroute. |
| 6 mm leftward USB plug envelope from full LCD left X=8 | Trial box extends to X=2, entering the theoretical left inner wall boundary at X=3 by **1 mm**. A side service opening, shorter/right-angle plug or other placement may be required *if* a real connector occupies this space. |

No project case width change is approved by these scenarios. The nominal screen/encoder/support source details and all unresolved fit gates remain in [the earlier fit review](HARDWARE-REV-B-FIT-REVIEW.md).

## Windows 11 PowerShell

After `git pull --ff-only origin main`, from the repo root:

```powershell
# Validate default assumptions and produce an independent OpenSCAD study folder.
python mechanical\revB\cad\internal_packaging.py --verify-defaults --out-dir "$HOME\Downloads\SpotifyDesk-RevB-3D"

# Visualize the independent 3D study: open the output .scad in OpenSCAD, then F5.
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-3D"

# Explore a more demanding (still assumed) cable scenario without changing Git files.
python mechanical\revB\cad\internal_packaging.py --i2c-extension 20 --usb-extension 10 --out-dir "$HOME\Downloads\SpotifyDesk-RevB-3D-20mm"

# Automated Python checks.
python -m unittest discover -s mechanical\revB\cad -p test_internal_packaging.py -v
```

OpenSCAD is only needed to inspect the `.scad`; the Python report works without additional Python dependencies. Files in Downloads are generated and safe to delete; **do not modify the Git-tracked sharp/rounded STEP files** when trying scenarios.

## Distinguish proven from assumptions

**Static validation in assistant's environment:** 8 new Python tests passed; OpenSCAD successfully rendered the scene into a multi-solid diagnostic STL without CSG errors. This is a *geometry/rendering test*, **not** a printable fitted shell; no physical parts acquired or measured, and no Windows runtime execution of these newly added 3D scripts yet.

**Not modelled / open:** exact right I²C connector orientation and bend, left USB connector/power supply/port access, screen rear PCB protrusions and standoffs, MX clip flange and solder terminals, KZ0087 fit/grub screw and push travel, AW9523B real mounting and cables, ESP32 Wi-Fi antenna clear zone, bottom hatch fasteners, R5 fillets, electrical input protection, actual 3D collisions against manufacturer STEP parts. No model-specific board drill size or extra unverified dimension should be treated as final.

**Next design task:** decide feasible connector exit strategy and screen standoffs using manufacturer-source geometry where available; after that iterate **separate** new enclosure variant with explicit provisional mount bosses, local 1.5mm MX clip collars, port access and hatch mechanics. Do not overwrite retained Rev B sharp/R5 baseline until reviewed.

# Rev B — CAD comparison: 2 mm, 4 mm, and 6 mm raised MX media keycaps

**2026-10-21. User requested separate CAD designs for all three resting cap heights. Status: three independent experimental CAD prototypes have been generated and B-Rep-validated locally, NOT physical fit-tested and NOT manufacturing-ready.** The user has visually selected the *rounded R5 exterior and USB-C on the left* as the preferred design direction, but has not selected a keycap height or actual caps/switches.

## Downloaded outputs

The separately delivered ZIP, `Spotify_Desk_RevB_R5_2mm_4mm_6mm_Media_CAD.zip`, contains **three model folders**, a `source/` folder and comparison images. Each folder contains:

- `spotify_desk_rounded180_recessed_3keys_EXPERIMENTAL.step`: actual CAD **single-solid** R5 enclosure with three independent reinforced wells, MX retaining plates, USB-left trial slot, rotated display aperture, and the retained encoder hole.
- `spotify_desk_rounded180_with_cap_knob_ENVELOPES.step`: **multibody coloured reference CAD assembly** including the case, simplified 3 keycaps and previous / play-pause / next legends, trial MX head/base/stems, trial LCD full-envelope and knob. These are *not* manufacturer cap or switch CAD solids.
- `variant_settings.json`, `fit_report.json`, front-elevation SVG, and rest/pressed cross-section SVG.

Also included: `three_heights_actual_cad_isometric.png` (static render from actual STEP shells with separately modelled keycaps and knob), `three_heights_section_comparison.png`, `three_heights_front_comparison.png`, companion SVGs, three custom white media legend SVGs, and source/dependency scripts for independent regeneration. **The original 0° sharp/R5 Rev B cases, separate rotated180 sharp/R5 cases and original 2mm recessed media case are NOT overwritten.** The new 2mm shell's computed volume exactly matches the previous 2mm recessed shell.

## Parametric geometry (millimetres)

We adjust *the cap's resting height AND the MX switch-retaining plate*, rather than making only a higher cap visual. An approximately 8mm-deep cap on a presumed full-travel 4mm switch is supported by a 1.5mm retaining plate and ~23.2mm support collar. All manufacturer-unverified physical dimensions remain assumptions.

| Parameter | 2mm low/recessed | 4mm middle | 6mm higher |
|---|---:|---:|---:|
| Cap top above enclosure face at rest | 2.0 | 4.0 | 6.0 |
| Clip-bearing switch plate top depth inward (W) | 11.5 | 9.5 | 7.5 |
| Cap top at assumed full 4mm press relative to skin | 2.0mm *below* | Flush | 2.0mm *above* |
| Nominal MX stem-tip-to-cap reference | 3.3 | 3.3 | 3.3 |
| Nominal full-press cap skirt-to-plate clearance | 1.5 | 1.5 | 1.5 |

All variants use an **18mm square assumed cap**, **19.2mm square well** (0.6mm nominal clearance each side), **23.2mm outer support collar**, **1.5mm retention plate with 14mm MX clip opening**, ~30mm three-key pitch, and the same **15.1mm diameter knob envelope** at (X=138,V=44). Same 156mm-wide, 55° sloped, R5-rounded external case with nominal left USB-C1 service slot, physically rotated 180° Waveshare screen, display viewing aperture at (X=13.33,V=17.09), 95.54×54.36mm.

**Important technical limit:** Holding nominal stem-tip projection and skirt-to-*plate* clearance constant does **not** prove real keycap-to-switch engagement or 4mm downstroke clearance. The simplified keycap shell has no real manufacturer stem-socket cavity, printed fillets/tolerance design, stabilizer, clip tabs, switch PCB support or actual mating USB plug. The 6mm concept moves the MX switch housing closer to the face and changes internal load/support arrangement. Actual Cherry MX and selected cap size/profile must be obtained or independently dimensioned to check inner skirt / housing interferences, switch spring return and manufacturing tolerances before committing a print.

## Validation

- Python/CadQuery **20/20 new tests pass** in assistant environment, including STEP generation and re-import for three independent single-solid R5 cases, three multi-body coloured reference assemblies and comparison geometry. No full STEP geometry has been modified in place.
- Generated individual rounded B-Rep case volumes: 2mm = **138,105.0mm³**, 4mm = **137,087.4mm³**, 6mm = **136,069.8mm³**. They are distinct solids; changing the plate height changes collar volume. Case external shape, display aperture, knob bore and left USB slot remain in the same coordinates.
- **User Windows validation of these new 3-height scripts pending.** Existing 2mm media-controls study had 13 Windows tests passing with 2 optional CadQuery/Shapely skips; do not claim the new 20 tests have already been run on Windows.

## Windows PowerShell

From the repository root after pulling the new commit:

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_media_controls_height_variants.py -v
python mechanical\revB\cad\media_controls_height_variants.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-RevB-2-4-6mm"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-2-4-6mm\three_heights_front_comparison.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-2-4-6mm\three_heights_section_comparison.svg"
```

PowerShell report-only mode works with Python standard library. Two new B-Rep tests may **skip** without optional CadQuery/Shapely. To inspect the **pre-generated STEP CAD in FreeCAD**, open the ZIP provided in chat, extract it, then open the shell and assembly files from each `outputs/2mm`, `outputs/4mm`, `outputs/6mm` folder. No local CadQuery install is necessary for FreeCAD STEP inspection.

Optional full local STEP regeneration if CadQuery and Shapely are already installed:

```powershell
python mechanical\revB\cad\media_controls_height_variants.py --out-dir "$HOME\Downloads\SpotifyDesk-RevB-2-4-6mm-CAD"
```

## Next choice

Have the user compare the **actual CAD** 2/4/6mm STEP reference assemblies, especially how visible each cap is along the sloped face. Only after choosing a preference, select specific purchasable MX switch and cap profile, verify actual cap/skirt/stem/travel dimensions, then revise the *selected* separate shell. The previously identified cheaper blank 1U four-pack or a four-cap custom printed pack remain candidates; the caps shown are approximate 18mm envelopes, **not verified retail parts**. No order, print or fabrication clearance is implied by these files.

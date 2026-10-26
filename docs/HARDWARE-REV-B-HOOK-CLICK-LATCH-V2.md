# Spotify Desk Rev B — hook-and-click latch V2, matching test coupons

**2026-10-26. EXPERIMENTAL CAD, not a verified printable enclosure or rated snap latch.** Based on the user-selected rounded R5 156mm enclosure, left USB-C (Waveshare physically rotated 180°), **4mm keycap rest height**, and the previous two-front-hooks/one-rear-catch bottom cover. The screen is still fastened by **four provisional M2.5 screw targets** at **98×60mm**. **Zero screws in the underside cover.**

## Changes since original hook-and-click STEP

| Part | Earlier version | Revised V2 |
|---|---|---|
| Rear spring-beam root | Sharp inside corners | **R0.68mm inside root fillets** at two Z-vertical corners, reducing geometric stress concentration (not a strength certification) |
| Catch nose insertion lead-in | Essentially square top edge | **1.50mm Y retreat at upper nose** forming an angled top closing cam; original square lower shoulder retained below **Z=1.90mm** |
| Finger release | Small exposed beam/nose | **Approx. 7.7 × 2.85mm shallow underside press pad**, integral with the latch, not attached to surrounding cover |
| Full-size enclosure | Rounded R5 USB-left | **Exactly unchanged B-Rep**. Geometric boolean difference with earlier case measured **0mm³**. Existing two front hooks unchanged. |
| Testability | Only full-size enclosure and separate lid | Small **two-piece crop of the real latch and its real case keeper** exported as STL and STEP; assembled coupon STEP included. |

The latch beam remains nominally **26mm long × 2.2mm wide** with a **1.6mm proposed manual retract stroke**, as established in the previous study. The rough ideal cantilever surface-strain relation `1.5 × beam_width × deflection / beam_length²` yields **~0.781%** for these numbers. **This is only a thin-beam estimate**, not nonlinear structural FEA or an assurance about FDM layers, actual yield/creep, release force or cycles. The model does not simulate a flexed latch during assembly.

**Insertion orientation:** the upper part of the nose enters first as the lid is pressed **up** against the underside; the **upper beveled profile** is intended to make the nose move towards the front before clicking into the short rear keeper. The lower face retains its shoulder to resist pulling the cover down. The printed part may still require bevel/force redesign once tested.

## CAD and fit-test exports

**Full enclosure STEP files:**

- `SpotifyDesk_R5_hook_click_v2_CASE.step` (unchanged R5 case including screw-mount brackets)
- `SpotifyDesk_R5_hook_click_v2_LID.step` (the refined latch)
- `SpotifyDesk_R5_hook_click_v2_ASSEMBLY.step` (two installed solids)
- `SpotifyDesk_R5_hook_click_v2_EXPLODED.step` (detached lid reference)

**Small test coupon files:**

- `SpotifyDesk_latch_v2_test_LID.stl` and `.step` (actual cropped spring/root, nose and thumb pad)
- `SpotifyDesk_latch_v2_test_FRAME.stl` and `.step` (actual cropped keeper material from unchanged full case)
- `SpotifyDesk_latch_v2_test_ASSEMBLY.step` (two parts in nominal mated coordinates)

**Important:** the cropped latch piece demonstrates the local rear catch; it **does not include the two full-cover front locating hooks**. Test how it deflects **gently** and seats, but do not interpret success as complete case assembly approval.

## Print trial procedure and decision criteria

1. Open each STL in your slicer, keep model scale at **100% millimetres**, and place the largest supported flat face on the bed. Inspect orientation/supported overhangs manually—no universal printer orientation is prescribed. Keep the spring/root in a favourable continuous extrusion orientation; avoid relying on layer adhesion across the beam root. Print **the coupon before the full lid/case**.
2. Use a suitably flexible filament for latch trials (PETG is a practical first choice), with your own calibrated printer tolerances. The existing **0.4mm nominal lid edge gap** is *not* a guaranteed fitted clearance, and coupon results apply to your material/settings only.
3. With both coupons, test gentle registration, whether the lead-in makes the free tip retract as intended, whether the catch snaps back and retains against a light pull, and whether the small release pad can be pressed without a tool. **Stop** if it needs excessive force, whitens, cracks, sticks or delaminates. Do not force a jammed hook.
4. Repeatedly latch/unlatch while observing whether force or alignment changes. Record material, nozzle size, layer height, orientation, observed engagement and any damage. We can then parameterize the next nose/beam/keeper adjustment instead of guessing.
5. Before full enclosure print, separately solve **how the 68.3mm overall Waveshare assembly can enter the current ~59mm-deep underside hatch and be screwed to its standoffs**, plus USB cable routing, actual switch/keycap envelope, screw depth and cable service. **None are resolved here**.

## Validation

- **26/26 assistant-side new tests passed**: 16 Python geometry/parameter checks and 10 optional CadQuery/STEP solid checks. Four distinct source STEP solids exported, independently reopened and validated; zero installed lid-to-case and coupon-to-keeper solid overlap; the cropped retention shoulder produces rigid interference if the lid is artificially pulled down 0.65mm (not a force/strength check). Two coupon STLs and three reference assemblies exported.
- Previous original case versus new V2 case Boolean symmetric geometric difference: **0.0mm³**. Old hook-click and slider/screwed cover source/STEP remain **unchanged**.
- **User Windows validation, physical PETG coupon print and real click tests pending.** Windows without CadQuery/Shapely may run 16 standard-library checks while 10 actual STEP/B-Rep tests skip.

## Reproduce on Windows

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_hook_click_latch_refinement_v2.py -v
python mechanical\revB\cad\hook_click_latch_refinement_v2.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-HookClick-V2"
Invoke-Item "$HOME\Downloads\SpotifyDesk-HookClick-V2\hook_click_latch_v2_design.svg"
```

Optional actual STEP regeneration if CadQuery and Shapely are available:

```powershell
python mechanical\revB\cad\hook_click_latch_refinement_v2.py --out-dir "$HOME\Downloads\SpotifyDesk-HookClick-V2-STEP"
```

**No manufacturer source STEP is redistributed in this project.** The case uses the previous manufacturer-dimension-derived board mounting reference only.

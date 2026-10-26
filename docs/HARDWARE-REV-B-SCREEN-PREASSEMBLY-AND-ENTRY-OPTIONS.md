# Spotify Desk Rev B — screen installation and accessible mounting options

**Study date: 26 October 2026. Engineering assessment, not a solved installation path or a print-ready enclosure.** The user has selected the rounded R5 156 mm enclosure, physically rotated 180° Waveshare ESP32-S3-Touch-LCD-4.3 touchscreen (USB-C on the left), 4 mm media keycaps, and V2 hook-and-click screwless underside cover. The display remains screw-mounted at four nominal M2.5 positions on a 98 × 60 mm grid. **No existing case, lid, front cutouts or UI code is changed in this study.**

## Screen orientation, dimensional facts and restrictions

- Official product identified as **Waveshare SKU 25948 touchscreen**; official documentation specifies glass/module about **106.1 × 67.8 mm**, Type-C 5 V power and RGB 800×480 display. [Official Waveshare documentation](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3).
- Geometric reference: the user previously downloaded original 2023 `ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip` (SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`). Prior source-grounded STEP extract found a **106.106 × 68.268 × 16.906 mm** full-assembly axis-aligned *bounding box*, and actual STEP M2.5 standoff centres ~98 × 60 mm. All moving proxies below are rectangular fills of that assembly box, **not a 693-body accurate collision solid**.
- The 55° selected mounting pose projects the conservative box to **53.01 mm desktop Y**, while open underside hatch is **59.09 mm in Y**. In projection only, Y translations **−10.129 to −4.041 mm** would fit within the hatch. Nominal seated board proxy extends 4.041 mm beyond rear opening Y boundary. The X span of the board fits the 134 mm-wide opening.
- Full manufacturer 693-part STEP was **not imported into this 3D motion search**. Real screen standoff/thread orientation, glass interface, ribbon, solder joints, PCB cables, male USB-C body and antenna have not been verified in a final unit. Actual SKU and revision must be matched before finalising dimensions.

## A. Angled/translated underbody insertion check — performed

The source generator samples a deliberately limited **72-position grid**: Y shifts `[−10, −7, −4.5, 0]` mm, global-X pitch offsets `[−12, 0, +12]` degrees, and Z offsets `[−125, −110, −75, −40, −20, 0]` mm. It compares the conservative **full-module rectangular prism** against the **unchanged genuine V2 R5 case STEP**, with the hook-click underside cover removed.

- **24/72 poses** are free of collision in the conservative screen-box model, **all at Z = −125 or −110 mm, beneath the case**. Those far-out poses are expected and do not demonstrate passage through the underside hatch.
- The **48 trial poses at Z ≥ −75 mm** all have a positive box/case overlap. Lowest intersection samples were ~279 mm³ at Z=−75, ~208 mm³ at Z=−40, ~178 mm³ at Z=−20, and **689.22 mm³ for the nominal seated full rectangular prism**.
- A 3D prism is an intentionally *pessimistic proxy* (it fills empty spaces between actual board components). **Cannot conclude angled insertion is impossible**, nor claim a route is clear. 72 disjoint poses also do not define a continuous collision-free path or include a controlled rotation sequence. There is no hardware to test physically yet.

**Decision:** Do not enlarge the underside opening or split the case solely on this result. The 2D projection makes shifted ingress theoretically possible, but further accurate full-part geometry and real assembly motion must be demonstrated.

## B. Pre-screw screen to two slim, detachable mounting rails — CAD reference

The aim is to attach the Waveshare board to its carrier **outside the enclosure**, using its four manufacturer standoff positions, then secure the preassembled carrier inside with **two underside-accessible screws**. This could avoid approaching all four tiny PCB mounting screws inside the cramped case.

- Two experimental independent **STEP bar solids**, nominal **8.0 mm across X × 64.0 mm along face V × 2.8 mm normal-W thickness**. Each has two **Ø2.9 mm trial PCB through-holes** spaced **60 mm**, mounted on X≈12.05 and X≈110.05 (98 mm apart). The bars lie behind the board at the reference mounting datum, not across the front touch glass.
- Each bar includes a small *candidate* inward ear with a **vertical Ø2.9 mm trial mounting hole** at face V=41.8 mm, approximately X=22.05 and 100.05 mm. Trial 4 mm-diameter, 75 mm-long **vertical screwdriver shafts** from underneath had **0.00 mm³ overlap with the unchanged case** at both ear axes. This is a useful direction for further work, **not verified driver-bit/hand/screwhead space or fastening direction**.
- The two bars **intersect the existing case-mounted screen brackets by ~214.56 mm³ each** in their nominal final position. Therefore **these bars cannot be installed in the existing case as-is**; the existing four cantilevers would need to be replaced with a new case-side support/attachment arrangement. We intentionally did *not* delete them or alter the original shell before deciding what to replace.
- A preassembled board + bars increases the insertion swept volume relative to the bare screen. **A clear ingress trajectory for this larger assembly is not demonstrated.** No case bosses or screws joining the rails to the shell are designed yet, and there is no PCB-thread engagement/torque certification.

**Decision:** Trial carrier concept worth exploring, especially for screw serviceability, but **NOT a drop-in mounting kit or manufacturing-ready bracket**. The deliverable case+bar STEP reference names explicitly warn of clashes.

## C. Proposed next engineering iteration

1. **First, improve installation geometry evidence:** obtain the exact touch-version manufacturer STEP and work with selected PCB, display glass, standoffs and FPC as individual solids or a simplified faithful mesh rather than their filled bounding prism. Model a continuous approach along Y/Z with controlled screen pitch, and guard the front glass and port walls; only then certify or reject an insertion route. Compare the actual purchased board revision when available.
2. **If the route appears feasible:** build a separate (new filename) **carrier-friendly case** with **two accessible vertical mounting supports replacing the four old screw-arm pads**, a pair of captive receiving supports for the preassembled screen side rails, and a defined underside screw-head/tool channel. Preserve R5 exterior, left-side USB and hook-click V2 cover. Confirm the complete carrier-with-board can actually enter the opening and that rails/PCB/hardware do not clash.
3. **If not feasible:** test a *hidden split seam / removable front frame* alternative rather than repeatedly cutting the underside hatch. Keep it screwless externally if possible but do not hide needed structural hardware or serviceability constraints.
4. Before manufacture: confirm actual **M2.5** fastener screw head side, insertion depth, torque and retention, PCB corners, cable bend radii, Wi-Fi antenna keepouts, screen/touch firmware rotation, final supplier keycap skirt and print tolerances. Do not order print parts on the basis of the box geometry.

## Test and deliverable status

- **20/20 assistant-environment tests passed**: 15 standard-library reporting/guard tests and 5 CadQuery solid/STEP checks. In Windows without CadQuery and the optional unchanged V2 case STEP, expect **15 PASS / 5 SKIP**. No full-board/physical test has been performed.
- Two carrier-bar **actual STEP solids** exported, reopened as valid, plus **two reference STEP assemblies**: existing untouched case + candidate rails + 2023 bounding prism, and an illustrated staging pose at Y −7/Z −65 mm. **Reference assembly can show collisions by design.**
- Two comparative SVGs, two CAD-derived PNG previews and JSON sample data. Binary STEP assets distributed in a separate ZIP; GitHub stores generator, editable dimensions, tests and SVGs, not original 31 MB manufacturer model.
- Strict source state: previous `hook_click_latch_refinement_v2.py` and the prior case STEP files are not modified; this is a new *screen installation study*, not a new enclosure version.

## Windows PowerShell

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_screen_install_bracket_options.py -v
python mechanical\revB\cad\screen_install_bracket_options.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-Screen-Mount-Options"
Invoke-Item "$HOME\Downloads\SpotifyDesk-Screen-Mount-Options\carrier_bar_mounting_plan.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-Screen-Mount-Options\staged_entry_2d_projection.svg"
```

The optional complete CAD study requires CadQuery/Shapely, a local copy of the **exact pre-generated V2 hook-click case STEP** previously supplied in its own ZIP, and:

```powershell
$case = "$HOME\Downloads\SpotifyDesk-HookClick-V2\SpotifyDesk_R5_hook_click_v2_CASE.step" # change to actual extracted path
$env:SPOTIFY_HOOK_CLICK_V2_CASE_STEP = $case
python mechanical\revB\cad\screen_install_bracket_options.py --case-step $case --out-dir "$HOME\Downloads\SpotifyDesk-Screen-Mount-Options-CAD"
```

The script will **not** download or overwrite any prior case. STEP reference files can be inspected in FreeCAD without CadQuery.

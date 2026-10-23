# Rev B — experimental removable underside cover and screen supports

**Status (2026-10-23): CAD geometry generated and assistant-side tests passed. Not physically fitted, not approved to 3D print as a usable case.** User chose the **R5 rounded, physically rotated Waveshare 180°, USB-C on left, 4 mm media keycaps at rest** configuration. Keycap vendor printing/dimensions are still awaiting Tech Toppers' human reply. Older 2/4/6 mm models, original Rev B STEP/DXF/PDF, and original 4 mm CAD source remain untouched.

## Design choices and reason

The existing rounded R180 4 mm experimental CAD shell already contained a **rectangular opening in its underside** with no panel. This iteration closes **that underside opening** with a separate removable cover, instead of cutting away the upright rear wall. The underside approach retains the 156 mm envelope and offers tool access to wiring and rear-facing board screws. It is an **underside service hatch, not an entire vertical rear panel**, and the **LCD insertion path is not yet proven**.

### Underside cover (trial dimensions, mm)

| Feature | Geometry |
|---|---|
| Outer case | 156.0 wide × 83.093 deep × 106.107 high, R5 |
| Existing underside access opening | X=11.0…145.0, desk Y=12.0…71.093 |
| Separately removable cover | X=11.4…144.6, desk Y=12.4…70.693 |
| Nominal gap | **0.4 mm on each edge** (experimental, material/print-process dependent) |
| Cover depth | **2.0 mm**; underside Z=0.35…2.35 |
| Seat lip | Continuous annular support frame, 2.0 mm extending into hole, 2.5 mm over original rim, Z=2.35…4.65 |
| Four independent lid fasteners | Vertical axes through underside at X=18.5/137.5, Y=19.5/63.593 |
| Preliminary cover clearance holes | Ø2.9 mm for conceptual M2.5 screw through-hole |
| Preliminary attached case bosses | Ø8.2 mm, 9 mm tall from Z=2.35; **Ø2.0 mm pilot is placeholder**, not approved for screws or heat-set inserts |

Real structural bridges tie each screw boss to the existing underside shell/support lip. The cover is a **distinct B-Rep solid**, not attached to the case, and the exported STEP reports **0 mm³ overlap** between installed parts. No screw head recess, gasket, clasp, counterbore or threaded insert model is included. The practical screw choice and pilot hole sizes must be confirmed from actual fastener and printer datasheets. Avoid overtightening bare printed pilots.

### Touchscreen retention (manufacturer STEP-aligned, *provisional*)

The 2023 Waveshare manufacturer's 693-body STEP model included four components named **SMTSO-M2_5-4ET**, at centres corresponding to **98.0 × 60.0 mm**. After the agreed physical 180° rotation, our sloping-face X/V centres are:

- (12.05, 11.80), (110.05, 11.80)
- (12.05, 71.80), (110.05, 71.80)

The prototype creates **four cantilever support arms**, anchored to case face regions above and below the nominal **106.1 × 67.8 mm** display module projection. Each arm ends in an **Ø8.7 mm** support pad with a **Ø2.9 mm** provisional screw pass-through. Using the pre-existing **3.25 mm assumed glass installation inset**, the measured STEP standoff bodies end at W=15.75 mm, and the support-pad bearing face begins **W=15.85 mm** (0.10 mm reference gap); pad thickness is **2.8 mm**. W is inward, normal to the sloping display face—not desktop depth or vertical Z.

**Important:** The support arms/holes are geometrically attached to the case, but **this is not a proof of mating**. The exact motherboard revision, thread direction, standoff screw penetration, ferrules, nearby PCB/components/antenna/ribbon collision and screw-tool access have not been inspected against the *full fitted 693-solid STEP* plus USB/I2C mating cables. The manufacturer model measures **16.906 mm front-to-back overall**, so a simple front-board thickness number is not safe. Final mount should be checked in an assembly with real male USB plugs, cable routing, actual board revision and mounting hardware. Arms must not contact active components, antenna, glass or flex cables.

## Deliverables

New independent, reproducible source files (existing files not altered):

- `mechanical/revB/cad/rear_cover_screen_mount_study.py` — Python geometry/report generator; `--report-only` runs with standard Python, full STEP export requires CadQuery/Shapely.
- `mechanical/revB/cad/rear_cover_screen_mount_study.json` — experimental size/tolerance choices and caveats.
- `mechanical/revB/cad/test_rear_cover_screen_mount_study.py` — 16 regressions; **16 passed in assistant environment** with CadQuery, including independent STEP B-Rep reimport, case/cover single-solid validity, cover/case zero intersection, exact four through-holes, and the original base-case dimension checks. In a Windows environment without optional CAD packages, **four B-Rep tests skip**; 12 standard-library geometry tests still run.

The separate `Spotify_Desk_RevB_R5_4mm_Rear_Cover_Screen_Mount_Study.zip` contains:

1. New case with internal lid and screen mounts (`spotify_revB_R5_USBleft_4mm_case_with_mounts_EXPERIMENTAL.step`).
2. Separately removable bottom plate (`spotify_revB_removable_rear_cover_EXPERIMENTAL.step`).
3. Assembled case/lid/4 standoff targets (`spotify_revB_case_cover_and_screen_target_ASSEMBLY.step`).
4. Exploded removal view (`spotify_revB_rear_cover_exploded_ASSEMBLY.step`).
5. Underside and screen-mount SVG coordinate drawings, two CAD-derived images, geometry report, source/dependencies, regression tests and this document.

All STEP output sizes/validity tested assistant-side. **Do not treat the conceptual mounting bridge structure as print/screw approved.** Manufacturer original STEP/ZIP are not republished in this package or public source repository.

## Windows PowerShell validation

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_rear_cover_screen_mount_study.py -v
python mechanical\revB\cad\rear_cover_screen_mount_study.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Rear-Cover-Study"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Rear-Cover-Study\rear_cover_bottom_plan.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Rear-Cover-Study\screen_mount_front_plan.svg"
```

The **separately supplied STEP package** opens in FreeCAD even if Windows Python has no CadQuery installed. Full source regeneration (optional) from project root:

```powershell
python mechanical\revB\cad\rear_cover_screen_mount_study.py --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Rear-Cover-STEP"
```

## Remaining gates before physical manufacture

1. **Screen insertion route:** the display module is approximately 106.1 × 68.3 mm, but the bottom access opening's Y width is approximately **59.1 mm**. An angled installation motion might work, but the actual insertion trajectory and access to four rear screws **are not demonstrated**. This is a critical next mechanical study. Enlarging the hatch or separating the case's front/rear could be required.
2. **Real LCD collision check:** mate official 2023 STEP and real board if available, confirm pad orientation/threads, cable position, antenna and delicate glass/touch areas. Avoid relying only on clearance boxes.
3. **Fastener strategy:** specify real lid M2.5 heads, pilot/insert specs and printable material; decide whether the full panel requires countersinks, threaded inserts, thermal insert clearance, or sealing.
4. **USB-C and programming:** validate real male USB plug through LEFT opening, strain relief, plus deliberate USB-UART service/reflash access. Left-side trial slot has not been enlarged or validated here.
5. **MX/keycaps:** 4 mm rest height is approved as styling, but Tech Toppers' exact keycap dimensions and white-on-black production confirmation remain open. Avoid freezing the 19.2 mm wells until cap profile/skirt/travel is measured.
6. **Encoder and expander:** ensure rotary press still functions, retain safe electrical map and AW9523B startup/reset verification; neither electrically tested or mounted inside this model.

**Recommendation:** Visual-review the two CAD pieces in FreeCAD first, then prioritise **screen assembly/insertion and fastener tool reach** before treating a back plate as complete.

# Rev B — screwless slide-in bottom cover with screw-mounted touchscreen

**Status: separate experimental CAD reference, dated 2026-10-26. No actual lid, friction latch, print tolerances, or module fit has been physically tested.** User rejected the prior bottom panel's four screws as unnecessarily complex and requested a slide-in / slide-out cover. **Only the Waveshare screen supports retain candidate M2.5 fastener holes.**

## Design decision and mechanism

- **Preserved:** 156mm rounded/R5 outer shell, the physically rotated 180° Waveshare display arrangement (USB power on LEFT), 4mm raised-at-rest three media keys, volume knob bore, screen visible aperture, and four 98×60mm Waveshare fixing targets. Existing CAD and original four-screw cover variant are **not overwritten**.
- **Bottom lid:** independent **2.0mm** thick sliding plate, main body nominal **133.2 × 58.293mm**, with **0.4mm** clearance to the original 134 × 59.093mm underside opening in plan. The little central rear thumb tab sticks out by **0.8mm** past the case rear edge when fully inserted; three shallow grip grooves are only for fingernail purchase.
- **Rails:** captured in two continuous *left/right side tracks*. Each has an upper and lower retaining lip; 4 lips total. Nominal overlap beyond the lid's edge is **2.6mm** per side; lower lip top at case Z=0.30mm, lid Z=0.55…2.55mm, upper lip bottom Z=2.85mm (0.25mm lower vertical margin, 0.30mm upper margin). Rail outer portions fuse into the original shell's underside perimeter.
- **Slide path:** lid is inserted/removed toward **rear (+Y)**, passing through a real shallow rear-wall feed-through opening. The rear entry mouth ends at **Z=2.80mm**, and is open downward at the back so it does not leave an unsupported 0.3mm-thick rear-wall web. A short narrow rear pull tab lets fingers reach the plate despite the hatch ending ~12mm before the rear wall.
- **No bottom-cover screws, bosses, through-holes, loose magnets or tools.** The original bottom cover four-screw concept is retained only as a reference/rollback model.
- **Touchscreen:** manufacturer-referenced four M2.5 nominal bracket target holes remain in an unmodified screen-bracket design (98×60mm pattern). Their PCB/antenna/flex-clearance and screw insertion path are **unverified**, so the screen assembly cannot yet be treated as mountable.

### Important retained-design caveat: security vs convenience

**This prototype does not claim a proven click-lock or positive latch.** It is a geometrically captured, freely sliding cover with clearance. Real-world retention must be decided after a tolerance test: a short, releasable low-profile friction/detent feature can be added if it would otherwise creep out when the controller is picked up or tilted. Do **not** assume nominal 0.4mm gaps retain the lid by friction, or that the device can be used upside down without the lid sliding out. The final lock should not need tools or screws.

Similarly, the long entry slot in the rear wall may affect case stiffness and print strength; **the rail cross-section and rear wall must be print-tested.** It is not yet proven possible to insert the actual 68mm-high board via the 59mm underside opening; consider alternate initial assembly before fabrication. The right I2C and left USB mating harnesses, rear button sockets, antenna and standoffs are not in the sweep check.

## CAD validation achieved (assistant environment)

- **21/21 Python tests passed**, including actual CadQuery B-Rep solid construction and STEP re-import.
- Case and lid are **two independent valid solids**, not a shell with a blind slot. Nominal case width remains **156mm**.
- **0.000 mm³** volumetric overlap at fully inserted position. Verified lid can translate along +Y at **10 intermediate offsets from 0 to 82mm** without volume overlap in this idealized rigid model (see JSON results). **This is a sampled interference check**, not load, friction, surface finish or tolerance certification.
- Cover STEP is **undrilled** at all four *former* cover screw positions. Screen still has four candidate drilled support pads; source reports 98×60mm pitch.
- Delivered as separate source generator, JSON assumptions, tests, two SVG mechanical plans and **four STEP references** (body, cover, installed assembly, partially withdrawn assembly), plus visual previews. No raw third-party manufacturer STEP redistributed into GitHub.

## In the repository

- Generator: [`mechanical/revB/cad/slide_in_rear_cover_study.py`](../mechanical/revB/cad/slide_in_rear_cover_study.py)
- Geometry and pending-fit assumptions: [`mechanical/revB/cad/slide_in_rear_cover_study.json`](../mechanical/revB/cad/slide_in_rear_cover_study.json)
- Independent regression tests: [`mechanical/revB/cad/test_slide_in_rear_cover_study.py`](../mechanical/revB/cad/test_slide_in_rear_cover_study.py)
- Plans: [`slide_cover_underside_plan.svg`](../mechanical/revB/cad/slide_cover_underside_plan.svg) and [`slide_cover_rail_section.svg`](../mechanical/revB/cad/slide_cover_rail_section.svg)

The generated STEP geometry is available in a **separate chat ZIP**, not replacing any prior GitHub CAD or mechanical baseline.

## Windows verification (PowerShell)

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_slide_in_rear_cover_study.py -v
python mechanical\revB\cad\slide_in_rear_cover_study.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Sliding-Lid"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Sliding-Lid\slide_cover_underside_plan.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Sliding-Lid\slide_cover_rail_section.svg"
```

In the user's previous Windows environment, **four CAD-dependent tests may skip** without optional CadQuery/Shapely. That is expected and does not establish STEP validity on Windows. The separate conversation ZIP contains STEP exports validated in assistant's environment, viewable in FreeCAD without CadQuery.

## Next mechanical gates

1. **Choose a tool-free retention detail** (detent/small spring latch versus measured friction) and test a short print coupon for easy thumb-release and resistance to accidental withdrawal.
2. Determine whether the actual Waveshare module can be **inserted and fastened** through a realistically sized access opening before choosing complete shell assembly order. Screen screws should remain, bottom lid should remain screwless.
3. Inspect entry slot and rails for **minimum FDM wall thickness, printing supports/orientation, warping** and desk-foot clearance.
4. Verify screen, I2C/USB wires, encoder and caps do not occupy slider sweep space; verify actual 4mm cap shape and press travel once Tech Toppers confirms the cap profile.

**Not fabrication-ready and no user signoff to a physical latch mechanism yet.**

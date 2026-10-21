# Rev B — rounded, USB-left, three recessed MX media controls and volume knob

**2026-10-21. Design stage; experimental physical envelope. No manufacturing signoff or hardware purchase.** User visually reviewed the earlier rounded 180° USB-left shell and selected **rounded corners** and **USB on the left** as preferred design direction. Preserve the retained original Rev B sharp/R5 and prior rotated case references. The newly derived STEP shell/assembly in the chat ZIP is a *new exploration*, not the final model or the maker's component CAD.

## Front appearance and controls

- Maintain 156mm case width, 55-degree sloped panel, rounded **R5** exterior, physical Waveshare module rotated 180°, and the user's centred three 30mm-pitch media keys (X=31.05, 61.05, 91.05; V=91mm). Screen aperture remains aligned with the rotated board at X=13.33, V=17.09, 95.54×54.36mm. Existing USB-C1 left access slot remains a provisional cut.
- Three matching matte-black 1U MX-compatible caps with high-contrast **white previous ⏮ / play-pause ⏯ / next ⏭** legends. The vector masters (`previous_white_legend.svg`, `play_pause_white_legend.svg`, `next_white_legend.svg`) use original SVG polygon silhouettes on a transparent background. The seller must confirm white printing on black is possible and agree on symbol scale and profile before ordering. Not backlit.
- KZ0087-01 black aluminium knob provisionally shown at X=138, V=44, Ø15.1mm. Trial exterior knob height 8mm above face; shaft/nut, pushing the encoder and grub-screw alignment remain unverified.

## Recessed vs proud keycaps

**Proposed concept:** retain full-height plate-mounted Cherry-MX-style switches, but sink the **switch-retaining plate** behind the 3mm front case skin. Do **not** try to clip switches into the 3mm front wall or keep only the existing 14×14mm front apertures. Provide 19.2mm through-keycap wells at face and a separate *modelled* 1.5mm plate with 14mm MX cutout below it, reinforced with a 23.2mm external collar. Caps move inside wells. These are candidate sizes, not final print tolerances.

| Trial parameter | Value | Why / caveat |
|---|---:|---|
| Visible keycap width | 18.0mm | **ASSUMED**, typical ~1U; vendor-specific cap may differ. |
| Through-panel cap well | 19.2mm | 0.6mm *lateral gap per side* if 18mm cap; may vary with printed tolerances. |
| Well retaining-ring outside | 23.2mm | Leaves 3.6mm projected between last edge and nominal screen module lower edge. |
| Keycap visible top at rest | 2.0mm above panel | Low-profile *look*, not actually an MX low-profile switch. |
| Nominal MX total travel | 4.0mm | Trial full-height MX Brown/RGB linear; other MX switches can travel 3.7mm or less. |
| Keycap body depth | 8.0mm | **ASSUMED** external skirt/body, not a certified vendor model. |
| Plate top | 11.5mm inward from exterior | 1.5mm plate, nominal 14×14mm switch aperture; exact MX clip geometry must be validated. |
| Full-press cap top | 2.0mm *below* face | Well surrounds keycap throughout full travel; does not guarantee actual fit. |
| Full-press skirt-to-retention plate | 1.5mm | **Simplified** gap assuming cap 8mm deep; real housing/skirt/stem interference not modelled. |
| Assumed MX stem insertion | 3.3mm | Derived from an illustrative stem-tip position, not a measured chosen cap. |
| Volume knob | Ø15.1mm, height 8mm above face | Trial envelope, not full KZ0087 mount/shaft model. |

**Engineering distinction:** The front cap well is not the *switch* clip aperture. An actual Cherry-style MX flange is approximately 15.6mm across and clips into a roughly 14mm opening in an approximately 1.5mm plate. The earlier 3mm-thick face cannot be assumed to snap-retain a conventional MX switch. Cherry MX Brown advertises 4mm travel; Silent Red advertises 3.7mm. See original [Cherry MX datasheet](https://www.digikey.co.uk/en/htmldatasheets/production/57428/0/0/1/mx-series.html), [Cherry Brown](https://www.cherry.de/en-us/product/mx2a-brown), and [Cherry Silent Red](https://www.cherry.de/en-gb/product/mx2a-silent-red). The keycap profile and plate top datum **must be iterated** after choosing exact switch and cap models. The illustrated MX stem and cap underside are intentionally simplified and can intersect in ways a real fitted stem would not.

**Why not surface-mount with the cap fully proud?** Simpler to build but leaves much more visible sidewall height and may look like a small keyboard stuck onto a desk device. A recessed well presents a lower visible cap profile while still allowing the full mechanical stroke; it requires a deeper support well and more careful tolerances/print orientation. Neither arrangement has been physically confirmed.

## Sourcing three matching icon caps (UK)

1. **First candidate — [Krome Keycaps custom Cherry 1U PBT](https://www.kromekeycaps.com/products/create-your-own-custom-cherry-keycap)**. Listed £8 **each** (three ≈ **£24 plus postage** on Oct 21), individual UV-printed, MX-compatible, file upload of SVG supported, no backlighting. All three should use **the same Cherry profile row** (select the same row for each) and black plastic with white icons *if that exact colour combination is offered*. Cherry-profile keytops are sculpted, so check top-face angle.
2. **Alternative — [Krome custom OEM 1U PBT](https://www.kromekeycaps.com/products/create-your-own-custom-keycap)**. £8 each and MX compatible, typically taller/more sculpted than selected Cherry row; riskier for our recessed well until cap skirt geometry is known.
3. **Alternative UK custom maker — [Tech Toppers single custom keycap](https://www.techtoppers.co.uk/products/single-keycap-editor)**. Cherry-MX compatible 1U PBT dye-sublimation / custom icons; verify suitable dark cap + high-contrast white legend with supplier before paying (dye sublimation is usually better on light cap materials). No price claim without current checkout.

**Lower-priced candidates found after user feedback:** [Mechbox four blank 1U MX PBT caps £1.56](https://mechbox.co.uk/products/blank-wasd-keys) + shipping (symbols separately); [Tech Toppers four custom MX PBT WASD caps £14.95](https://www.techtoppers.co.uk/products/wasd-custom-keycaps-editor) + £3.95 standard UK delivery ≈£18.90, with uploaded artwork (confirm black plastic/white legend compatibility before ordering). Krome three custom single Cherry caps £24 + delivery is **not required**. No confirmed cheaper off-the-shelf matching three-icon pack was found with verified MX stem, profile and UK delivery. **Do not order custom caps yet**, because final case recess must be based on the actual cap geometry, profile, housing and 3D-print fit test. The SVGs supplied are *printing drafts*, not seller-approved print templates.

## Side-by-side raised-height option (illustrative only)

User requested a visual comparison of the **2mm** above-surface-at-rest recessed prototype and a **6mm raised-at-rest** appearance on the same rounded USB-left unit. A comparison image was generated. **6mm is not a newly engineered shell:** the nominal 4mm stroke, cap skirt, switch engagement, well/plate placement and return clearance must be recalculated after picking real cap profile and user preference. Original 2mm geometry stays checked in unchanged.

## Generated independent design assets

- [`mechanical/revB/cad/media_controls_fit_study.py`](../mechanical/revB/cad/media_controls_fit_study.py) — stdlib-only JSON/SVG/symbol preview mode; optional CadQuery STEP generation for a **new R5 rotated-180** trial shell with 3 collared keycap wells and internal 1.5mm switch-retention plates, plus coloured assembly with nominal cap/switch/knob envelopes.
- [`mechanical/revB/cad/keycap_mount_assumptions.json`](../mechanical/revB/cad/keycap_mount_assumptions.json) — candidate sizes, height/stroke and reference supplier link.
- [`mechanical/revB/cad/test_media_controls_fit_study.py`](../mechanical/revB/cad/test_media_controls_fit_study.py) — **15 assistant-environment tests passed**, including two real CadQuery solid generation and STEP reimport checks. **User Windows validation 2026-10-21: 13 passed, 2 skipped** because optional CadQuery/Shapely unavailable; both SVG drawings generated and opened. Assistant-side 15/15 including B-Rep checks passed separately.
- Three reusable vector legend masters under [`mechanical/revB/keycaps/`](../mechanical/revB/keycaps/) (previous, play_pause, next), with transparent backgrounds and white fills, for potential custom ordering.
- A separate conversation ZIP contains the rendered PNG/SVG front layout, two-state schematic MX section, nominal cap and knob STEP assembly, new R5 shell STEP, JSON assumptions and source + tests. The generated STEP binaries and manufacturer original STEP **are not checked into the public GitHub repo**. A photorealistic visualization is *illustrative only*; use the source output for dimensional checks.

## Windows PowerShell

From a pulled repo root (no CAD installation required for this run):

```powershell
python -m unittest discover -s mechanical\revB\cad -p test_media_controls_fit_study.py -v
python mechanical\revB\cad\media_controls_fit_study.py --report-only --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Media-Controls"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Media-Controls\media_controls_front.svg"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Media-Controls\mx_recess_section.svg"
```

For local regeneration of the STEP parts, CadQuery + Shapely are necessary, but the chat ZIP contains the already built STEP files for FreeCAD viewing.

## Successor three-height experimental STEP alternatives (2026-10-21)

The user requested three separate **actual CAD designs at 2, 4 and 6mm rest cap height** after seeing the style comparison. [The new parametric three-height CAD study](HARDWARE-REV-B-KEYCAP-HEIGHT-CAD-COMPARISON.md) supplies six STEP files separately in a conversation ZIP: each height has an R5 rounded case and cap/knob assembly. The retained original 2mm model remains unchanged. As cap height increases, the internal 1.5mm MX retaining plate moves outward from 11.5mm to 9.5mm to 7.5mm inward W; nominal stem-tip engagement and 1.5mm full-stroke skirt-to-plate gap are held equal by arithmetic, **not physical validation**. The new test suite passed 20 cases assistant-side including CadQuery roundtrip; Windows validation and user choice pending.

**Later decision (2026-10-21):** user selected **4mm raised caps**, with plate top W=9.5mm, out of the actual three-height STEP reference designs. This original 2mm experimental document is now a historical geometry baseline. Exact cap supplier is pending [purchase- and profile-specific verification](KEYCAP-FINAL-SHORTLIST.md); do not re-label the 2mm file as a 4mm CAD shell.

## Before print / purchase

Confirm (1) black 1U cap width, skirt depth, cross-stem socket depth and print suitability with manufacturer; (2) the exact MX switch and its real actuation/total travel and flange + clip retention geometry; (3) cap skirt clearance against the entire switch housing through downstroke, not just plate; (4) integrated 1.5mm printed plate strength/snap reliability and independent support/PCB soldering; (5) case interior near 98×60mm Waveshare standoffs, rear component depth, USB-C cable, I2C, antenna and chin; (6) encoder M7 nut, rotary shaft, knob travel, and grub-screw service; (7) real full case lid, screws and print clearances; (8) actual ESP32-screen/touch 180° firmware. No hardware purchased or print-ready files generated.

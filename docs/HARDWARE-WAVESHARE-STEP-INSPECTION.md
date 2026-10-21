# Rev B — official Waveshare STEP model inspection (manufacturer reference)

**2026-10-21. Status: manufacturer's assembled 3D model parsed and measured; provisional enclosure comparison; NOT physical fit or manufacturing signoff.** This corrects the *front/back viewing orientation* in older Rev B studies. Neither of the original sharp or R5-rounded 156 mm STEP enclosure variants has been changed.

## Source and integrity

- User supplied Waveshare's `ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip` from the official documentation and downloaded it on Windows with `scripts/inspect-waveshare-3d-reference.ps1`.
- SHA-256 (rechecked on the user-uploaded file in the assistant environment): `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`.
- ZIP: **5,677,592 bytes**; one `esp32-s3-touch-lcd-4_3.stp`: **31,338,066 bytes**. ZIP CRC test passed.
- STEP header: `ESP32-S3-TOUCH-LCD-4_3_ASM`, PTC Creo Parametric, timestamp **2023-12-13**. STEP read with OpenCascade 7.x / OCP and the XCAF assembly tree: **693 solids**. Model geometry uses millimetres.
- Exact source ZIP and its 31 MB STEP are deliberately **not included** in the public repository. We have stored extracted *part names and axis-aligned measurement boxes* only in [`waveshare_step_reference.json`](../mechanical/revB/cad/waveshare_step_reference.json). Continue retaining the official file locally. Confirm board revision against a purchased SKU 25948 eventually.

## Actual CAD geometry (global model XYZ axes, mm)

| Named part in actual STEP | X min…max | Y min…max | Z min…max |
|---|---|---|---|
| Complete assembled model | −53.003…53.103 | −36.482…31.786 | −12.103…4.803 |
| Touch-glass `43H-800480-TP` | −53.000…53.100 | −36.388…31.530 | −4.250…4.800 |
| PCB body `BOARD` | −52.962…53.062 | −36.482…31.543 | −3.703…−2.097 |
| USB `TYPE_C1_ASM` | 45.145…52.856 | −6.197…3.385 | −7.001…−2.839 |
| USB-UART `TYPE_C2_ASM` | 45.275…52.986 | 13.772…23.355 | −7.001…−2.839 |
| Four-pin peripheral connector `HP2_0-4PIN-00` | −52.423…−47.423 | −5.738…4.262 | −12.100…−2.450 |

The whole model has an overall bounding-box extent of **106.106 × 68.268 × 16.906 mm**, which is not the same as an uninterrupted 16.906 mm-thick slab. It includes glass, board, surface-mount parts and rear connectors. The front glass is toward **+Z**; the PCB and sockets extend toward **−Z**.

Four `SMTSO-M2_5-4ET` standoff-model instances have centre pitches **98.000 mm horizontally × 60.000 mm vertically**, matching earlier drawing estimates. Their modelled round external envelope is about **5.5 mm diameter**. The exact real tapped bore, screw-length allowance, washer clearance and vendor revision are not validated; "M2_5" is a CAD component-name designation, not independently measured thread proof.

## Critical orientation correction

**Front of display = looking towards its positive-Z glass face**; from there **+STEP X is front-right**.

| Connector | Manufacturer STEP front view | Location on our Rev B 156 mm front face |
|---|---|---|
| USB Type-C1 (manufacturer rear board label USB) | **RIGHT** | X ≈106.145…113.856 mm, V ≈36.145…45.727 mm |
| USB Type-C2 (rear board label UART) | **RIGHT**, above USB | X ≈106.275…113.986 mm, V ≈16.175…25.758 mm |
| Four-pin peripheral header (I²C H7, consistent with manufacturer board diagram) | **LEFT** | X ≈8.580…13.580 mm, V ≈35.268…45.268 mm |

Manufacturer rear-view PCB photographs are mirrored relative to the **front of the display**: they show USB at image left and I²C at image right. The source STEP, when viewed from the **front of the glass**, puts USB at the right and I²C at the left. Earlier `fit_audit.py` / `internal_packaging.py` deliberately represented a *hypothetical reversed* I²C-right / USB-left layout. **Do not silently rely on their connector sides for this actual manufacturer board.** They remain useful archived hypothetical-envelope tools; this newer inspection is the correct orientation-specific reference.

Original manufacturer documentation: [Waveshare ESP32-S3-Touch-LCD-4.3](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3) and [its hardware resource files](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Resources-And-Documents).

## Alignment to Rev B and what it means

To compare without editing the case, the measured **touch-glass outer bbox** is mapped to existing front-face origin (X=8, V=8), with front glass W=0 along the face normal. This is a **chosen registration datum**, not a validated structural mounting offset; top/rear shell needs an actual flush/recessed decision. Display centring and MX key positions have not been changed.

- **USB Type-C1 housing to nominal encoder-body X gap:** **17.544 mm**. Encoder nominal body assumed 13.2 mm across, centre X=138,V=44 and inward W=3.3…18.1 mm. The installed encoder terminals/shaft/nut/mount may differ.
- **I²C four-pin housing to nominal inner-left wall X gap:** **5.577 mm** (outer side wall X≈0…3 mm). Modelled PH bare connector has **no mating cable**.
- **Complete STEP back extent from front glass:** **16.906 mm**. Previous simplistic LCD body assumption was 6.8 mm deep from W=3.3 (plus surface offset). The real assembled STEP has rear components reaching farther inward; LCD standoffs, cable routing and the true enclosed-space cross-section should be revised *after* selecting a mounting datum.
- **Four mount pattern centres:** approx 98 × 60 mm; available but not signed off for complete screw/support construction.

### Provisional *cable-extension* scenarios only

These extend the **measured bare socket bounding boxes** directly outward in X. Their V and inward-W bounds are copied from the socket itself; real mating plug shape, wire bend and port access may be substantially different.

| Trial mating-cable extension beyond socket body | Simplified result |
|---|---|
| USB-C1, 14 mm towards right | No assumed encoder-body box intersection; X projection remains 3.544 mm short of encoder body. |
| USB-C1, 20 mm towards right | **2.456 × 8.327 × 4.162 mm** trial box intersection with assumed encoder body. Not proof of physical collision. |
| I²C, 6 mm towards left | Reaches theoretical X=2.577 mm; **0.423 mm** into the nominal X=3 mm inner wall. Left service cutout or cable redirection may be possible. |
| I²C, 10 mm towards left | **4.423 mm** beyond nominal inner wall; may cross the outside side-plane, depending on plug geometry. |

Two USB-C sockets are physically present but are **not necessarily interchangeable in boot, programming, power-entry, or flash workflows**. Manufacturer labels distinguish USB and USB-to-UART. We must still decide which to expose for everyday power and for servicing before placing cutouts.

## Reproducible tools (no STEP redistribution)

- [`waveshare_step_reference.json`](../mechanical/revB/cad/waveshare_step_reference.json) contains the original OCCT-imported model bounds, labels, source provenance and coordinate sign conventions. These are measurements, **not a manufacturer STEP substitute**.
- [`manufacturer_fit_compare.py`](../mechanical/revB/cad/manufacturer_fit_compare.py) is pure Python standard library; reads checked-in `dimensions.json` and extracted reference measurements, makes the correctly oriented front-view SVG and a machine-readable report. It never edits the original case or downloads the STEP.
- [`test_manufacturer_fit_compare.py`](../mechanical/revB/cad/test_manufacturer_fit_compare.py): **10 regression tests passed in the assistant environment** covering manufacturer STEP extents, correct connector sides, mount pitch, optional W seating offset, hypothetical cable intersections, and no false physical-fit claims. **Windows user test pending.**

### Windows PowerShell

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
python -m unittest discover -s mechanical\revB\cad -p test_manufacturer_fit_compare.py -v
python mechanical\revB\cad\manufacturer_fit_compare.py --out-dir "$HOME\Downloads\SpotifyDesk-Waveshare-STEP-Comparison"
python mechanical\revB\cad\manufacturer_fit_compare.py --usb-reach-mm 20 --i2c-reach-mm 10 --out-dir "$HOME\Downloads\SpotifyDesk-Waveshare-STEP-LongCables"
```

Open the exported `waveshare_step_front_overlay.svg` in a browser. Orange = USB housings; aqua/green = I²C four-pin housing; yellow = source-model mounting standoffs; white keys and dark rotary represent the **existing Rev B design**. This drawing displays *measured socket-body rectangles*, not their unmodelled mating plugs.

## Alternative 180° physical board orientation

The user proposed rotating the *complete front-facing module* by 180° in the sloped face, leaving its glass outward. This would move the **main USB-C and USB-UART to the LEFT** and **four-pin H7 I2C to the RIGHT**. It could be preferable for an externally exposed power port away from the encoder, though a deliberate left side-wall USB port/tunnel is still necessary. The nominal visible LCD aperture moves **+4.74mm in V** after rotation due to asymmetric front bezel, and display/touch firmware rotation is untested. Compare both options in the [physical-orientation report](HARDWARE-WAVESHARE-ROTATION-180-STUDY.md); no case modifications or final orientation decisions yet.

## Remaining design and engineering gates

1. Determine **USB-C1** realistic plug and strain relief size and potential side/rear access corridor. Its V interval overlaps the trial encoder body; investigate orienting plug into case depth, right-angle harness and alternate encoder/USB V placement before making shell wider.
2. Determine **H7 I²C** factory HY2.0 4P mating plug and bend geometry (the STEP only has the bare socket); allow a deliberate left-side slot or route inward without cutting through the enclosure side wall.
3. Establish a real screen-front mounting datum and design standoff bosses/bore/counterbore/cable depths; the 16.9 mm *overall STEP depth* is not an assembly-space tolerance. Include USB-C2 for service/debug access as necessary.
4. Keep the manufacturer raw STEP offline until verified against actual purchased touch SKU 25948 hardware and redistribution terms. Use it for local fit review where licences permit; do not commit raw 31MB third-party CAD or overwrite established sharp/R5 case STEP.
5. Once the user reviews this reference overlay and strategy, develop **separate Rev B fit-iteration variants** for either one/both exterior styles; keep 156mm face and centred 3-MX keys as baseline unless geometric evidence warrants an explicit change.

**Status:** the manufacturer's bare board now has a meaningful spatial reference, but the physical encoder/knob, mating cables, mounting hardware and true cable path still remain assumptions. No manufacture-ready CAD, no hardware ordered.

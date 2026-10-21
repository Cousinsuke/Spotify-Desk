# Rev B — Physical fit review and measurement gate

**2026-10-21. Status: engineering review, 2D calculations and printable test coupons; NO verified physical assembly.** Keep both existing sharp and R5 rounded STEP variants and the **156 mm external width unchanged** until user review/actual measurements. This work does not revise either original STEP case.

## Verified manufacturer / supplier reference dimensions

- **Waveshare ESP32-S3-Touch-LCD-4.3, touch SKU 25948:** total display module 106.1 × 67.8 mm; rear board mounting centres nominal 98 × 60 mm. Manufacturer photo/dimensional drawing shows right-edge I2C and other connectors, left-side USB/UART USB-C, and rear wiring/flex. Exact right-edge mating plug protrusion, bend radius, screw bore and assembled Z clearance are **not** specified here. Source: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3 ; https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/manual/ESP32-S3-Touch-LCD-4.3-Sch.pdf (page 3).
- **Adafruit PID 377 / Bourns PEC11-4215F-S24:** nominal encoder body 13.2 × 13.2 mm (excluding solder terminals), M7×0.75 bushing, **LB=5 mm** for the 15 mm L1 shaft version, **7 mm shaft beyond bushing**, nominal 0.5±0.2 mm axial switch travel. Physical assembly, washer, nut thread engagement and KZ0087 grub screw / push-click still need test. Source: https://www.adafruit.com/product/377 ; https://cdn-shop.adafruit.com/datasheets/pec11.pdf (page 2).
- **KZ0087-01:** body Ø15.1 mm; 6 mm round/grub-screw shaft bore, nominal 6–12.4 mm insertion. D-shaft orientation and axial travel need testing. Source: https://knobzone.co.uk/products/kz0087
- **Standard Cherry MX-type plate mounts:** nominal 14 × 14 mm square aperture and around 1.5 mm local plate thickness, but the owned switch model/clip design is **unknown**; a 3 mm case face cannot be assumed to engage clips as intended. Source: https://www.digikey.co.uk/en/products/detail/cherry-americas-llc/MX1A-E1NN/CH196-ND/40084 ; https://www.digikey.co.uk/en/htmldatasheets/production/57428/0/0/1/mx-series.html .

## Revision B CAD datums retained

- Sloping 156 × 110 mm face, 55°; front X right, V down slope.
- LCD module origin (8,8), outer X=8…114.1 mm and V=8…75.8 mm.
- MX centres X=31.05, 61.05, 91.05, V=91; mathematical display centre 61.05 mm; nominal 18 mm keycap tops V=82, giving **6.2 mm frontal gap** from LCD full lower module edge.
- Knob (138,44), Ø15.1 mm; encoder nominal 13.2 mm body with X=131.4…144.6 mm (pins excluded); 3 mm wall assumed.
- Pure X projection from LCD right edge to encoder body left edge is **17.3 mm**. This is an upper bound on any corridor extension *before* a design margin, and **not a measured cable clearance**.

## Parametric lateral cable scenarios

The 14 mm corridor from Rev B is **only a hypothesis**, not from Waveshare; the nominal **2 mm safety guard is a trial design target**, not a rated manufacturing limit. No connector's true V location, cable bend, depth or wire exit is established. The script cannot detect actual 3D collisions.

| Assumed extension beyond LCD right | Projected remaining gap to encoder body | Meets trial 2 mm guard? | Case width if knob and outer right wall shift together |
| ---: | ---: | :---: | ---: |
| 14 mm | 3.3 mm | 2D yes, physical unknown | 156.0 mm |
| 17 mm | 0.3 mm | No | 157.7 mm |
| 20 mm | −2.7 mm | No | 160.7 mm |
| 25 mm | −7.7 mm | No | 165.7 mm |

**No size change is approved by this table.** The 160.7mm scenario would only be relevant *if* the user measures a connector+wire envelope extending 20mm into the knob's V/Z space; without that 3D intersection it may not require an increase at all. Alternatives include rotating/using a right-angle harness, shifting cable routing in Z, moving knob V, or changing layout after measurement.

## Fit-test tools (reproducible, no binary dependencies committed)

- [`cad/fit_audit.py`](../mechanical/revB/cad/fit_audit.py) reads existing `dimensions.json`, reports multiple cable scenarios and can export a clearly marked illustrative SVG. Requires only Python 3 standard library.
- [`cad/fit_coupons.scad`](../mechanical/revB/cad/fit_coupons.scad) creates **five 24×24 mm detached sample panels**, two MX (14.0/14.2 mm square at 1.5 mm thickness) and three encoder variants (7.0/7.3 mm bore, 3.0/1.5 mm thickness). Print these samples instead of committing the final shell before measuring real parts.
- [`cad/test_fit_audit.py`](../mechanical/revB/cad/test_fit_audit.py) checks centred keys, original 3.3mm calculation, 20mm enlargement contingency, parameter guards and explicit no-physical-verification labelling. **Five unit tests passed locally**, and OpenSCAD rendered the coupons STL without CSG errors; this does **not** imply parts were printed or tested.

### Windows PowerShell (from repository root)

```powershell
python mechanical\revB\cad\fit_audit.py
python mechanical\revB\cad\fit_audit.py --cable-mm 20 --svg "$HOME\Downloads\revB_fit_overlay.svg"
python -m unittest discover -s mechanical\revB\cad -p test_fit_audit.py -v
# If OpenSCAD is installed and on PATH:
openscad -o "$HOME\Downloads\Spotify_Desk_RevB_fit_coupons.stl" mechanical\revB\cad\fit_coupons.scad
```

## Measurements needed to upgrade CAD from study to real fit

1. **Screen and connectors:** Take direct photos with a ruler/calipers beside right H7 I2C header with factory cable fully seated; measure extension beyond 106.1mm module edge and cable bend radius, V band and rear-plane depth. Verify both USB-C plug/port access, SD, antenna and pin-1 orientation.
2. **LCD mounting:** Measure actual rear screw hole diameters, stand-off heights, wiring and screw-head clearance. Manufacturer nominal 98×60 pitch alone is insufficient.
3. **Three MX switches:** Identify model, keycap size/height, whether plate-mount or PCB-mount, mounting clip thickness and rear pin/wire envelope. Test both coupon square sizes and record which snaps securely.
4. **Encoder and knob:** On the actual PID 377 + KZ0087, test the 7.0 and 7.3mm holes, 1.5/3mm plate thicknesses, retained washer/nut and room for push-click travel. Confirm press action while grub screw is engaged; check terminals and panel-side washer.
5. **Case internal support:** Once component Z dimensions exist, add real display bosses, mechanical reinforcement behind locally thin MX clips, left USB-C access, cable retainers, input-expander supports, bottom-hatch hardware and true B-rep component clash checks.
6. **Electrical safety:** Before wiring the AW9523B, separately validate voltage selector, connector pin ordering and expander reset/startup as recorded in `HARDWARE-ELECTRICAL-REVIEW.md`.

**Gate:** do not call current Rev B STEP printable/production-ready; only cut/print final enclosure after real component measurements, 3D clearance checks and a user's physical fit test.

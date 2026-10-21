# Rev B — Rotate the Waveshare module 180° to expose power USB on the left?

**Status 2026-10-21: feasible design candidate, not selected or fabrication approved.** User proposed physically turning the **whole assembled Waveshare touchscreen board** 180° in the plane of the sloped case so USB is on the **left** rather than next to the volume encoder; software would compensate the upside-down image. This is different from flipping the board front-to-back: its glass **still faces the user**. The existing sharp/R5 156 mm Rev B case STEP files have not been modified.

## What is confirmed and what is proposed

- **Vendor-supported:** Waveshare original ESP32-S3-Touch-LCD-4.3 has **5 V USB-C power**, 800×480 RGB LCD and capacitive touch; one Type-C is the direct **USB** interface and another marked **USB TO UART** is intended for flashing/serial diagnostics. The manufacturer's guide explicitly distinguishes these ports. Do not assume they are interchangeable for charging, powering or development operations without checking the schematic and actual board.
- **From uploaded official STEP:** USB-C1/C2 are on **front RIGHT**, H7 four-pin I²C socket on **front LEFT**, nominal module glass 106.1×67.8 mm, four PCB standoff positions on 98×60 mm pitch. See [STEP inspection](HARDWARE-WAVESHARE-STEP-INSPECTION.md). Product version still needs confirmation against exact touch SKU 25948 when purchased.
- **Proposed:** rotating all hardware 180° around its front-plane centre swaps front left/right socket positions but leaves nominal outer glass footprint and hole pitch unchanged. Its asymmetric visible LCD bezel also rotates, and the case's aperture must follow it.
- **Not implemented:** ESP32 firmware/display rotation, touch-coordinate transform, power-plug opening, wire management, new mounting supports or any edit to current B-rep case.

## Measured-model comparison, same Rev B X/V/W datums

Local X grows to the viewer's right; V down the inclined front surface, W inward from the glass. Original touch bounding rectangle continues to start at X=8,V=8 and the existing 3 media-key centres **31.05/61.05/91.05 mm** at V=91 are unchanged. The encoder also remains centred (138,44) mm, Ø15.1 nominal.

| Check | Physical original 0° | Proposed physical 180° |
| --- | ---: | ---: |
| Main Type-C USB | Front **RIGHT**, X=106.145…113.856 | Front **LEFT**, X=8.244…15.955 |
| Secondary USB-to-UART | Front **RIGHT**, V=16.175…25.758 | Front **LEFT**, V=58.042…67.625 |
| Four-pin H7 I²C | Front **LEFT**, X=8.577…13.577 | Front **RIGHT**, X=108.523…113.523 |
| Nominal left-side socket to X=3 inner wall | I²C: **5.577 mm** | Main USB: **5.244 mm** |
| Nominal right-side socket to X=153 inner wall | Main USB: **39.144 mm** | H7 I²C: **39.477 mm** |
| Right-side socket to encoder body in X | USB: **17.544 mm** | I²C: **17.877 mm** |
| Assumed 14 mm USB mating envelope / 6 mm I²C envelope | Left I²C crosses 3mm inner-wall plane by 0.423mm | Left USB crosses 3mm inner-wall plane by **8.756mm** |
| Nominal *visible* pixel-window origin X,V | (13.23, **12.35**) | (13.33, **17.09**) |
| Visible window shift relative to original (X,V) | (0,0) | (**+0.10, +4.74 mm**) |
| Nominal visible window bottom to nearest 18mm keycap top | **15.29mm** | **10.55mm** |
| Mounting centre pitch | 98×60mm | 98×60mm |

The 14 mm / 6 mm *mating cable lengths are trial approximations*, not actual manufacturer dimensions. In both default orientations the simple encoder-body prisms show no collision with these assumed cable prisms. A trial **20mm right-I²C projection** after rotation can intersect the encoder-body envelope; this is a geometric warning, not proof of failure. The screen standoff **hole locations** may rotate but their rectangular pitch stays the same; the shell still needs hardware detail.

**Power exposure:** in 180° orientation, a conventional straight USB plug could extend beyond the left inner-wall line. That is not automatically a defect: the design would need a deliberate **left-side USB tunnel/aperture** so the plug can be inserted from outside. Other strategies include a compact right-angle male USB-C inside and an external panel-mounted female connector; all need physical envelope and power checks. The USB-C main socket is still recessed from the case's outer left edge (approx 8.24 mm from the X=0 plane), so a hole drawn exactly at the bare socket may not be enough for insertion/grip. UART/debug accessibility, antenna exclusion, safe USB-C power entry and bottom-hatch access remain open.

## Display and touch rotation

The ESP32 RGB screen can be driven with a UI orientation transform, but this project has **no actual ESP32 firmware yet** and the exact driver path has not been proven. The Waveshare examples use LVGL with an ESP32 RGB LCD and GT911 touch controller. Depending on the specific ESP-IDF/LVGL port and performance path, rotating every pixel could require framebuffer/display-driver support; 180° is conceptually easier than swapping width/height but do **not** claim a working rotation without a bench test. Also rotate the **touch coordinates**, ideally in the touch input driver, to preserve tap locations (pixel-space conceptual formula at 800×480: `(x',y')=(799-x,479-y)`). Calibrate orientation and any edge offsets on the real part.

Because the visible LCD has **4.35 mm top and 9.09 mm bottom** offsets in the original physical orientation, turning the module 180° swaps these bezels. The *existing case aperture* is in its old location. It must move approximately **4.74mm down V** (and **0.10mm right X**) for the rotated assembly; doing only software image rotation will **not** compensate the physical cutout. The nominal visible-to-keycap separation would still be about 10.55mm, but check real cap/switch protrusions and shell structure when moving the cutout.

Manufacturer references: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3 ; https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use ; ESP-IDF RGB LCD software orientation https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/lcd/rgb_lcd.html . No hardware was used to verify programming or display speed.

## Study tools

- [`orientation_180_study.py`](../mechanical/revB/cad/orientation_180_study.py) reads the same checked-in manufacturer STEP reference boxes as the existing normal-orientation comparison and computes both orientations. It uses **standard Python only**; no CAD binaries or file downloads needed.
- [`test_orientation_180_study.py`](../mechanical/revB/cad/test_orientation_180_study.py): **12 local Python regression tests passed**, covering 180° coordinate mapping, physical USB/I²C swap, aperture shift, hole pitch, case/button preservation, simplified plug/encoder alternatives, a conceptual touch rotation and honest warnings. No user Windows validation yet.
- Run this from repo root in Windows PowerShell:

```powershell
python -m unittest discover -s mechanical\revB\cad -p test_orientation_180_study.py -v
python mechanical\revB\cad\orientation_180_study.py --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Orientation-Study"
python mechanical\revB\cad\orientation_180_study.py --usb-reach-mm 20 --i2c-reach-mm 20 --out-dir "$HOME\Downloads\SpotifyDesk-RevB-Orientation-LongCables"
Invoke-Item "$HOME\Downloads\SpotifyDesk-RevB-Orientation-Study\orientation_180_comparison.svg"
```

## Design decision gate

**Recommendation for investigation:** Try the **physical 180° board orientation** as a separate Rev B fit-iteration, because left-side USB power entry could avoid a close-to-encoder external cable. Keep both 156mm exterior styles and the existing original-mounted reference unchanged. Before choosing this as final, prototype or model a left-side port tunnel/USB harness, verify right-side H7 wiring does not collide with encoder terminals, reposition the LCD *visible* aperture, preserve UART/BOOT/RESET servicing and Wi-Fi antenna clearance, and verify firmware LCD+touch rotation when the board is purchased. It is **not yet a user-confirmed mechanical design decision**.

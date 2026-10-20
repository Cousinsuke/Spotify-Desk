# Phase 6 — Proposed hardware shortlist (UK)

**2026-10-20 — user-selected provisional trio, not a purchase approval.** User chose Waveshare **25948**, Adafruit **377** and Waveshare AW9523B **22132** for pre-purchase verification. Research cost examples still apply; electrical wiring, CAD and firmware unvalidated. See [pre-purchase verification](HARDWARE-PRE-PURCHASE-CHECK.md). The confirmed interaction mapping is: **three MX keys** (previous, play/pause, next); rotary encoder clockwise/anticlockwise = volume, **integrated press** = PC/Wi-Fi mode. This is **six digital contact signals** including encoder A/B. Existing Phase 5.2 desktop code remains unchanged.

## Preferred compact prototype

| Component | Specific part | UK example price | Reason / caveat |
| --- | --- | ---: | --- |
| ESP32-S3 + touch display | Waveshare **ESP32-S3-Touch-LCD-4.3**, manufacturer **SKU 25948**, The Pi Hut WAV-25948 | **£31.70** | 800×480 touch; ~106.1×67.8 mm board; 270 cd/m²; 16 MB flash / 8 MB PSRAM. Be sure to select TOUCH, not no-touch 30493. |
| Knob with integrated push | Adafruit **Rotary Encoder + Extras PID 377**, The Pi Hut ADA377 | **£4.40** | 24-detent rotary, built-in momentary switch, 6 mm D shaft, supplied soft-touch knob; Adafruit-linked 450-BA761 *family drawing* indicates **~16 mm outside diameter**, close to 18 mm mockup; confirm actual supplied knob before CAD. |
| 16-input expansion | Waveshare **AW9523B IO Expansion Board SKU 22132**, The Pi Hut WAV-22132 | **£4.80** | Nominal I2C address **0x58**; ~38×23 mm, 3.3/5 V capable. Needs external bias resistors on switch/encoder contacts **and validated boot-time output/short-circuit protection**, and its 6-wire connector is NOT interchangeable with the display's four-wire I2C connector. |
| Keys | **3 owned MX switches**, plus 1u keycaps if not already available | Already owned switches | Use for previous/play-pause/next. |

**Base parts subtotal: £40.90**, before shipping, power/USB cable, cables/adapters, six external resistors, 1u keycaps if missing, solder/perfboard, fastening and printing. Values are observed example UK prices, not guaranteed stock quotes.

- Screen: https://thepihut.com/products/esp32-s3-4-3-touch-display-dev-board-800x480
- Encoder: https://thepihut.com/products/rotary-encoder-extras
- Waveshare AW9523B: https://thepihut.com/products/aw9523b-io-expansion-board

### Optional appearance change

- Adafruit 20 mm black aluminium knob, The Pi Hut ADA5527: **£2.90 observed**, but listing showed sold out. Fits a 6 mm shaft using set screw. Slightly larger than user's 18 mm concept; MUST verify push actuation is not obstructed by faceplate, and shaft fit, encoder push travel and knob weight.
- https://thepihut.com/products/anodized-aluminium-machined-knob-black-20mm-diameter

## Brighter-screen alternative

The **Waveshare ESP32-S3-Touch-LCD-4.3B**, **SKU 27848** (BARE, not factory-case SKU 28141) is rated **550 cd/m²** vs original **270 cd/m²**. Its module is **112.4×75.1 mm**, rather than 106.1×67.8 mm. At **~£35.60** (example), the difference is **£3.90**; paired with same encoder and AW9523B the base component subtotal is **£44.80**. It has the same ESP32-S3, 16 MB flash, 8 MB PSRAM, 800×480 display: no guaranteed FPS gain. The larger industrial-style PCB/terminals may complicate the 3-key/knob enclosure. Its I2C bus has extra onboard peripherals; verify its own schematic/address list, not only standard 25948 docs.

- Manufacturer: https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3B
- UK listing: https://thepihut.com/products/esp32-s3-development-board-with-4-3-capacitive-touch-lcd-display-800-x-480

## More reliable rotary-processing candidate

**Adafruit I2C Quad Rotary Encoder Breakout PID 5752**, **~£7.30**, default **0x49**. With Waveshare 25948 and encoder PID 377, component subtotal is **£43.40**. Firmware in its seesaw coprocessor accumulates rotary encoder counts. Potential off-label configuration: attach **three MX switches and the encoder's own push** to its four independent switch connections, and one physical encoder A/B to a single rotary footprint. Official guide reads four separate switch pins, but published pinout appears to assign seesaw pin 9 twice; must inspect actual PCB schematic and test each press **before approving this wiring**. The long four-encoder footprint may be difficult to conceal. Unlike standard AW9523B, seesaw board can count knob transitions without constant raw-state I2C polling.

- Product: https://thepihut.com/products/adafruit-i2c-quad-rotary-encoder-breakout-with-neopixel-stemma-qt-qwiic
- Guide: https://learn.adafruit.com/adafruit-i2c-quad-rotary-encoder-breakout/pinouts

## Mandatory checks before purchase or electrical hookup

1. **Exact display revision and geometry:** glass opening, full PCB (not just 4.3-in diagonal), back panel/screw holes, mounting height, USB, antenna and encoder/switch clearance.
2. **I2C address conflicts:** original Waveshare uses CH422G address ranges **0x20–0x27, 0x30–0x3F**, plus touch **0x5D**. Avoid MCP23017 at 0x20–0x27 or Adafruit single seesaw rotary breakout at 0x36–0x3D. AW9523B nominal **0x58** and Quad seesaw **0x49** avoid published reserved ranges; verify by 7-bit I2C bus scan before operation.
3. **3.3 V logic and connector pinout:** Waveshare original screen I2C 4-wire HY/PH2.0 vs AW9523B 6-pin PH2.0 or Adafruit JST-SH; connector plug formats/pin positions **do not match** automatically. Check SDA/SCL pullups, VCC selector, common GND with actual schematics; never wire 5 V directly to unprotected ESP32 GPIO.
4. **AW9523B input resistor bias:** chip does not have convenient internal switch pullups; plan external resistors for 3 MX + A/B + encoder press, debounce and test rotary steps under simultaneous Wi-Fi/LVGL/touch load. If it loses ticks, reconsider a dedicated counter such as QUAD.
5. **Encoder mechanics:** push-switch must work through the final knob, and intended ~18 mm visible outside diameter must not interfere with encoder nut/panel or nearby display.
6. **Firmware/software:** ESP-IDF+LVGL firmware and a secure device protocol are not yet implemented. Existing Flask/HTML/JS browser app cannot simply run on the ESP32-S3. Full screen rendering performance remains bench-untested.

**Provisional trio accepted for verification:** original Waveshare **25948**, Adafruit **377**, Waveshare **AW9523B 22132**. **No purchase authorization or validated harness/case**. Next gate is AW9523B-module startup/reset schematic review, 3.3 V 4-to-6 wire adapter, and internal CAD clearance; see [pre-purchase check](HARDWARE-PRE-PURCHASE-CHECK.md).

References:
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3
- https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Instructions-For-Use
- https://www.waveshare.com/product/aw9523b-io-expansion-board.htm
- https://www.adafruit.com/product/377
- https://learn.adafruit.com/adafruit-i2c-quad-rotary-encoder-breakout/pinouts

## Modern top/knob alternatives (visual selection still OPEN, 2026-10-20)

User dislikes the retro/arrow marking on the **included Adafruit 377 soft-touch knob**. The encoder body itself is still electrically suitable, and has a **6 mm D-shaped shaft**, so swapping the removable cap can be easier than changing the actual encoder. Confirm final shaft insertion depth, panel clearance and ability to **press the encoder**. For any third-party heavy metal knob, test repeated push travel and side loading before final case design. **No substitute selected.**

| Separate knob | Size / look | Shaft fitting, mass | UK price example | Compatibility qualification |
| --- | --- | --- | ---: | --- |
| **Knob Zone KZ0022-01** | **18.6 mm Ø × 16.7 mm**, matte black, smooth cylindrical, **concave top and no marker** | **6 mm D push-fit**, 2.11 g; accepts 8.3–15.8 mm inserted shaft | **£0.54** | **Leading size/style fit** to approx 18 mm mockup and Adafruit 377's 6 mm D shaft; push travel still needs testing. |
| **Knob Zone KZ0087-01** | **15.1 mm Ø × 15.2 mm**, solid black ridged aluminium, flat top and **no marker** | **6 mm round bore + grub screw** (can grip D shaft), 6.23 g; accepts 6.0–12.4 mm shaft insertion | **£3.84** | Modern premium finish, compact; **shorter maximum insertion depth than 377's nominal 15 mm shaft** means test mounting height/exposed shaft; requires set screw. |
| **Knob Zone KZ0059** | **18.0 mm Ø × 18.5 mm**, black/optional matte black, knurled metal and smooth **domed** top, no marker | **6 mm round bore + grub screw**, **25.5 g**; accepts 9.4–16.1 mm insertion | **£2.63** | Exact sketch diameter and secure grip; substantially heavier, so test momentary encoder push and mechanical wear before acceptance. |
| **Adafruit 20 mm anodised black aluminium, PID 5527** | **20 mm Ø × 12.5 mm**, knurled sides, white **triangle pointer on top** | 6 mm round bore + grub screw, **11 g** | **£2.90** at Pi Hut; **sold out** in checked listing | Explicitly NOT ideal for desired unmarked minimalist top despite obvious mechanical fit. |
| **Switch Electronics push encoder MPN 483364** | 24 detents, SPST normally-open push, **20 mm-long 6 mm D shaft**, bare part only | 7 mm panel hole, through-hole solder body | **£0.98 inc VAT** | Optional **entire encoder** alternative if Adafruit 377 mechanical length/price proves unsuitable; no improvement to knob appearance by itself. Verify quality/datasheet and case clearance. |

UK source pages (listing prices/stock can change):
- KZ0022: https://knobzone.co.uk/products/kz0022
- KZ0087: https://knobzone.co.uk/products/kz0087
- KZ0059: https://knobzone.co.uk/products/kz0059
- Adafruit 5527: https://thepihut.com/products/anodized-aluminium-machined-knob-black-20mm-diameter
- Switch encoder 483364: https://www.switchelectronics.co.uk/products/20mm-rotary-encoder-with-switch-6mm-d-shaft
- Adafruit 377 (existing proposed encoder): https://www.adafruit.com/product/377

**Next action:** user chooses a *visual finish* first (smooth concave black / ridged flat-top aluminium / knurled dome), then dimension/shaft/press clearance is verified. Retain **Adafruit 377 + AW9523B + Waveshare 25948** as the currently proposed base; the cosmetic change may only require a separately purchased knob. No parts ordered.


### User visual preference refined — RK M75 low-profile reference (2026-10-20)

User likes **KZ0022 (smooth concave black, 18.6 mm wide × 16.7 mm overall height)** or **KZ0087 (flat ridged black aluminium, 15.1 mm wide × 15.2 mm overall height)**; **rejects KZ0059 domed top**. The style reference is the owner's **Royal Kludge RK M75 keyboard knob**: low exposed height, flat top, short cylinder and subtle textured grip. RK M75 exact physical knob height/diameter could not be reliably verified from a manufacturer measurement; **do not assert numerical equivalence**. Manufacturer keyboard product photo: https://www.rkgamingstore.com/products/m75-keyboard-side-printed-keycaps

**Key distinction:** manufacturer knob *overall height* is not the same as *height protruding above a 3D-printed faceplate*. A custom counterbore/recess and mounting position may expose a shorter cylinder while retaining enough accessible grip, rotation clearance and axial encoder push travel (~0.5 ± 0.2 mm). Full CAD cross-section required.

**Fit caution:** Adafruit 377 has a nominal 15 mm 6 mm D shaft. KZ0022's specified shaft insertion 8.3–15.8 mm is a closer nominal match. KZ0087 uses a 6 mm round bore/set screw (can hold D shafts if oriented properly) but accepts only 6.0–12.4 mm insertion: **cannot assume full 15 mm shaft seats inside; may need to stand proud or have an alternative mounting solution**, tested with push travel. Do not cut a shaft or place an order based on nominal diameters alone. KZ0087 is closest aesthetically to the flat/ridged RK M75; KZ0022 is closer to 18 mm design diameter and easier shaft match. Both still subject to height/fit testing.

**Potential alternative:** custom **3D-printed flat cylindrical 18 mm diameter cap ~8–11 mm tall** with correctly dimensioned 6 mm D recess, allowing final exposed profile to imitate the RK M75, but print tolerances, material wear, tactile grip and shaft/push clearance need physical iteration. This is an optional design exploration, **not a proven or selected part**.

**Pending before cosmetic selection:** if practical, measure the owned RK M75 knob **diameter** and **height above the keyboard's surrounding case surface**, ideally with ruler/caliper and a side photo. Use those numbers to set the visible height target, then test the faceplate/shaft interaction in CAD. No finalized knob/purchase.

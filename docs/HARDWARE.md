# Hardware — research checkpoint (not a wiring guide)

**No final bill of materials or schematic has been accepted. Nothing in this document authorizes a hardware purchase yet.**

## Intended parts

| Part | Current direction | Status |
|---|---|---|
| MCU | ESP32-S3 | Candidate |
| Screen | Waveshare 4.3-inch, 800 × 480 touch | **Exact SKU unresolved** |
| Keys | Four owned MX-style mechanical switches | User has switches; physical wiring TBD |
| Knob | Rotary encoder + knob | Model/pins TBD |
| Case | 3D-printed | CAD/dimensions TBD |
| Power | USB-powered prototype preferred for simplicity | Electrical choice TBD |

## Compatibility checks before buying

1. Identify exact Waveshare product page, board schematic, display/touch controllers and bus (RGB/SPI/etc.).
2. Check which signals occupy ESP32-S3 GPIO and which are truly free for keys/encoder; evaluate I/O expansion if necessary.
3. Confirm PSRAM/flash and LVGL/framebuffer support for 800 × 480 plus artwork, colour extraction and animation.
4. Verify safe logic levels, current requirements, reset/boot pin conflicts, USB wiring and cable lengths.
5. Check mount holes, glass visible area, touchscreen bezel thickness and case clearance.
6. Decide how firmware provisions network, stores pairing credentials, updates itself and recovers after a bad flash.
7. Determine whether the chosen display board already integrates MCU, PSRAM, USB and power to avoid unnecessary duplicate parts.

## Planned deliverables

Validated part/SKU shortlist, pinout table grounded in schematics, firmware framework decision, prototype wiring plan, mechanical CAD, software/hardware test checklist and procurement list with verified costs.

Do not confuse a demo 4.3-inch screen with another Waveshare 4.3-inch variant; resolution alone does not establish pin compatibility.

# Display and interaction design

## Established UI baseline

- Target viewport: **800 × 480** landscape, not a full desktop dashboard.
- Track cover on the left; title, artist, release and timeline on the right.
- Clear transport controls: previous, central play/pause, next.
- Status/mode information near top; player and volume source visible.
- Compact bottom controls with **speaker icon** and Spotify/SYSTEM volume slider.
- Cover-driven ambient glow **clipped to the display**, with subtle movement while music plays; PC mode may modulate glow using a real OS output level.
- Loading/skip artwork feedback should be optimistic but reconcile with actual media state.
- Reuse the established `ui.css` design when creating physical-device or simulator variants. Phase 5.0 diverged and Phase 5.1 restored parity; protect that regression fix.

## Physical controls — user-accepted mapping (2026-10-20)

The revised approximately 1:1-scale sketch establishes **three physical MX keys below the touchscreen** and an **approximately 18 mm diameter rotary knob to the right**. The encoder must have an **integrated momentary push switch**. Pressing the knob replaces the discarded fourth MX mode key. The detached refresh symbol in the sketch was only a placeholder and is **not part of the enclosure**.

| Control | Accepted action | Preliminary size |
|---|---|---|
| K1 (MX) | Previous track | 0.71 in / ~18 mm keycap |
| K2 (MX) | Play/Pause | 0.71 in / ~18 mm keycap |
| K3 (MX) | Next track | 0.71 in / ~18 mm keycap |
| Encoder clockwise/counterclockwise | Volume up/down | ~18 mm knob outside diameter |
| **Encoder push** | **Toggle PC / Wi-Fi mode** | Built-in momentary push, no fourth MX switch |
| Touchscreen | Shuffle, repeat, settings, player and optional mode switch | 4.3 in active diagonal |

**Electrical input count:** 3 MX switch inputs + 2 rotary quadrature signals (A/B) + 1 encoder press = **six logical digital inputs**, plus a common ground. The input breakout and precise GPIO assignments are **not selected**. An encoder without an integrated push switch will **not meet the agreed control mapping**.

**Mechanical caution:** 18 mm keycaps are not 18 mm mounting holes; common MX plate cutouts are ~14×14 mm (verify exact switches) and standard 1u key pitch is 19.05 mm. An 18 mm knob diameter is not its shaft/panel hole size. Check encoder shaft format, push travel, available depth, nut/washer, switch spacing and PCB clearance. The Waveshare 4.3-in diagonal is not the complete module: the candidate original touch board is ~106.1×67.8 mm and requires clearance behind the faceplate.

**Acceptance scope:** button *functions and approximate face layout* are confirmed by the user. No part number, wiring diagram, final CAD, purchase, firmware or physical runtime result has been accepted. The existing Phase 5.2 four-key browser simulator remains **unchanged** pending a separate focused adaptation.

## Screen states to design for firmware

Paired and playing; paired and paused; changing tracks; waiting for artwork; no media; PC unavailable; Wi-Fi disconnected; first-time pairing; revoked pairing; firmware update/recovery.

## UI review checklist

Check contrast, text truncation, fast double-skip behaviour, art-cache invalidation, volume-source label, keyboard/touch targets, disconnection fallback, responsiveness and display bounds. Retain visual continuity on Windows, Linux and simulator.

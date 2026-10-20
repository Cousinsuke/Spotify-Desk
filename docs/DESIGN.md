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

## Physical controls — revised preferred mockup (2026-10-20)

The user's revised approximately 1:1-scale sketch **prefers three physical MX keys beneath the touchscreen plus a rotary knob to the right**. This supersedes the earlier *four-physical-key* hardware concept. Do not modify the accepted Phase 5.2 four-key **software simulator** until the user requests a UI/protocol update.

| Physical control | Preferred action | Front-panel size from sketch |
|---|---|---|
| K1 | Previous track | 0.71 in / ~18 mm square 1u-style keycap |
| K2 | Play/Pause | 0.71 in / ~18 mm square 1u-style keycap |
| K3 | Next track | 0.71 in / ~18 mm square 1u-style keycap |
| Rotary knob | Adjust volume | 0.71 in / ~18 mm knob diameter |
| Rotary push (if fitted) | Undecided | Not counted as a fourth key |
| Touchscreen | PC/Wi-Fi mode, shuffle, repeat, settings and other secondary actions | No independent physical switch specified for these |

The isolated refresh/mode-like icon drawn to the **right of the case outline** is not counted as a fourth confirmed hardware button; its intended role/location requires clarification before CAD.

**Mechanical caution:** an 18 mm square keycap is **not** an 18 mm square switch mounting cut-out; common MX plate cut-outs are about 14×14 mm (validate the exact switch model and plate). Standard 1u pitch is 19.05 mm centre-to-centre; this mockup has more clearance, subject to final CAD. 18 mm knob is its **outside diameter**, not an encoder mounting hole or shaft diameter. Check underside switch/PCB depth, encoder nut/washer/rotation clearance and wiring.

The **4.3-inch diagonal** refers to the active glass/display, not the complete WaveShare module; the candidate original board is ~106.1 × 67.8 mm. The diagram is a **concept sketch, not a validated machinable drawing**: the PCB, display connector, mounting holes, Wi-Fi antenna keepout, case walls and keys/encoder may conflict internally. Verify exact dimensions/revision before cutting or printing.

No firmware/hardware pinout, 3D-print case, purchase or physical validation has been accepted.

## Screen states to design for firmware

Paired and playing; paired and paused; changing tracks; waiting for artwork; no media; PC unavailable; Wi-Fi disconnected; first-time pairing; revoked pairing; firmware update/recovery.

## UI review checklist

Check contrast, text truncation, fast double-skip behaviour, art-cache invalidation, volume-source label, keyboard/touch targets, disconnection fallback, responsiveness and display bounds. Retain visual continuity on Windows, Linux and simulator.

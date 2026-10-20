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

## Physical controls (intended)

| Control | Default action |
|---|---|
| K1 | Previous |
| K2 | Play/Pause |
| K3 | Next |
| K4 | PC / Wi-Fi |
| Encoder turn | Volume in steps |
| Encoder press | Undecided, do not invent function |

No final input mapping, pin assignment, touch gesture behaviour or 3D-print dimensions are accepted yet.

## Screen states to design for firmware

Paired and playing; paired and paused; changing tracks; waiting for artwork; no media; PC unavailable; Wi-Fi disconnected; first-time pairing; revoked pairing; firmware update/recovery.

## UI review checklist

Check contrast, text truncation, fast double-skip behaviour, art-cache invalidation, volume-source label, keyboard/touch targets, disconnection fallback, responsiveness and display bounds. Retain visual continuity on Windows, Linux and simulator.

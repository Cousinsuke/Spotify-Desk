# Echo Show 5 — dashboard UI direction

2026-11-26. User supplied rough visual reference in chat. **Design direction recorded; exact pages and icons not yet approved, no implementation or device validation.**

## Reference and user decisions

- Target: Echo Show 5 Gen 1 landscape 960 x 480, 5.5-inch touchscreen.
- User confirmed Raspberry Pi hosting because future features will be easier and less backend processing/RAM pressure falls on the Echo Show. Frontend performance still needs physical testing.
- Rough reference: large clock (19:26 in the example), date underneath, compact weather summary, warm abstract wallpaper, and narrow dark rounded navigation rail on the right. Active Home icon has a blue highlight. Other slots show Spotify, cloud, droplet and a question mark.
- User explicitly stated icons are approximate and the question mark is a placeholder. They suggested a down arrow that could reveal all additional features as the project grows.
- The reference is a design concept, not actual device screenshot. Text description retained here; original image not uploaded.

## Proposed navigation

Keep central content area and a right-side rail that can collapse (user proposed auto-hide on inactivity, with tap or edge arrow to reopen; exact timing/trigger pending). Aim for five visible slots, with consistent icon sizes and touch targets, active-page indication and accessible labels. Proposed top-to-bottom:

| Page | Suggested icon | Purpose |
| --- | --- | --- |
| Home | House | Default clock-first dashboard |
| Spotify | Spotify logo | Playback and active device |
| Weather | Cloud / weather | Bournemouth forecast |
| Glucose | Droplet | Supplementary current value and trend |
| More | Grid (recommended), chevron/down arrow alternative | Additional widgets |

For More, a grid indicates app/widget selection, a chevron indicates expandable content, and ellipsis tends to imply options. Recommendation: a grid icon opening a separate More page first; possible slide-out drawer later. User has not yet selected the final icon or interaction. If future features exceed available rail slots, list them in More rather than crowding or shrinking main touch targets.

## Proposed page layouts (review before implementation)

- Home: default page at launch/wake (wake behavior to test); large time, date and compact current weather as in reference. Optional compact Spotify now-playing and current glucose/trend summaries, only if they fit without clutter; agree placement with user. No stale value presented as live. Background choice and clock typography pending.
- Spotify: album art, track/artist, progress, previous/play-pause/next, active playback device; volume if supported. Preserve Wi-Fi Spotify Connect and optional PC mode, clearly identify current mode/device, and keep PC-off behavior graceful.
- Weather: fixed Bournemouth, current conditions, today/tomorrow/following day. Hourly details only as optional future refinement if space allows.
- Glucose: prominent current value, source trend, age/timestamp, visible stale/offline status and graph. Retain previous LIVE/GRAPH/BOTH layouts and graph configuration from existing dashboard docs. This is a supplementary display, not medical alarms or a treatment-decision tool. Synthetic data only for design tests.
- More: proposed simple grid/list of additional pages; settings, calendar, timers, reminders and system info are examples, not committed features.

## Visual and performance principles

Minimal, dark/neutral rail with consistent icons; wallpaper can vary on Home. Large readable typography and comfortably spaced touch targets appropriate to 5.5-inch display. Keep the main content clear, no clipping or scrolling on primary views at 960 x 480. Use lightweight CSS, restrained transitions, bounded chart updates and minimal browser work. No expensive animation by default; test against actual hardware. Provide keyboard/focus and accessible labels where applicable.

## 2026-11-26 — Navigation interaction and collaborative layout review

User requested a clean design process with ideas/questions for each page and an explicit **Own idea** option for every choice, including variations or entirely different concepts. Work through global navigation, Home, Spotify, Weather, Glucose, More/Settings, then themes/animations. Record selections as accepted only when user confirms them.

User proposed hiding the right rail after inactivity to reclaim screen area and revealing it by touch or a small arrow on the right. This supersedes the earlier always-visible rail concept. Candidate design (not yet accepted): rail slides away after a configurable idle delay, content uses full width, small left-facing edge handle opens it; lightweight transition; current page and data updates unaffected. Alternative reveal methods: edge swipe, tap empty background or hybrid. Avoid stealing media/graph interactions, hiding while a user is interacting with navigation, or making the control inaccessible. Decide global versus per-page behavior, timeout, whether it overlays or reflows content, reveal control and More behavior before implementation. Prefer a comfortably sized invisible touch area around a small visible handle. No automatic page switching as a side effect of collapse.

Design discussion question set: reveal method (edge handle, background tap, swipe, own idea); auto-hide delay (5/10/15/30 seconds or own idea); layout (reflow, overlay, hybrid, own idea); More (grid/chevron, own idea); Home content (clock-only, subtle summaries, cards, own idea). These are candidates, not final choices. No app code changed.

## Next design task

Define exact layouts of all five pages, including rail dimensions, navigation behavior, typography, spacing, wallpaper, Home summary density and More interaction. Review with user using a browser prototype at 960 x 480; preserve previous desktop UI and code, test with synthetic data first. Then connect the Pi backend over authenticated HTTPS (see SOFTWARE-AND-PI.md). Record screenshots only if appropriate and without private data. No claim of implementation until tested.

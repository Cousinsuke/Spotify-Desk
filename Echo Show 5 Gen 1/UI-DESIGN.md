# Echo Show 5 — dashboard UI direction

2026-11-26. User supplied rough visual reference in chat. **Global navigation and default Home direction accepted by user; remaining page layouts and visual details pending, no implementation or device validation.**

## Reference and user decisions

- Target: Echo Show 5 Gen 1 landscape 960 x 480, 5.5-inch touchscreen.
- User confirmed Raspberry Pi hosting because future features will be easier and less backend processing/RAM pressure falls on the Echo Show. Frontend performance still needs physical testing.
- Rough reference: large clock (19:26 in the example), date underneath, compact weather summary, warm abstract wallpaper, and narrow dark rounded navigation rail on the right. Active Home icon has a blue highlight. Other slots show Spotify, cloud, droplet and a question mark.
- User explicitly stated icons are approximate and the question mark is a placeholder. They suggested a down arrow that could reveal all additional features as the project grows.
- The reference is a design concept, not actual device screenshot. Text description retained here; original image not uploaded.

## Accepted navigation behavior (2026-11-26)

The user explicitly selected all five choices:

- Reveal via a small right-edge arrow **and** inward swipe from the right edge.
- Auto-hide timeout configurable in Settings.
- Content expands to fill the space when the rail is hidden; reflows when revealed.
- More uses a grid icon opening a floating app drawer, not a dedicated full-screen page.
- Auto-hide configurable per page.

Implementation details still proposed: default delay 10 seconds; reset timer on relevant interaction, suspend while drawer is open or navigation has focus, keep a large touch target around the subtle arrow, avoid stealing graph/media gestures, lightweight short transition. No automatic page changes. Exact default delay, dimensions, styling and settings design not selected yet.

## Navigation slots

Keep central content area and collapsible right-side rail following the accepted behavior above. Aim for five visible slots, with consistent icon sizes and touch targets, active-page indication and accessible labels. Proposed top-to-bottom:

| Page | Suggested icon | Purpose |
| --- | --- | --- |
| Home | House | Default clock-first dashboard |
| Spotify | Spotify logo | Playback and active device |
| Weather | Cloud / weather | Bournemouth forecast |
| Glucose | Droplet | Supplementary current value and trend |
| More | Grid (accepted) | Floating app drawer for additional widgets |

The user selected a grid icon opening a floating app drawer. If future features exceed available rail slots, list them in the drawer rather than crowding or shrinking main touch targets. Its exact size, placement and dismissal behavior remain for review.

## Accepted Home direction (2026-11-26)

- Default: option B, clock with subtle widgets. Large central clock and date with compact weather, now-playing and glucose summaries along the bottom, as in the proposed B concept. User explicitly selected B and time/date; the inclusion of all three B summaries is a working interpretation of that selection because user was unsure why the content question was separate. Confirm in prototype; do not treat exact positions/content as separately approved.
- User would like the other Home layouts available as settings presets if they do not materially increase storage/RAM: A minimal clock, C split dashboard, D dynamic clock. Default to fixed/hard-coded layouts, not a general drag-and-resize editor. Implement one active layout at a time and share common components/state; add presets only if practical and performance is acceptable.
- Selectable clock styles in Settings (candidate thin/bold digital, separate hour/minute blocks, analogue). Specific styles and fonts not individually approved.
- Background options conditional on low resource cost: abstract wallpaper, gradient, solid colour, scheduled/time-of-day changes, custom static wallpaper. Pi stores assets/settings, serve appropriately resized image and load only selected background, no animated wallpaper by default. Actual memory and responsiveness remain unmeasured. Keep a basic fallback.
- **Stay on current page during inactivity.** Only deliberate user navigation changes page. Auto-hide rail does not return Home. Startup/wake after app restart or screen sleep remains a separate design/implementation detail.
- Fixed default layout and hard-coded adjustments first; optional lightweight preset/visibility settings if resource use permits. No freeform editor planned for initial version. Do not promise zero RAM/storage overhead; test one active layout, image decoding, navigation and idle memory.
- Night mode was suggested, not approved; defer brightness/schedule/dim clock choices to Settings.

## Page layouts (review before implementation)

- Home: default B clock with subtle bottom summaries as above; optional other fixed presets conditional on resources. Do not switch pages on inactivity. No stale value presented as live.
- Spotify: album art, track/artist, progress, previous/play-pause/next, active playback device; volume if supported. Preserve Wi-Fi Spotify Connect and optional PC mode, clearly identify current mode/device, and keep PC-off behavior graceful.
- Weather: fixed Bournemouth, current conditions, today/tomorrow/following day. Hourly details only as optional future refinement if space allows.
- Glucose: prominent current value, source trend, age/timestamp, visible stale/offline status and graph. Retain previous LIVE/GRAPH/BOTH layouts and graph configuration from existing dashboard docs. This is a supplementary display, not medical alarms or a treatment-decision tool. Synthetic data only for design tests.
- More: floating app drawer with a proposed grid/list of additional pages; settings, calendar, timers, reminders and system info are examples, not committed features.

## Visual and performance principles

Minimal, dark/neutral rail with consistent icons; wallpaper can vary on Home. Large readable typography and comfortably spaced touch targets appropriate to 5.5-inch display. Keep the main content clear, no clipping or scrolling on primary views at 960 x 480. Use lightweight CSS, restrained transitions, bounded chart updates and minimal browser work. No expensive animation by default; test against actual hardware. Provide keyboard/focus and accessible labels where applicable.

## 2026-11-26 — Navigation interaction and collaborative layout review

User requested a clean design process with ideas/questions for each page and an explicit **Own idea** option for every choice, including variations or entirely different concepts. Work through global navigation, Home, Spotify, Weather, Glucose, More/Settings, then themes/animations. Record selections as accepted only when user confirms them.

User proposed hiding the right rail after inactivity to reclaim screen area and revealing it by touch or a small arrow on the right. This supersedes the earlier always-visible rail concept. Original candidate design (subsequently accepted with arrow + swipe): rail slides away after a configurable idle delay, content uses full width, small left-facing edge handle opens it; lightweight transition; current page and data updates unaffected. Alternative reveal methods: edge swipe, tap empty background or hybrid. Avoid stealing media/graph interactions, hiding while a user is interacting with navigation, or making the control inaccessible. These behavior choices have now been resolved above; exact defaults and visuals remain pending. Prefer a comfortably sized invisible touch area around a small visible handle. No automatic page switching as a side effect of collapse.

Design discussion question set: reveal method (edge handle, background tap, swipe, own idea); auto-hide delay (5/10/15/30 seconds or own idea); layout (reflow, overlay, hybrid, own idea); More (grid/chevron, own idea); Home content (clock-only, subtle summaries, cards, own idea). Historical question set; navigation answers are recorded above. Home direction accepted above; exact details remain for prototype review. No app code changed.

## Next design task — Spotify

Present landscape layout choices: classic split album artwork and controls; artwork-focused with lower controls; compact control-first with larger touch targets. Use synthetic metadata/artwork in sketches. Ask about default layout, background tied to album art versus theme, playback controls and progress/seeking, volume placement, active device selection and Wi-Fi/PC mode placement, always including Own idea and optional modifications. Preserve existing functionality where supported and handle offline/restricted devices gracefully. These are proposals for user review, not new accepted choices. Then review Weather, Glucose, floating app drawer/Settings and remaining visual details. Review in browser at 960 x 480 before deployment, preserving existing desktop UI/code; no implementation or physical validation yet.

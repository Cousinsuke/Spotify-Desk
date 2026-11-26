# Echo Show 5 — dashboard UI direction

2026-11-26. User supplied rough visual reference in chat. **Global navigation, default Home and Spotify visual direction accepted by user; remaining pages and hardware-dependent features pending, no implementation or device validation.**

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

## Accepted Spotify design direction (2026-11-26)

- Retain the existing Spotify Desk web player composition: square artwork left, track information and controls right; combine classic split layout with immersive album-art colours. Reference implementation: ../templates/device.html, ../static/ui.css, ../static/device.js, ../static/device.css. Adapt to 960 x 480; retain navigation reflow.
- Background selectable in Settings (candidate dynamic album-colour gradient, dim artwork, subtle glow, theme/static background); actual choices and resource impact to test.
- User wants previous/play-pause/next, touch seeking on progress bar, shuffle/repeat, like/save song. API scopes, current developer-mode endpoint restrictions and device capabilities must be checked before implementing; disable unsupported actions, not fake success.
- Physical volume +/- preferred, with temporary OS-style volume popup showing selected target/percentage then disappearing. User refinement: remove the permanent volume icon and slider from the Spotify page. Move the save-song button to the far-right position previously occupied by the volume icon; extend the tappable active-device selector across the freed width. Physical +/- and transient volume popup are the preferred interface. If physical key forwarding fails or the playback target does not expose remote volume, show the limitation clearly; evaluate a non-permanent fallback (e.g. within the device drawer or Settings) only if needed, not a permanent icon. Local Echo volume is Android media volume; Wi-Fi volume targets selected Spotify device only if supported; PC volume retains existing companion ownership policy. Avoid changing two outputs with one press. Android native bridge or supported kiosk key integration required for remote control; browser alone cannot reliably intercept hardware volume keys. Test key handling, hold/repeat, debounce, popup and no unintended navigation.
- User requests third Echo playback mode, playing through built-in speaker. Wi-Fi / PC / Echo three touchscreen buttons if no spare physical button. Model-specific Kiosk Satellite documentation assigns the third hardware button to screen power (short press) and privacy (hold); preserve privacy and power functions rather than remap. Thus three touch buttons are the planned fallback, Echo mode disabled/unavailable until validated. Do not repurpose hardware privacy control.
- Accepted floating device selector (tap active device name), available devices and active indicator; keep PC companion connectivity separate from Spotify device availability. No automatic transfer merely on opening the menu.
- Idle playback: prefer retain last known track/artwork if lightweight, label accurately paused vs disconnected/no active playback; fallback Spotify logo and No music playing. Proposed memory-only single last state/one resized artwork, no persistent history or secret caching. Never present old state as active or auto-resume on reconnection.
- Local playback first experiment: official Spotify Android app running in background, if install/authentication and Spotify Connect discovery succeed on checkers ROM; Pi controls it using Web API. Alternative Android App Remote SDK (requires installed Spotify app), or browser Web Playback SDK (requires compatible protected media/DRM, Premium and current developer permissions; kiosk WebView not guaranteed). Web API alone cannot stream audio. Test screen-off playback, app/kiosk coexistence, memory, sleep and audio output; no claim of local playback compatibility until hardware test. Existing Wi-Fi/PC modes independent.
- Research: https://kiosksatellite.com/docs/echo-show-5-1st-gen/ (exact model power/privacy behavior, speaker); https://github.com/jxlarrea/kiosk-satellite/issues/821 (reported volume events KEY_VOLUMEUP/DOWN and navigation bug, not proof of remapping support); https://developer.spotify.com/documentation/android ; https://developer.spotify.com/documentation/web-playback-sdk ; https://developer.spotify.com/documentation/web-api/concepts/scopes . Reviewed 2026-11-26. No actual key or audio test performed.

## Page layouts (review before implementation)

- Home: default B clock with subtle bottom summaries as above; optional other fixed presets conditional on resources. Do not switch pages on inactivity. No stale value presented as live.
- Spotify: accepted split/immersive layout and controls above, with expanded device selector and save button at far right, no permanent volume icon/slider; hardware volume and Echo playback remain experimental; floating device selector and three touch mode buttons planned.
- Weather: fixed Bournemouth, current conditions, today/tomorrow/following day. Hourly details only as optional future refinement if space allows.
- Glucose: prominent current value, source trend, age/timestamp, visible stale/offline status and graph. Retain previous LIVE/GRAPH/BOTH layouts and graph configuration from existing dashboard docs. This is a supplementary display, not medical alarms or a treatment-decision tool. Synthetic data only for design tests.
- More: floating app drawer with a proposed grid/list of additional pages; settings, calendar, timers, reminders and system info are examples, not committed features.

## Visual and performance principles

Minimal, dark/neutral rail with consistent icons; wallpaper can vary on Home. Large readable typography and comfortably spaced touch targets appropriate to 5.5-inch display. Keep the main content clear, no clipping or scrolling on primary views at 960 x 480. Use lightweight CSS, restrained transitions, bounded chart updates and minimal browser work. No expensive animation by default; test against actual hardware. Provide keyboard/focus and accessible labels where applicable.

## 2026-11-26 — Navigation interaction and collaborative layout review

User requested a clean design process with ideas/questions for each page and an explicit **Own idea** option for every choice, including variations or entirely different concepts. Work through global navigation, Home, Spotify, Weather, Glucose, More/Settings, then themes/animations. Record selections as accepted only when user confirms them.

User proposed hiding the right rail after inactivity to reclaim screen area and revealing it by touch or a small arrow on the right. This supersedes the earlier always-visible rail concept. Original candidate design (subsequently accepted with arrow + swipe): rail slides away after a configurable idle delay, content uses full width, small left-facing edge handle opens it; lightweight transition; current page and data updates unaffected. Alternative reveal methods: edge swipe, tap empty background or hybrid. Avoid stealing media/graph interactions, hiding while a user is interacting with navigation, or making the control inaccessible. These behavior choices have now been resolved above; exact defaults and visuals remain pending. Prefer a comfortably sized invisible touch area around a small visible handle. No automatic page switching as a side effect of collapse.

Design discussion question set: reveal method (edge handle, background tap, swipe, own idea); auto-hide delay (5/10/15/30 seconds or own idea); layout (reflow, overlay, hybrid, own idea); More (grid/chevron, own idea); Home content (clock-only, subtle summaries, cards, own idea). Historical question set; navigation answers are recorded above. Home direction accepted above; exact details remain for prototype review. No app code changed.

## Next design task — Weather

Present landscape weather layout options: current conditions left with daily cards right; current conditions across top with three day cards below; minimalist current weather plus expandable details. Keep Bournemouth default and next couple days from prior decisions; ask about layout, forecast detail, icon style, background, forecast time range and optional expanded information with Own idea for every choice. Then review Glucose, floating drawer/Settings and visual details. All mockup data illustrative, no device implementation yet. Preserve existing software and test on 960 x 480 before deployment.

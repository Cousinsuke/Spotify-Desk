# Echo Show 5 — dashboard UI direction

2026-11-26. User supplied rough visual reference in chat. **Global navigation, default Home, Spotify, Weather and Glucose design directions accepted by user; remaining pages and hardware-dependent features pending, no implementation or device validation.**

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
- User requests third Echo playback mode, playing through built-in speaker. Initial proposal was three touchscreen buttons for Wi-Fi / PC / Echo if no spare physical button; user subsequently requested a single compact dropdown with down arrow instead. Show current mode in the collapsed selector and all three options when expanded; do not show three permanent buttons. Keep separate from the bottom playback-device selector. Model-specific Kiosk Satellite documentation assigns the third hardware button to screen power (short press) and privacy (hold); preserve privacy and power functions rather than remap. Thus the compact touchscreen mode dropdown is the planned interface, Echo mode disabled/unavailable until validated. Switching mode is deliberate, not triggered by opening the dropdown. Dismiss on selection or outside tap; show unavailable modes clearly. Do not repurpose hardware privacy control.
- Accepted floating device selector (tap active device name), available devices and active indicator; keep PC companion connectivity separate from Spotify device availability. No automatic transfer merely on opening the menu.
- Idle playback: prefer retain last known track/artwork if lightweight, label accurately paused vs disconnected/no active playback; fallback Spotify logo and No music playing. Proposed memory-only single last state/one resized artwork, no persistent history or secret caching. Never present old state as active or auto-resume on reconnection.
- Local playback first experiment: official Spotify Android app running in background, if install/authentication and Spotify Connect discovery succeed on checkers ROM; Pi controls it using Web API. Alternative Android App Remote SDK (requires installed Spotify app), or browser Web Playback SDK (requires compatible protected media/DRM, Premium and current developer permissions; kiosk WebView not guaranteed). Web API alone cannot stream audio. Test screen-off playback, app/kiosk coexistence, memory, sleep and audio output; no claim of local playback compatibility until hardware test. Existing Wi-Fi/PC modes independent.
- Research: https://kiosksatellite.com/docs/echo-show-5-1st-gen/ (exact model power/privacy behavior, speaker); https://github.com/jxlarrea/kiosk-satellite/issues/821 (reported volume events KEY_VOLUMEUP/DOWN and navigation bug, not proof of remapping support); https://developer.spotify.com/documentation/android ; https://developer.spotify.com/documentation/web-playback-sdk ; https://developer.spotify.com/documentation/web-api/concepts/scopes . Reviewed 2026-11-26. No actual key or audio test performed.

## Accepted Weather design direction (2026-11-26)

- User selected B: large current condition icon/temperature above daily forecast cards, adapted to 960 x 480 and both navigation rail states.
- Current summary: temperature and weather condition, feels-like temperature, rain probability, sunrise/sunset and humidity. Distinguish forecast precipitation probability from measured precipitation; label the period (e.g. next hour or today) rather than treating it as a current observation. Wind and UV were not selected for the main view.
- Forecast duration configurable in Settings; proposed default remains today + next two days. Proposed horizontal swipeable row for longer forecasts to retain readable card sizes; exact supported durations and detail presentation pending prototype. Separate rail edge gesture from forecast scrolling.
- Selectable weather icon styles in Settings, with a consistent Home weather symbol mapping. Exact icon sets pending.
- Static weather-themed images change with current condition. Proposed clear/cloud/rain/storm/snow/fog and day/night variants; serve appropriately resized assets from Pi, display one active image, avoid animated backgrounds and maintain contrast with a lightweight overlay. Resource impact remains unmeasured.
- Always Bournemouth, no location input or selector. Reuse existing town-center configuration and Open-Meteo integration; use Europe/London local times.
- Tapping a forecast day opens more details. Proposed floating panel with date, daily high/low, condition, rain probability, sunrise/sunset and hourly breakdown where supported. Exact detail fields/layout not separately approved. Dismiss without changing main page. Pi should cache weather data; preserve last-success timestamp and label stale/unavailable data. Verify API fields and allowed forecast lengths at implementation; no new weather endpoint or code implemented.
- Illustrative weather previews are not live forecasts.

## Accepted Glucose design direction (2026-11-26)

User supplied four screenshots of the existing desktop browser Glucose page (BOTH, GRAPH, LIVE and GRAPH with 24h/FULL). User explicitly wants the existing visual layout and graph functionality preserved, instead of answering the previous general questionnaire. Screenshots contain private CGM data; do not upload, reproduce readings, or copy graph samples to Git. Describe design only, and use synthetic data in prototypes.

- Preserve dark green gradient, rounded dark reading/graph panels, mint line/latest dot, shaded display band, Libre 2 Plus header, live/stale/offline source status, update age/timestamp, number with mmol/L and source trend arrow. Keep the small supplementary-display safety footer. BOTH: square live tile left and wider graph right, top edges aligned. GRAPH: full-width graph. LIVE: large centered value/unit/arrow and update note. Adapt spacing to actual 960 x 480 viewport without old horizontal navigation; use agreed right-side auto-hide rail and reflow.
- Source reviewed: ../static/glucose-chart.js, ../static/desk-dashboard.js, ../static/desk-dashboard.css, ../glucose_live.py, ../docs/DASHBOARDS.md and ../docs/GLUCOSE-LIVE.md. Existing layout defaults to BOTH and remembers selected layout in localStorage (preference only). Existing chart duration starts at 6h and scale at AUTO. Preserve these defaults unless user selects otherwise.
- Keep separate visible 1h/3h/6h/12h/24h buttons and the single AUTO/FULL toggle from screenshots. The renderer filters sorted/deduplicated timestamped valid readings over the selected window (current time for live); no extra upstream request on range changes. Retain current local-time x-axis, shaded 4–7 visual band, latest dot, gaps when consecutive data are more than 20 minutes apart, no invented/extrapolated readings. Backend currently requests up to 730 readings, accepts up to 24h of history; 24h may be incomplete. Preserve existing limits and privacy.
- AUTO: default bounds 3–12 mmol/L, expand lower to whole number below 3 (floor, not below 0) and upper in multiples of 3 for values above 12. Use whole-number ticks, with target boundary labels formatted as in existing renderer and suppress labels to avoid overlap. FULL: normal 3–21 in steps of 3; expand bounds in multiples of 3 for valid extremes and thin labels if needed. Current source accepts finite values 0.5–40 mmol/L. These are visual scaling rules, not clinical thresholds. Keep existing chart algorithm, not a new fixed 40 ceiling.
- Final refinements accepted: compact top-right LIVE/GRAPH/BOTH dropdown matching Spotify; selectable backgrounds in Settings with original green gradient as default; existing 6h and AUTO defaults on reload; retain existing graph interaction unchanged (no new tap/drag inspection). Preserve existing remembered view preference; no new persistence of duration or scale.
- User requested optional dynamic background: red for lows, green in display range, yellow-orange above range up to 15 mmol/L, orange from 15 upward. Proposed exact boundary interpretation using existing display band: below 4 red, 4–7 inclusive green, above 7 and below 15 yellow-orange, 15 and above orange. These are aesthetic display bands only, not medical categories, alerts or treatment guidance. Exact shades and boundary interpretation pending prototype review. Use muted CSS gradients, no continuous animation. On stale/offline/unknown state revert to neutral appearance, preserve visible source status and age, never imply freshness with colour. Do not alter chart geometry, data, source trends or official monitoring. No additional polling or persisted readings for theme. No device performance measured.
- Existing GGC backend polls at least 150s apart, stale at age >=600s or failed upstream; preserve cached polling/backoff, source timestamp and clear stale/offline states, hide Home current value/arrow if not fresh. Pi-to-Echo authenticated HTTPS remains unimplemented; no real data on plain HTTP, no sensitive logs/cache/storage. Official Libre app remains authoritative for monitoring, alarms and treatment.
- No new app code or physical-device tests performed. Screenshots are user-provided evidence of existing browser presentation, not evidence of Pi/Echo deployment.

### Final Glucose layout refinements (2026-11-26)

User requested a cleaner page after reviewing the illustrative preview, and explicitly selected A for BOTH width and A for graph title.

- Remove redundant GLUCOSE / Libre 2 Plus heading, CURRENT READING and GLUCOSE TREND titles, and permanent DEMO label from normal live presentation. Keep the compact view dropdown in the top-right. Synthetic previews must still be unmistakably labelled as demo/sample, separate from the normal live layout. Stale/offline/unavailable states and reading age remain clear; never misrepresent old or synthetic readings as live.
- Default dark green page background, lighter green rounded cards, no unnecessary enclosing panel or wasted heading area. Retain selectable static and optional dynamic backgrounds already agreed.
- BOTH: aligned cards of equal height; approximately 40% reading and 60% graph width, excluding gap. Reading panel contains number, source arrow, mmol/L and update age/time. Graph panel contains chart and controls; no graph title. Use the extra space and reflow for both navigation states.
- LIVE: one large reading card. GRAPH: one large graph card. BOTH and GRAPH: place two compact dropdowns inside top-right of graph card, one for 1h/3h/6h/12h/24h and one for AUTO/FULL. These replace the exposed duration buttons and scale toggle visually; preserve exact underlying filtering/scaling behavior, 6h/AUTO reload defaults and unchanged graph interaction. No graph controls in LIVE view.
- Keep unobtrusive clear stale/offline indication and supplementary-display footer; official Libre app remains authoritative. Exact spacing, accessible touch targets and status placement to test at 960 x 480. No implementation yet.

## Page layouts (review before implementation)

- Home: default B clock with subtle bottom summaries as above; optional other fixed presets conditional on resources. Do not switch pages on inactivity. No stale value presented as live.
- Spotify: accepted split/immersive layout and controls above, with expanded device selector and save button at far right, no permanent volume icon/slider; hardware volume and Echo playback remain experimental; floating device selector and compact Wi-Fi/PC/Echo mode dropdown planned.
- Weather: accepted B layout with large current weather, selected statistics, configurable daily forecast duration, selectable icon styles, condition-dependent static backgrounds and tappable forecast days; fixed Bournemouth.
- Glucose: final clean layout accepted; equal-height 40/60 BOTH cards, no redundant headers or graph title, top-right view dropdown and graph-card duration/scale dropdowns, original chart behavior and green default. See final refinements above, which supersede earlier visible range-button and header proposals. Dynamic colour shades and exact boundary handling proposed for prototype review.
- More: floating app drawer with a proposed grid/list of additional pages; settings, calendar, timers, reminders and system info are examples, not committed features.

## Visual and performance principles

Minimal, dark/neutral rail with consistent icons; wallpaper can vary on Home. Large readable typography and comfortably spaced touch targets appropriate to 5.5-inch display. Keep the main content clear, no clipping or scrolling on primary views at 960 x 480. Use lightweight CSS, restrained transitions, bounded chart updates and minimal browser work. No expensive animation by default; test against actual hardware. Provide keyboard/focus and accessible labels where applicable.

## 2026-11-26 — Navigation interaction and collaborative layout review

User requested a clean design process with ideas/questions for each page and an explicit **Own idea** option for every choice, including variations or entirely different concepts. Work through global navigation, Home, Spotify, Weather, Glucose, More/Settings, then themes/animations. Record selections as accepted only when user confirms them.

User proposed hiding the right rail after inactivity to reclaim screen area and revealing it by touch or a small arrow on the right. This supersedes the earlier always-visible rail concept. Original candidate design (subsequently accepted with arrow + swipe): rail slides away after a configurable idle delay, content uses full width, small left-facing edge handle opens it; lightweight transition; current page and data updates unaffected. Alternative reveal methods: edge swipe, tap empty background or hybrid. Avoid stealing media/graph interactions, hiding while a user is interacting with navigation, or making the control inaccessible. These behavior choices have now been resolved above; exact defaults and visuals remain pending. Prefer a comfortably sized invisible touch area around a small visible handle. No automatic page switching as a side effect of collapse.

Design discussion question set: reveal method (edge handle, background tap, swipe, own idea); auto-hide delay (5/10/15/30 seconds or own idea); layout (reflow, overlay, hybrid, own idea); More (grid/chevron, own idea); Home content (clock-only, subtle summaries, cards, own idea). Historical question set; navigation answers are recorded above. Home direction accepted above; exact details remain for prototype review. No app code changed.

## Next design task — floating app drawer and Settings

Final Glucose layout refinements are accepted. Design a compact floating app drawer launched by the existing grid icon without changing the current page until a destination is selected. Present alternative placement/shape (right-side popover, centered grid, bottom tray), dismissal behavior, initial apps vs optional future placeholders, and Settings access. Settings proposal: full-page layout with left category list and right detail pane; alternatives include floating panel or category tiles. Suggested categories: General/Display, Navigation, Home, Spotify, Weather, Glucose, Connections/System; group related preferences, preserve accepted settings, and avoid exposing credentials or private readings. Prefer immediate local preference application with reset controls, Pi-backed non-sensitive preferences where appropriate; exact persistence, app ordering/pinning, brightness/night mode and animations pending approval. Ask only relevant questions, always include Own idea. Use illustrative previews, no actual health data. Next review final themes/animations, then prototype and Pi preflight; no code or hardware implementation yet.

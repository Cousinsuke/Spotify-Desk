# ChatGPT handoff — Spotify Desk Thing

## Glucose BOTH graph alignment — 2026-10-25 (v0.9; pending user screenshot)

- User provided Windows screenshots of v0.8 at 1h/24h AUTO and FULL, confirmed overall square-live-plus-graph layout looks good but noticed the plot top edge **lower than the live reading square**. The chart header (GLUCOSE TREND + time-range/scale buttons) was in the same flex column and consumed height above the plot.
- Added narrow scope CSS to `static/desk-dashboard.css`: in Glucose BOTH, position header/controls absolutely above the chart column, shorten and vertically centre the chart column to align plot top with the left square, maintain actual chart SVG width and prior gap-safe glucose rendering. Under a 610px-wide browser, restore normal heading flow for stacked layout. No JS/Gluroo logic or Spotify player changed.
- Template CSS cache v0.9; Python static dashboard test updated. Source validation performed, live browser screenshot revalidation pending. Next: pull main, reload and compare top boundaries of square and graph for BOTH at 1h/24h.

## Glucose BOTH mode horizontal experiment — 2026-10-25 (v0.8; user visual validation pending)

- User confirmed v0.7 graph looks good and supplied a Figma-inspired screenshot for an alternative **BOTH** glucose layout patterned after the Spotify player: **square LIVE reading tile on the left**, **wider recent-glucose chart on the right**, keeping all existing backgrounds/details, 800×480 screen, real Gluroo feed, 4–7 range, time and scale buttons. This replaces only the composition inside Glucose BOTH; LIVE-only and GRAPH-only are unchanged.

- Implemented `desk-glucose-layout` and `desk-glucose-chart-column` wrappers in `static/desk-dashboard.js`; BOTH uses two columns (218px square reading tile plus flexible timeline plot) in `static/desk-dashboard.css`. The current mmol/L value, trend and age are retained, including clear STALE/OFFLINE and safety labelling. Chart max-height ~240px to avoid vertical over-stretch. Responsive fallback stacks below viewport width 610px.

- `static/glucose-chart.js` now supports variable SVG width: plot uses the actual measured browser width (not a compressed 700px viewBox), retaining readable axis/time labels and preserving 4–7 shading. ResizeObserver recalculates after layout/viewport changes. Chart fixture now tests compact 410px and full 680px rendering; dashboard static tests cover BOTH wrapper, modes and Spotify controls. Assistant-side JS/chart static checks passed, no browser runtime screenshot yet.

- Cache busting: template imports `desk-dashboard.css?v=0.8`, `glucose-chart.js?v=0.8`, `desk-dashboard.js?v=0.8`. No Gluroo server, auth, API, LAN routing or native firmware changes. Do not commit personal health values.

- Next: user pulls GitHub main on Windows 11 and restarts their configured server in the same PowerShell session, visually verifies BOTH at 800×480 and tests LIVE/GRAPH and all 1/3/6/12/24h chart controls. After user acceptance, record approval; otherwise revise this layout.

## Glucose v0.7 AUTO axis — 2026-10-25 (awaiting new screenshot)

- User observed AUTO labels 12, 9.6, 7, 4, 2.5 in v0.6. Old code selected an interpolated quartile and a padded lower bound. User requested a baseline of 3–12 mmol/L, whole-number supporting labels, retaining 4–7 reference band, and automatic extension only for actual outlier readings.

- v0.7 defaults to 3–12 with Y ticks 3, 4.0, 7.0, 9, 12. Only 4.0 and 7.0 remain decimal markers for target range. AUTO expands below 3 to a whole number and above 12 to the next multiple of 3 when actual readings demand it. No cropping. Five labels maximum, 15 SVG px minimum spacing with 11px font so default 3/4 pair stays legible.

- FULL is unchanged at 3–21 in steps of 3. Changed static/glucose-chart.js, tests/check_glucose_chart.cjs, template chart script cache to v0.7 and corresponding tests. Assistant-side JS fixture checks passed; user runtime screenshots for v0.7 pending. No Gluroo/API, Spotify, credentials or sensor-data modifications.

- Next: user pulls main, runs chart tests, restarts existing server in same Windows PowerShell session, verifies AUTO 3/6h and FULL in the 800×480 simulator.

## Glucose chart scale and label fix — 2026-10-25 (v0.6, pending user runtime check)

- User provided live Windows screenshots showing LIVE / GRAPH / BOTH modes and clock-time chart plots at 1h and 3h. All modes looked operational. Requested **FULL scale maximum 21**, with axis markings **21, 18, 15, 12, 9, 6, 3**, and an AUTO y-axis fix: reference numbers near 7.0 overlap when graph time range exceeds one hour.
- Implemented new `yBounds` FULL baseline **3–21 mmol/L** with exactly 3-unit labels, target 4–7 green-band borders shown independently of Y tick labels. If actual values outside 3–21 arrive, FULL extends by multiples of 3 (and thins labels if needed to prevent crowding) rather than clipping outlier data. AUTO makes 4.0 and 7.0 reference labels highest priority; other axis ticks are suppressed if within 20 SVG pixels. This fixes cases like 7.0 and ~7.3 overlapping without flattening glucose changes.
- `static/glucose-chart.js` and chart tests updated, dashboard scale accessibility labels corrected, `templates/device.html` imports `glucose-chart.js?v=0.6` / `desk-dashboard.js?v=0.6` to avoid stale cache, dashboard tests adjusted. Assistant-side JS chart regression assertions passed; **user Windows visual regression confirmation still pending**. Gluroo/API/security and Spotify handlers unchanged.
- Next: pull latest main, run `node tests/check_glucose_chart.cjs` and focused dashboard tests, restart existing Flask server in same credential-configured PowerShell session and inspect GRAPH/BOTH AUTO vs FULL at 3h/6h. Do not record health readings or credentials in repo.

> Current-state save point, not the full project history. **Read this first** in a new project conversation. Cross-check against the current branch and commits.

Updated: 2026-10-25

## Glucose dashboard Libre-style chart + layouts — 2026-10-25 (implemented; not runtime accepted yet)

- User supplied an official Libre app screenshot as visual reference and asked for **real wall-clock labels under chart**, a shaded **4.0–7.0 mmol/L preferred display band**, graph scaling that reveals changes, **1h/3h/6h/12h/24h** time windows, and **Live / Graph / Both** layouts. They want the glucose top-right WI-FI/PC selector replaced by these view choices only while on the Glucose screen. Existing Spotify control semantics **must remain unchanged**.
- Implemented a standalone **`static/glucose-chart.js`** module: local `en-GB` x-axis clock labels from actual sample timestamps, 4–7 green shaded band, y-axis reference values and boundaries, optional AUTO zoom or the earlier FULL 0–40 mmol/L scale (superseded in v0.6), missing-reading segment breaks greater than 20 minutes and latest reading dot. Range selection supports 1,3,6,12,24h. Previous fixed broad y-scale was flattening lines. `static/desk-dashboard.js` now uses this renderer for Gluroo live, imported history and clearly labelled sample data.
- Glucose-only top-right buttons replace the visible Spotify WI-FI/PC selector with **LIVE / GRAPH / BOTH**; original Spotify controls stay in DOM and reappear unchanged on Spotify and other pages. The view mode preference is localStorage-only; no glucose values stored. Live-only hides chart, Graph-only hides large number, Both shows both. Stale/offline and non-treatment labels remain visible. Browser assets versioned to v0.5; `device_bridge.py` allowlists only the public chart static asset, **not** the private glucose API.
- Added `tests/check_glucose_chart.cjs` synthetic assertions for time labels, shading, scaling, gaps and five ranges. Updated Python dashboard and LAN static allowlist tests. Assistant-side V8 chart assertions and JS syntax passed; **no new screenshot/runtime user validation yet**.
- **Live data limits:** provider GGC states history is roughly the previous 24h, **up to 730 records**; thus 24h is a plot window, not a guarantee of complete every-minute values. Target band 4–7 is only this user's graph preference and never used as a medical alert/treatment recommendation. Glucose route remains local-only, not encrypted to physical ESP32.
- Next: user pulls main in Windows, restarts Flask from the existing credential-configured PowerShell session, runs focused tests, checks v0.5 at 800×480 and switches every view/range while Gluroo stays live. Request feedback before marking UI accepted.


## Glucose screen visual refresh — 2026-10-25 (implemented; awaiting user review)

- User ran six glucose backend tests on Windows 11, **all passed**, configured their own Gluroo GGC account in local PowerShell and demonstrated the actual `/device` Glucose tab displaying **LIVE FEED**, a recent mmol/L value/trend and non-synthetic time-series graph. Flask route and pairing were working. Avoid storing the user's actual glucose values or secrets in project docs.
- User requested a cleaner **Spotify-style minimalist redesign** of that verified live Glucose screen. Source changes on `main`: one large high-contrast number with separate trend arrow/unit, small last-reading timestamp, short LIVE/STALE/OFFLINE pill, simplified chart ticks and last-reading dot, 3/6/12h controls, one unobtrusive but retained non-treatment notice. Dynamic page label changes the topbar suffix only for active page; Spotify page and its controls otherwise unchanged. Offline readings must never be presented as live or silently replaced with sample data.
- **Implementation and static tests added; new visual design NOT yet runtime-tested/user-accepted.** Next action: Windows `git pull`, restart existing Python server (while keeping private Gluroo env variables available), open `/device`, verify layout, real feed/trend freshness, tab switching and no overflow at 800×480. Obtain visual feedback before further feature scope.
- Existing `--lan` is HTTP and remains blocked for personal glucose endpoint. No ESP32 CGM firmware, physical-device medical-data connection or credentials added.


## Ad-hoc multi-dashboard preview — 2026-10-25 (Windows visual validation confirmed)

- User asked to start building Home, Weather and glucose monitoring after a review of all repository Markdown files. Existing hardware candidate and current Rev B CAD remain unchanged.
- Additive `/device` browser screens created: default Home (clock, existing Spotify summary, weather shortcut, disconnected glucose status), Spotify (Phase 5.2 interface preserved), Weather (Open-Meteo city geocoding/current/hourly forecasts, example London and browser-local city preference), Glucose (**synthetic SAMPLE DATA graph only, no connected Libre 2 Plus readings**). Screen tabs, arrow-key navigation and swipe switching. New CSS/JS loaded after existing assets; restricted LAN allowlist includes those static assets only.
- Feature code committed on main through `3918194`, and regression tests through `3bf9630`. See [docs/DASHBOARDS.md](DASHBOARDS.md) for architecture, safety boundaries and test instructions. Windows user ran tests with Python 3.13: **42 passed, 2 Linux-only test errors**; four dashboard tests and restricted LAN assets test passed. Node syntax check passed. Screenshots show Home, Spotify, live weather and clearly labelled sample graph; the paired device is connected. Spotify transport functions, all chart range controls, Omarchy and ESP32 remain to be tested.
- **Glucose privacy gate:** existing `--lan` device transport is plain HTTP. Never send real medical data or Abbott credentials through it. No permitted/authorised Libre data integration validated; official Libre app remains primary for readings, alarms and treatment decisions.
- **Next action:** validate actual playback/volume controls and chart time-range switching, address Windows/Linux test isolation, then research a secure, permitted glucose-data integration. The dashboard's Windows visual layout and live weather are user-confirmed. No firmware, physical purchase or enclosure change implied.


## Near-real-time glucose bridge — 2026-10-25 (implemented; real account and Windows testing pending)

- User rejected manual historical CSV as unsuitable and requested the same **live** Libre 2 Plus updates offered by third-party desk glucose displays. Research verified Abbott phone-to-LibreLinkUp cloud sharing and third-party products including GlucyView, Glucose Display and Glowcose. Gluroo explicitly supports importing Libre data via LibreLinkUp and provides the experimental, documented Gluroo Global Connect Nightscout-compatible read API. Direct Abbott automated API access restricted by Abbott terms; not implemented.
- Added `glucose_live.py`: opt-in HTTPS remote CGM reader configured with process env `DESK_GLUCOSE_URL` + 40-character `DESK_GLUCOSE_API_SECRET_SHA1`; no local credentials file, no browser access to secret, no redirected URLs. Fetch `/api/v1/entries/sgv.json` max 730 entries, 150s cache, 429 backoff, 10m stale cutoff, mg/dL to mmol/L, in-memory only.
- Added **authenticated, loopback-only `/api/device/glucose`** in Flask; route is deliberately excluded from the HTTP LAN device allowlist. Browser `/device` Glucose screen auto-fetches via paired browser credentials, shows last received mmol/L/trend/time, live history with gaps and stale/offline label. Home glucose tile mirrors live status. Older CSV stays available when live is unconfigured.
- Added `tests/test_glucose_live.py` for mock HTTP, timestamp/unit validation, authorization-header handling, caching/rate limit and no-LAN route exposure; no actual user's CGM data has been used. `docs/GLUCOSE-LIVE.md` contains **iPhone follower → Gluroo → Windows PowerShell** setup. **Not yet run on user's Windows 11 or Omarchy, no Gluroo or real Libre feed verified.** Existing 800x480 Spotify/Weather pages intended to be preserved.
- Key constraints: Gluroo GGC API is experimental, API SHA-1 hash gives read+write (not a safe low-privilege token); consent/privacy implications; Abbott may restrict third-party access; feed has multi-minute delays. Official LibreLink app remains primary for alarms/treatment. Physical ESP32 CGM remains blocked on mutually authenticated encrypted transport.
- Next: user sets up an Abbott LibreLinkUp follower account and optionally Gluroo CGM integration on iPhone, generates GGC URL/SHA-1 hash **privately**, runs new mock tests and launches the Windows app, verifies live labels/timestamp and source freshness. Then resolve 800x480 UI issues; only next build physical secured device transport. Avoid collecting their account secrets or readings in chat.

## LibreView historical CSV import — 2026-10-25 (implemented; Windows runtime test pending)

- User asked to continue with glucose dashboard research after confirming the four-screen Windows browser preview. Abbott confirms Libre 2 Plus + LibreView/LibreLinkUp interoperability; LibreView historical CSV can be manually exported. Abbott terms restrict automated access, so **no unofficial Libre credentials/API scraping** has been added.
- New local-only in-browser CSV import for `/device` recognises LibreView historic glucose record type 0, DMY/MDY date-order selection, mmol/L or mg/dL, filters invalid records, and plots 3h/6h/12h windows relative to the **last exported timestamp**. Gaps exceeding 20 minutes are shown as gaps, with explicit **HISTORY · NOT LIVE** notices. No upload/storage/transmission by application; no actual personal export or data has been accessed.
- Source: `static/glucose-history.js`, modified `static/desk-dashboard.js`, `static/desk-dashboard.css`, `templates/device.html`, `device_bridge.py`; offline synthetic fixture checks `tests/check_glucose_history.cjs`, dashboard/allowlist test updates. Pure JS parser and dashboard source passed assistant-side syntax/unit checks in isolated V8; **user Windows/Omarchy/browser test pending**, do not claim implemented live Libre 2 Plus monitoring.
- Prior Home/Weather/Spotify visual Windows verification retained; previous full Python suite 42/44 with two Linux-only errors remains unresolved. See [dashboard research and private import instructions](DASHBOARDS.md).
- Next task: user downloads their LibreView CSV **privately** and tests import locally at `127.0.0.1`, then report graph/date labels without sharing glucose values or the CSV. If successful, investigate only permitted and secure options for genuinely live monitoring before extending a LAN device protocol.

## Repository / checkpoint

- Repository: `Cousinsuke/Spotify-Desk`
- Default / current development branch: `main` (no alternate development branch established yet)
- Last source baseline: **Phase 5.2** source imported into `main` from checksum-checked ZIP; actual GitHub commit verified
- Latest implementation checkpoint: **`7172c2ee2f285253507b13c71acb7072adc04067`** (`feat: import accepted Phase 5.2 desktop and simulator baseline`, source commit). Later docs/script commits are not a newer application version.
- Handoff status: GitHub migration completed; 16 historical ZIPs archived at `f781506`. User uploaded the full Rev B package in [`6ae257e`](https://github.com/Cousinsuke/Spotify-Desk/commit/6ae257e2ce01256b320417fd21e14d9339bd9ed1): original ZIP and 13 extracted files. GitHub blob hashes matched the uploaded ZIP entries exactly. This is a CAD artifact checkpoint, not newer application code.
- GitHub access: connected read/write access was confirmed at bootstrap; verify access in future conversations

## Current project phase vs current actual work

- **Current project phase:** Phase 6 physical design research/CAD, no ESP32 firmware implemented.
- **Current actual work:** **Rev B design package is now tracked in GitHub** at [`mechanical/revB/cad/`](../mechanical/revB/cad/), with the [original source ZIP](../mechanical/revB/Spotify_Desk_RevB_CAD_Shared_Package.zip). Both sharp and R5-rounded cases, full reference assemblies, dimensioned DXF, four-page A3 PDF, preview images, Python CadQuery generator and JSON dimensions are preserved. User indicates these are the designs to continue from; no single exterior style or print-ready enclosure is definitively approved.
- **Rev B geometry (retained):** 156 mm width × 83.093 mm desk depth × 106.107 mm height, 55° sloped 156×110 mm face, 16mm chin, 20mm roof and assumed 3mm wall; either sharp or R5 edges. LCD origin X=8,V=8, screen centre X=61.05; centred MX keys X=31.05,61.05,91.05 at V=91; knob (138,44), Ø15.1mm. **Important correction from official STEP:** earlier right-I2C/left-USB orientation was taken from a **rear view** and is reversed from front viewing side. Manufacturer source shows **USB-C1/C2 on front RIGHT**, **I2C 4P header on front LEFT**. The earlier 3.3mm right-I2C/encoder gap is only an old hypothetical calculation; not the physical layout.
- **Status:** Reference STEP solids were reopened/checked, DXF reopened and A3 PDF rendered during design; GitHub files now byte-matched 13/13 with source ZIP. **Not fabrication geometry**: screw bores, full electronics/cable collisions, switch depths, USB openings and fasteners remain unverified. AW9523B RESET/pin mapping still open. No hardware purchase reported. Accepted software remains Phase 5.2 (`7172c2e`).

## Last accepted work

- **Most recent repository checkpoint:** User provided genuine official Waveshare STEP ZIP; ZIP SHA-256 independently matched, 31,338,066-byte STEP parsed using OpenCascade/XCAF (693 solids) and source sockets/standoffs inspected. An alignment/clearance reference was implemented with 10 locally passing Python tests; **user Windows testing of this new STEP-based tool pending**. Earlier 3D packaging tool has 8/8 user Windows tests passed. No actual physical fitting or firmware.
- **Most recent accepted interaction-design task:** three physical MX media keys plus rotary volume encoder whose **press toggles PC/Wi-Fi** (2026-10-20; design approval only, no hardware implementation).
- **Last accepted software:** Phase 5.2 device/PC artwork reliability fix on **Omarchy**; user confirmed the fix worked and ran **39 Python tests**, all passing.
- Previous accepted: Phase 4.2 Windows and Omarchy volume sync; Windows companion play/pause, album art, sound-level stream; Phase 5 pairing and simulator UI were demonstrated, then polished.
- **Do not assume:** Phase 5.2 has been individually runtime-validated on Windows after the last patch; earlier Windows platform validation is real but older.

## Implemented in current checked-in Phase 5.2 source

- Flask + Spotipy PKCE Spotify Wi-Fi mode at `/`, OAuth redirect on localhost.
- PC mode: Windows media-session adapter or Linux playerctl/MPRIS adapter; WASAPI/PipeWire audio level sampling, SSE for the glow.
- 800×480 HTML/CSS/JS interface, album-colour glow, optimistic controls, synchronized Spotify volume where the local track matches Spotify Connect; SYSTEM fallback.
- Browser `/device` simulator: four switches (previous, play/pause, next, mode switch), rotary volume steps, authenticated paired device API, state/events, album-art proxy/retry.
- Local `/pair` management page, one-time six-digit code; `--lan` optional and restricted device surface.
- `--configure` saves public Spotify client ID locally without committing it.

## Not implemented / still awaiting validation

- Actual ESP32-S3 firmware, pairing on-device, Wi-Fi provisioning, secure LAN transport, final standalone-without-PC architecture.
- Final Waveshare board SKU, connector/pinout, input expander and electrical verification, case/3-key/**push-encoder** placement. Research favors original touch SKU **25948**, but user has not selected final board. Check whether module's *full PCB* (~106.1×67.8 mm) leaves clearance behind 18 mm bottom keys and right knob.
- Real cross-platform end-to-end device simulator testing over separate physical LAN clients; Linux and Windows post-import revalidation.

## Phase 6 Rev B component-fit review checkpoint (2026-10-21)

- Manufacturer board rear drawing, PEC11 encoder drawing, KZ0087 specs, and Cherry MX plate conventions reviewed. **No measured physical part in hand and no revised enclosure dimensions approved.** Right-side I2C plug remains the principal unknown; encoder's 5mm nominal threaded bushing and 3mm conceptual face require washer/nut assembly checking; common Cherry MX clips may require ~1.5mm local plate, not 3mm.
- Added **[`docs/HARDWARE-REV-B-FIT-REVIEW.md`](HARDWARE-REV-B-FIT-REVIEW.md)**; `mechanical/revB/cad/fit_audit.py`, `fit_coupons.scad` and `test_fit_audit.py`. Fit calculator: assumed I2C extension 14mm -> 3.3mm nominal X gap; if actual extension 20mm overlaps same V/Z region, 2mm trial guard would imply 160.7mm wider-case scenario (NOT a decision).
- **Validation:** Initial assistant-side 5 Python tests passed and OpenSCAD rendered the five conceptual coupons. **User independently confirmed a clean Windows 11 PowerShell pull of `fd82d35`, successful `fit_audit.py` output for 14/17/20/25mm hypothetical cables, and all five `unittest` checks passing** (`Ran 5 tests in 0.002s / OK`). This is **Windows script execution only**, not a Windows companion runtime test, electronics or printed-part validation. The user confirmed we are **still at the design stage**, so no actual parts/coupon prints or measured assembly are available. Both existing 156mm sharp/R5 STEP variants unchanged.

## Phase 6 Rev B internal 3D packaging study — 2026-10-21 (awaiting Windows validation)

- Independent CAD-only packaging study added via `mechanical/revB/cad/internal_packaging.py`, `internal_packaging_view.scad`, `internal_packaging_assumptions.json`, synchronised OpenSCAD parameter file and `test_internal_packaging.py`. Guide: [3D packaging study](HARDWARE-REV-B-INTERNAL-PACKAGING.md). Both original 156mm sharp and R5 STEP cases remain **unchanged**.
- This study maps X/V/inward-W reference boxes onto desk-space wedge coordinates. It models provisional LCD, MX keys, encoder/terminal prism, right I2C and left USB cable envelopes, nominal screen mounting markers, AW9523B historical arbitrary position and hatch clearance; no accurate R5 shell or actual connector model.
- **User Windows validation:** eight new 3D packaging unit tests passed (8/8, 0.014s). User ran `--verify-defaults` 14mm I2C/6mm USB successfully and generated a 20mm I2C/10mm USB scenario. Hypothetical body overlap (2.7×13.2×13.1mm), terminal overlap (2.7×13.2×0.9mm), and left wall encroachments (-1mm and -5mm) matched expectations. This confirms Windows Python execution, **not** real hardware or OpenSCAD visual inspection.
- Default **assumed** 14mm I2C cable projection: 3.3mm nominal X gap to encoder; 20mm scenario produces a **2.7mm X × 13.2mm V × 13.1mm W hypothetical box overlap**. An assumed 6mm left USB cable projection reaches 1mm inside nominal side wall, suggesting a future port-opening or cable-route decision; not measured or confirmed. No case width revision authorised.

## Waveshare official 3D reference discovery — 2026-10-21

- Official [Waveshare hardware resources](https://docs.waveshare.com/ESP32-S3-Touch-LCD-4.3/Resources-And-Documents) list a [3D Drawing ZIP](https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-4.3/ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip). This could reduce guessed LCD board/USB/I2C positions. The ZIP contents, model resolution, touch SKU match and licence are **unverified**; don't assume exact connectors or dimensions.
- Added [`scripts/inspect-waveshare-3d-reference.ps1`](../scripts/inspect-waveshare-3d-reference.ps1) to download the manufacturer's ZIP **outside the repository** and list its members/size/SHA-256; optional `-Extract`. This script has not been executed on Windows yet and no third-party CAD is checked into our public repo.

- **Windows manufacturer archive inspection completed by user (2026-10-21):** `scripts/inspect-waveshare-3d-reference.ps1 -Extract` ran successfully after pulling `8a67325`. Archive path: `$HOME\Downloads\SpotifyDesk-Waveshare-Official-3D\ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip`; **ZIP size 5,677,592 bytes**, reported **SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`**; exactly one entry `esp32-s3-touch-lcd-4_3.stp` (**31,338,066 uncompressed bytes**). Extracted under adjacent `extracted\`. These are **user-reported output values**, not yet independently audited STEP geometry. Direct assistant download was unavailable. Request the **original manufacturer ZIP uploaded into the chat** to inspect full assembly, its coordinate system, connectors, SKU compatibility and whether it has usable mounting/detail geometry. Do not upload it to public GitHub or overwrite the Rev B cases without review.

## Manufacturer STEP geometry checkpoint — 2026-10-21

- User uploaded manufacturer `ESP32-S3-Touch-LCD-4in3_3D_Drawing.zip`; CRC and SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15` independently matched. Sole STEP `esp32-s3-touch-lcd-4_3.stp` 31,338,066 bytes, Creo dated 2023-12-13, **693 solids**, overall bounds **106.106 × 68.268 × 16.906mm**.
- [Detailed STEP findings](HARDWARE-WAVESHARE-STEP-INSPECTION.md) plus [`waveshare_step_reference.json`](../mechanical/revB/cad/waveshare_step_reference.json), [`manufacturer_fit_compare.py`](../mechanical/revB/cad/manufacturer_fit_compare.py), [annotated front overlay](../mechanical/revB/cad/waveshare_step_front_overlay.svg), and 10 passing local tests. This adds only *extracted named bounding measurements and tool code* to GitHub, **not** Waveshare raw STEP/ZIP.
- **Critical front-view orientation correction:** STEP +Z faces viewer; USB-C1 and USB-UART Type-C2 housings on right by encoder, H7 four-pin I2C on left by close side wall. Earlier `fit_audit.py` and `internal_packaging.py` represented mirror-imaged **hypothetical** connector sides. Manufacturer STEP measures 17.544mm bare USB-C1-to-encoder body X gap, and 5.577mm H7-to-left-inner-wall X gap. Assumed 20mm USB extension would produce 2.456×8.327×4.162mm possible box intersection; assumed 6mm H7 I2C extension reaches 0.423mm inside assumed left inner wall. Actual cables/plug paths **unmodelled**. 98×60mm standoff pitches measured in STEP; vendor revision/hole/thread not validated.
- Complete manufacturer depth is **16.906mm**, not earlier 6.8mm assumed rear LCD-depth box; align glass front W=0 as *provisional* and design case supports after mounting datum is chosen. No sharp/R5 original STEP enclosure modified, no finished printable case, no hardware ordered.

## Physical 180° board-rotation concept — 2026-10-21 (unapproved alternative)

- User's Windows 11 report independently confirmed the **STEP front-view comparator 10/10 tests** and both default (USB 14mm, I2C 6mm) and longer-cable (USB 20mm, I2C 10mm) runs; user opened generated SVG. These confirm the current *normal* view tool on Windows, **not** actual geometry fit.
- User suggested **rotate entire Waveshare module 180° within the front plane**, then rotate pixel output and capacitive touch in firmware. Waveshare docs specify **USB-C 5V power** and distinguish main USB from separate USB-to-UART debug. Physical 180° would put **main USB-C1/C2 on case LEFT** and **I2C H7 on case RIGHT**, while keeping glass outward, 156mm case, 98×60 mounts and centred keys. Firmware is not implemented/tested.
- Added [parametric side-by-side orientation study](HARDWARE-WAVESHARE-ROTATION-180-STUDY.md), `mechanical/revB/cad/orientation_180_study.py`, `test_orientation_180_study.py`, and checked-in `orientation_180_comparison.svg`. **Twelve assistant-side regression tests pass**; user Windows test/approval of the new study pending. Original sharp/R5 STEP enclosure variants and the earlier original-orientation reference remain untouched.
- **Design implications from manufacturer bounding boxes:** the main USB-C housing on left would be ~5.244mm inside nominal X=3mm inner wall; a trial 14mm outward plug extension extends **8.756mm through that nominal wall**, calling for a designed left-side access tunnel/port. H7 I2C housing on right is ~17.877mm horizontally from assumed encoder body; 20mm I2C straight-prism assumption can intersect encoder. Visible LCD window shifts down V **4.74mm**, right X **0.10mm**: existing display aperture must relocate in a *future alternative* case variant. Existing 18mm keycaps still have ~10.55mm gap to nominal visible window. Mount pitch still 98×60.
- The 180° mapping at 800×480 could use conceptual touch mapping (x,y)->(799-x,479-y), but LCD RGB/LVGL render and GT911 touch alignment/performance require actual ESP32 test. No physical parts bought and no fabrication/port-opening decision accepted.

## Rev B rotated 180° shell alternatives — 2026-10-21 (Windows math checks passed; full Windows B-rep / design approval pending)

- User Windows 11 independently ran **12/12 orientation-study unit tests (0.005s)** and generated the expected 0°/180° side-by-side reports; physically rotated USB-C LEFT / I2C RIGHT is *still a suggestion*, not final design acceptance.
- Created a **separate, independently generated pair of experimental sharp and R5-rounded CAD STEP shells**, with same 156mm width, 55° wedge, MX/encoder placements, and moved display aperture **X+0.10mm and V+4.74mm**; trial USB-C1 access passage through LEFT SIDE WALL rather than front. Nominal slot from extracted manufacturer socket housing: X=-2.000..9.244, V=36.073..49.655, W=8.889..17.051mm for **assumed** glass W=3.25mm; no actual male plug fit established.
- Added [experimental case design report](HARDWARE-REV-B-ROTATED180-CASE-PROTOTYPE.md) and `mechanical/revB/cad/{rotated_case_prototype.py,rotated_case_parameters.json,test_rotated_case_prototype.py}`. Assistant locally exported two sharp/R5 STEP solids and two B-Rep reference assemblies, imported exported shells and verified nominal bounding box **156×83.093×106.107mm**; **10 new tests pass**, including B-rep validity and actual side-wall cut removal. 2 B-Rep tests skip in Windows if optional CadQuery/Shapely are not installed.
- Experimental STEP binaries and preview are delivered as a **separate chat ZIP**; the source generator and assumptions are checked into GitHub but *not* the generated STEP binaries. Original 0° sharp/R5 CAD and ZIP remain unmodified. This **does not implement** LCD/GT911 firmware rotation, actual mounting bosses, UART opening, cable strain relief or a print-ready case.

- **Rotated-shell prototype Windows validation:** user fast-forwarded to `f186eac`, ran `test_rotated_case_prototype.py`: **10 tests discovered; 8 PASS; 2 SKIPPED** because optional CadQuery/Shapely unavailable (`test_sharp_and_rounded_are_valid_brep_solids`, `test_left_usb_cut_removes_wall_material_both_variants`). User ran `rotated_case_prototype.py --report-only` and generated SVG correctly: width 156mm, display aperture (X=13.33,V=17.09), size 95.54×54.36mm; trial left USB wall slot X=-2…9.244, V=36.073…49.655, W=8.889…17.051mm. Opened SVG command; **no explicit FreeCAD STEP review or acceptance of 180° board orientation**. Assistant-side full 10/10 (CadQuery present) remains separate evidence. No need to install CadQuery for viewing the supplied STEP ZIP.

## Rounded USB-left media-key design direction — 2026-10-21

- User **viewed the screenshot of the experimental R5 rounded 180° case** and explicitly chose **rounded corners** and **USB-C on left as preferred direction**. This is a visual design preference only, NOT physical print approval or acceptance of the tentative USB cutout. User wants to see *installed 3 media keycaps* (previous, play/pause, next icons) and volume knob, ensure MX switches/keycaps return freely, and identify a matching set of UK purchasable icons.
- Added [recessed media-control fit study](HARDWARE-REV-B-MEDIA-CONTROLS-FIT.md); new `mechanical/revB/cad/media_controls_fit_study.py`, `keycap_mount_assumptions.json`, `test_media_controls_fit_study.py` and three white-background-transparent **custom legend SVGs** under `mechanical/revB/keycaps/`. Full CAD and icon art also exported as a **separate conversation ZIP** (new R5 STEP shell and assembly featuring 3 keycap + MX switch reference envelopes, existing knob Ø15.1, top and two-state cutaway illustrations). Original rounded/flat Rev B baselines and prior R180 prototype untouched.
- Trial **18mm cap, 19.2mm cap-through-well, 0.6mm lateral side gap, 2mm cap above front at rest, 4mm stroke, 8mm cap body depth, 1.5mm clip plate at W=11.5mm** results in simplified 1.5mm skirt-to-plate gap at full travel; neither actual keycap skirt/inner MX stem engagement nor printer tolerances verified. Integrated conceptual collar 23.2mm wide, retains centred 30mm pitch and avoids nominal screen module V projection by 3.6mm. **Not fabrication ready.**
- Initial assistant-side tests: **15/15 pass**, including two CadQuery/STEP generation/reimport checks. **User Windows 11 validation on `9322af3`: 15 tests discovered, 13 PASS, 2 SKIPPED** (CadQuery/Shapely unavailable). `media_controls_fit_study.py --report-only` ran successfully (cap 2mm proud at rest, 8mm assumed body depth, 4mm nominal stroke, 19.2mm well, 0.6mm side gap, W=11.5mm retaining plate, 1.5mm full-travel nominal skirt-to-plate margin); both SVGs opened. Does not validate physical MX/keycap fit. A vendor individual **1U MX PBT custom Cherry cap at £8 each** was found at [Krome Keycaps](https://www.kromekeycaps.com/products/create-your-own-custom-cherry-keycap), so matching white-on-black custom symbols could cost ≈£24 before shipping if colour options allow; **no purchase or color/profile confirmed**. Also consider Krome OEM and Tech Toppers; media SVGs provided for quotes.

## Raised-vs-recessed appearance and lower-price keycap search — 2026-10-21

- User requested **visually raised keycaps** next to current 2mm proud-at-rest design, and questioned prior custom cap budget. Created side-by-side **illustrative** comparison of 2mm recessed versus nominal 6mm raised, with rounded USB-left body unchanged. **6mm is an appearance exploration**, not a tested B-Rep variant or measured mechanical clearance. Awaiting user preference; do not revise current CAD before selection.
- UK price research: [Mechbox blank 1U PBT four-pack £1.56](https://mechbox.co.uk/products/blank-wasd-keys) (requires custom legends, delivery extra); [Tech Toppers four custom MX PBT caps £14.95](https://www.techtoppers.co.uk/products/wasd-custom-keycaps-editor) (+ £3.95 standard UK delivery ≈£18.90, print black/white colour and cap profile unverified); [Krome individual Cherry 1U caps £8 each](https://www.kromekeycaps.com/products/create-your-own-custom-cherry-keycap) (three ~£24 + delivery). Exact ready-printed matching trio with confirmed UK stock not identified; no purchase authorised.

## Rounded USB-left 2mm/4mm/6mm actual CAD comparison — 2026-10-21 (Windows validation pending)

- User explicitly requested *actual CAD designs for all three keycap heights* after the earlier 2/4/6mm styling preview. Delivered a verified separate ZIP: `Spotify_Desk_RevB_R5_2mm_4mm_6mm_Media_CAD.zip`, which contains **three different single-solid rounded R5 STEP cases and three cap/switch/knob multibody STEP assemblies**, plus dimensioned vector and PNG drawings, JSON reports and offline-source folder.
- Three candidate **rest heights** above the same face: **2mm**, **4mm**, **6mm**. Rather than shifting *only* illustrative keycaps, the actual **1.5mm MX switch-retainer plate top W** is relocated **11.5mm / 9.5mm / 7.5mm inward respectively**, preserving the mathematical **3.3mm nominal stem projection overlap** and **1.5mm cap-skirt-to-plate gap at assumed full 4mm travel**. Keycap width 18mm, wells 19.2mm, wall clearance 0.6mm each side and cap depth 8mm remain **assumed**. At full travel cap tops: 2mm *below* / flush / 2mm *above* the face.
- Source (no prior CAD overwritten): `mechanical/revB/cad/media_controls_height_variants.py`, `keycap_height_variant_parameters.json`, `test_media_controls_height_variants.py`, and [detailed CAD study](HARDWARE-REV-B-KEYCAP-HEIGHT-CAD-COMPARISON.md), plus two checked-in comparison SVGs. Assistant-side **20/20 new tests PASS** including true three-height CadQuery B-rep generation, valid single-solid STEP roundtrip, three named multibody assemblies; 2mm case B-Rep volume matches preceding 2mm model exactly. **New user's Windows tests are pending**; 2 tests will skip if optional CadQuery/Shapely missing.
- Rounded corners and USB-left remain accepted **visual direction**, not fabrication approval. No final height selected. Chosen keycap product geometry, snap fit, strength, PCB/wiring, male USB plug and ESP32 display/touch rotation still open.

## 4mm chosen and final keycap procurement review — 2026-10-21

- User independently ran three-height Python/geometry tests after pulling `3b3c7f0`: **18 PASS / 2 SKIP (optional CadQuery/Shapely)** out of 20, and successfully generated all three `--report-only` outputs (MX plate W=11.5/9.5/7.5mm). **User chose 4mm resting keycap height** as the preferred physical CAD design. Original 2/6mm alternatives and reference R5/USB-left CAD remain preserved; selection is **not a physical fit or print signoff**.
- Final vendor comparison in [KEYCAP-FINAL-SHORTLIST.md](KEYCAP-FINAL-SHORTLIST.md): matching **⏮ / ⏯ / ⏭** white-on-black 1U PBT MX caps; **primary provisional supplier Tech Toppers 4 custom caps £14.95 + £3.95 standard UK shipping**, pending confirmation of opaque white legends on black plastic (normal dye sub can't deposit white on black), consistent profile/row, cap skirt and MX socket dimensions; **blank Mechbox 4 caps £1.56 + shipping** as fit-test/DIY alternative; Krome UV-printed 3 × £8 = £24 + shipping if suitable. No exact ready-printed matching trio verified. No specific cap ordered/selected beyond candidate.

## Tech Toppers chatbot follow-up — 2026-10-21

- User provided screenshot of completed custom WASD 4-key editor/cart with desired **black keycap colour #000000, white symbols** (previous, play/pause, next, alternate single play) and **£14.95 basket before shipping**. Generic vendor chatbot says **Cherry profile/MX-style crosses**, WASD typically 1U but advises independent confirmation; it says **dye sublimation** may vary in colour and clarity and urges written pre-production requirement notification. **It did not confirm that white artwork on a black-looking finished keycap is achievable**, give actual dimensions or verify that all four WASD keys are the same sculpted Cherry row. See [supplier pre-check and unresolved questions](KEYCAP-FINAL-SHORTLIST.md). Do not treat placing item in cart as purchase or technical approval.
- Before order: ask human support about black/white achievable printing/reverse sublimation method and finished sample, consistency of Cherry row/height across three side-by-side keys, underside skirt X/Y, cap depth, stem engagement. Current **4mm** raised-at-rest STEP case still uses approximate **18mm cap / 19.2mm well / 9.5mm plate top**, not confirmed by Tech Toppers.

## New 4mm R5 underside cover & LCD support mechanical prototype — 2026-10-23

- While waiting for a **human Tech Toppers response**, created a **new, separate** R5 rounded, USB-left, Waveshare physically rotated 180°, **4mm media cap rest-height** engineering variant. The retained CAD is not overwritten. A zipped offline CAD/source/test package (`Spotify_Desk_RevB_R5_4mm_Rear_Cover_Screen_Mount_Study.zip`) was created and given in chat (four valid STEP outputs, diagrams and source code). Detailed [design study](HARDWARE-REV-B-REAR-COVER-AND-SCREEN-MOUNTS.md).
- Used the pre-existing **underside** access cut (X11…145, desk Y12…71.093) as a hatch, not a vertical rear wall. Added **a separately removable 2mm lid**, theoretical 0.4mm perimeter gap, inward seating lip, four tied-in screw bosses and nominal M2.5 holes. Four case-attached screen cantilevers lead to manufacturer STEP **98×60mm** standoffs at front-face X=12.05/110.05, V=11.8/71.8; trial bearing W15.85mm. Designed around 2023 STEP **reference**, not a purchased model.
- **Assistant-side 16 new tests all passed**, including CAD B-Rep STEP export and independent reimport; case + cover are valid single solids with **0.0mm³** interpenetration. No user Windows tests yet, no user acceptance and no full manufacturer-board collision or screen insertion simulation. Critical access issue: underside opening Y width ~59.1mm, Waveshare full module face height ~68mm; insertion at an angle and rear screw-tool reach remain **open**.
- **Publishing status updated:** generator, editable JSON parameters, regression tests and 2 SVG reference drawings are **now also committed natively** in `mechanical/revB/cad/` and byte-for-byte verified against generated source. The full four-STEP binary CAD package remains a separate conversation ZIP; original source CAD unchanged. User Windows test still pending.

## Current next action

1. **Review the experimental removable underside cover/LCD support model** in [the 4mm R5 engineering note](HARDWARE-REV-B-REAR-COVER-AND-SCREEN-MOUNTS.md) and chat ZIP; check **physical insertion route and tool access** next, then refine mount supports against exact Waveshare board geometry. Await human Tech Toppers answer before settling cap dimensions or purchasing. The new mount generator and tests are now committed to GitHub and runnable after `git pull` (full regeneration additionally needs optional CadQuery/Shapely).
2. Use the [Rev B report](HARDWARE-WEDGE-REV-B-CAD.md), [coordinate notes](../mechanical/revB/README.md) and [checked-in CAD package](../mechanical/revB/cad/) as the source for mechanical edits. Rev A's 165mm OpenSCAD model is historical.
3. **Measure exact owned MX switches and caps**, screen mounting-hole bores, left USB-C service locations, right I2C plug and bend radius, true AW9523B and encoder/knob Z/depth, then perform real 3D collision analysis.
4. **Case engineering** still needed: 3D printable mounting lips and screw bosses, bottom-access hatch fasteners, key/switch tolerances and support, USB ports, screen and antenna keepouts, knob push travel and KZ0087 grub-screw access. Current STEP shell cutouts are placeholders.
5. **Electrical** still needed: AW9523B module RESET/pullup and safe 3.3V connector mapping, protected six input signals and encoder pulse tracking. If layout/electrical tests succeed, *then* consider compact carrier PCB. Firmware unchanged.

## Relevant project files (from Phase 5.2 source)

- `desk_ui.py`, `device_bridge.py`
- `windows_companion.py`, `linux_companion.py`
- `static/ui.js`, `static/ui.css`, `static/device.js`, `static/device.css`
- `templates/index.html`, `templates/device.html`, `templates/pair.html`
- `tests/`, `requirements-ui.txt`, `requirements-windows.txt`
- `docs/ROADMAP.md`, `docs/DECISIONS.md`, **`docs/DESIGN.md`**, **`mechanical/` (editable front + wedge CAD envelopes)**, `docs/HARDWARE.md`, **`docs/HARDWARE-SHORTLIST.md`**, **`docs/HARDWARE-PRE-PURCHASE-CHECK.md`**, **`docs/HARDWARE-ELECTRICAL-REVIEW.md`**, **`docs/HARDWARE-MECHANICAL-LAYOUT-STUDY.md`**, `docs/HARDWARE-RESEARCH.md`, `docs/HARDWARE-COMPARISON.md`, `docs/CHATGPT-WORKFLOW.md`
- One-time import scripts: `scripts/import-phase5-2.ps1` (already run) and `scripts/archive-local-phases.ps1` (already run). Historical files: `archives/phase-zips/` and `docs/history/ARCHIVED-PHASE-ZIPS.md` (16 verified archives and their original/stored hashes).

## Recent meaningful commits

- `7172c2e` — accepted Phase 5.2 source imported into `main` (**implementation checkpoint**).
- `234a976` — sanitize generated Python bytecode when preserving old ZIPs.
- `f781506` — all 16 historical ZIP archives and checksum manifest pushed and verified.
- `196a66a` — Phase 6 WaveShare board/expander manufacturer-source research (documentation only; no application or firmware changed).
- `5833f0e` — Phase 6 extended screen/input-expander comparison; includes AW9523 and QUAD seesaw ideas (documentation only).
- 2026-10-20 user-accepted physical design mapping: **3 MX keys + push encoder (turn volume, push PC/Wi-Fi)**; docs-only. No fourth physical MX key.
- `cc6c4b6` — proposed SKU-specific Waveshare / encoder / AW9523B parts shortlist and UK price estimates (documentation only).
- `bab9e96` — manufacturer PDF-based pre-purchase mechanical, voltage and input-safety checklist (documentation only).
- `3f7d768` — manufacturer chip datasheet electrical review + preliminary protected six-input network and documented unresolved module schematic verification (docs only).
- `e89fa20` — faceplate 150×105 vs 165×110 mechanical study, screen I2C/right-hand knob cable conflict, and manufacturer-supported 7 mm exposed encoder shaft correction (documentation only).
- 2026-10-20 static CAD envelope milestone: source assets added under `mechanical/`; 3-page A3 PDF/SVG/DXF bundle delivered as a conversation attachment. No 3D-print manufacturing geometry or runtime tests; the latest Git source baseline remains unchanged.
- 2026-10-20: wedge 3D Rev A packaging proposal + editable SCAD checked in to mechanical/, separate annotated rendered concept ZIP in conversation; purely geometric.
- 2026-10-21: **Rev B** 156mm wedge with centred MX keys; matched sharp/R5 STEP solids, assemblies, DXFs, A3 PDF and rendered previews produced. User pushed CAD ZIP plus all 13 extracted assets in `6ae257e`; remote blobs verified byte-for-byte. No physical test or software implementation change.
- Documentation-only commits after this checkpoint are not evidence of newer runtime implementation.

## Unresolved issues / deferred

- Current Rev B trial is **156×83.09×106.11 mm** (W×D×H), 55° slope and 16mm chin/20mm roof; width is reduced from Rev A 165mm. Proposed R5 round is an *option*, not a final user-accepted finish. 14mm assumed I2C corridor + encoder body leaves just 3.3mm theoretical lateral gap, real fit unknown.
- Adafruit 377 included cap rejected aesthetically; **KZ0087 provisionally selected** to match low-profile RK M75 styling. Its 12.4 mm maximum insertion is shorter than Adafruit shaft's nominal 15 mm, so mechanical fit/encoder push still require validation. Encoder electronics unchanged.
- The Waveshare AW9523B silicon **defaults GPIO to outputs**; at the anticipated 0x58 straps P0 starts low open-drain, but **RESET has internal 100k pull-down**, so verify module's external reset pull-up and boot timing. Preliminary six-input 22k pullups + 1k series are **not an approved wiring schematic**. Module full diagram still inaccessible even though an indexed text copy identifies R1–R4 10k. See `docs/HARDWARE-ELECTRICAL-REVIEW.md`.
- Part availability is variable. The Adafruit AW9523 PID 4886 module was shown sold out in one checked supplier listing; Waveshare AW9523B SKU 22132 is a proposed same-chip breakout, not necessarily plug-and-play. User has not ordered hardware.
- GPIO/I²C warning: onboard CH422G reserves `0x20–0x27` and `0x30–0x3F`, so default MCP23017 (0x20+) and Adafruit **single** I²C rotary breakout (0x36–0x3D) conflict. AW9523 (0x58) and Adafruit **QUAD** seesaw breakout (0x49) are proposed alternatives; QUAD off-label 3 MX + encoder push switch contact use needs schematic/bench checks due to possible duplicated pin listing. No purchase approval.
- The device simulator can poll `/api/device/state` repeatedly even with SSE; optimization is deferred, not a blocker.
- A test emitted a minor `ResourceWarning` about a stylesheet file handle.
- Linux `playerctl -l` previously found no player in an SSH session, yet paired device state and Spotify API worked; avoid claiming native MPRIS parity without a local player test.
- Desktop Flask server is a development prototype, not an internet-facing deployment.
- Final independent Wi-Fi mode on physical hardware still needs a design decision: do not assume Spotify embedded playback or safe on-device OAuth storage is possible.

## Workflow rules

See `docs/CHATGPT-WORKFLOW.md`. Read repository state before changes. Distinguish implemented, statically tested, runtime-tested and accepted. Preserve 800×480 UI and accepted playback behavior. Record actual ad-hoc work without inventing roadmap numbers. Commit code directly through GitHub when permitted and update this handoff after each user-accepted task. Keep passwords, OAuth tokens, pairing bearer tokens and host-specific config out of Git.

# Changelog / version history

## Weather v1.0: Bournemouth and three-day forecast — 2026-10-25

- After user accepted final Glucose layout, Weather input/city search and browser-saved location were removed. Fixed Bournemouth town-centre coordinates (50.72098, -1.87669) and Europe/London timezone; direct Open-Meteo call without geocoding.

- Replaced NEXT HOURS five hourly tiles with a three-day weather forecast: Today, Tomorrow and following weekday, showing condition, high and low temperatures and daily maximum chance of precipitation. Retained current weather stats, Home weather shortcut, 15-minute refresh and offline error fallback.

- Compact 3-column day cards to fit within 800×480. Added tests/check_weather_daily.cjs offline DOM fixture and expanded tests/test_dashboard_preview.py checks. Mocked JS test passed assistant-side; awaiting actual Windows user screenshot. Dashboard script/CSS versioned v1.0. No media, glucose data or physical hardware changes.

## Glucose v0.9: Match graph top edge with LIVE square — 2026-10-25

- Visual follow-up: v0.8 square reading tile and plot were not quite top-aligned because GLUCOSE TREND and chart controls contributed to right-column height.
- Scoped BOTH chart heading above the plot using absolute positioning, with a centred plot column; restores normal stacked heading behaviour at narrow widths. Graph scale, real CGM readings, target band, safety labels, and Spotify remain unchanged. CSS cache v0.9; static regression test added. Windows screenshot acceptance pending.

## Experimental Spotify-style side-by-side glucose BOTH layout — 2026-10-25 (v0.8)

- User provided a two-column Figma concept: LIVE reading in a square analogous to Spotify album art, time graph in the right column analogous to playback details. LIVE-only and GRAPH-only retained.

- Added structural layout wrappers around the existing reading and chart, scope-limited CSS grid for BOTH with a ~218px square tile and flexible plot, and responsive narrow-screen stacking. Retains current Gluroo reading, trend, timestamp, 4–7 target shading, time range and Auto/Full scale controls. Background and Spotify media player untouched.

- Chart SVG renderer now receives the actual chart column width and draws numerically equivalent lines/time labels within that coordinate system, avoiding horizontally stretched/squashed values. ResizeObserver redraws on layout width changes; test fixture covers both compact and wide geometry. Static V8 tests passed, user runtime visual testing pending.

- Browser cache versions v0.8. No health data, credentials, backend API or actual device changes.

## Glucose v0.7: Whole-number AUTO chart ticks — 2026-10-25

- AUTO now uses default 3–12 mmol/L with labels 3, 4.0, 7.0, 9, 12 rather than fractional quartiles such as 9.6 or padded floor 2.5. 4/7 shaded reference guides remain. Expand if actual reading is below 3 or above 12.

- Capped AUTO at five labels, 15 SVG px separation and 11px tick font, maintaining readability. FULL remains 3–21 with ticks every 3, including extreme-readings extension.

- Added JS test cases for typical chart, no overlapping labels, below/above baseline and extreme data. v0.7 chart script cache; no health data or credentials committed. Implementation tested by assistant JS runner but Windows runtime UI acceptance pending.

## Glucose v0.6: Libre 3–21 full scale and readable AUTO ticks — 2026-10-25

- User Windows screenshots verified LIVE, GRAPH and BOTH layouts and exposed two chart-axis issues: FULL stretched to 40 mmol/L rather than matching Libre's 21, and AUTO labels near 7.0 collided in longer plots.
- FULL now uses **3–21 mmol/L** with labels every three units under normal conditions; extends safely outside that span for extreme readings rather than clipping. Automatic scale preserves target-band references and skips crowded Y labels (minimum 20 px separation). Always draws 4–7 zone boundary lines, including FULL where axis tick labels are multiples of three.
- Added regressions for tick sequence, auto-label separation and extreme-value behavior. Synthetic JS fixture checks passed; user runtime acceptance is pending. HTML cache versions: chart v0.6; dashboard JS v0.6. No real CGM data or credentials committed.

This is **historical milestone tracking**, not a separate implementation branch for each ZIP. The accepted Phase 5.2 source is committed at `7172c2e`; historical ZIPs are reference snapshots only. Prefer Git commits, tags and releases for future work rather than duplicated source folders.

## Live CGM feed via Gluroo / Nightscout-compatible HTTPS — 2026-10-25## Glucose Libre-style timeline, target band and 3 layouts — 2026-10-25 (awaiting UI acceptance)

- Added **real local clock labels** inside glucose time-series plot, **shaded 4–7 mmol/L** preferred graph band (not an alarm setting), automatically zoomed Y-axis plus full-range option, end marker, gap-aware traces and 1h/3h/6h/12h/24h range buttons. Source data unchanged from existing Gluroo live reader. The API offers at most ~730 records across ~24h, so plots may have partial coverage.
- Replaced top-right PC/Wi-Fi mode buttons **visually on Glucose only** with **LIVE / GRAPH / BOTH** layout selector. Restored original mode controls automatically on other pages, without altering underlying Spotify functions. Live-only focuses on one number, Graph-only expands graph, Both combines.
- Added pure `static/glucose-chart.js` renderer and synthetic test fixture `tests/check_glucose_chart.cjs`; updated dashboard and device bridge tests; cache version bumped to v0.5. No medical data/credentials added. Assistant-side JS parser and chart assertion checks passed; Windows runtime screenshots and user acceptance outstanding.

## Spotify-style minimal glucose dashboard — 2026-10-25 (awaiting UI acceptance)
- Followed Windows screenshot confirmation of real Gluroo readings in paired simulator and six passing backend tests; no private CGM readings or Gluroo credentials recorded.
- Simplified only `/device` Glucose view: emphasized large mmol/L number, distinct trend arrow, compact timestamp, clear LIVE/STALE/OFFLINE state, smaller single safety footer, minimal trend graph with reduced grid and a highlighted latest point, 3/6/12h controls. Dynamic active-page name corrects the header suffix; Spotify playback logic preserved.
- Static/source regression tests expanded, browser CSS/JS cache versions bumped to v0.4. **User visual runtime acceptance pending.**


- Added opt-in local-only live glucose bridge, configured through PowerShell environment variables, not stored in the repo. Gluroo supports LibreLinkUp follower data plus an experimental documented Nightscout-compatible API. Python service enforces HTTPS, secret-header access, 150s+ polling, rate-limit handling, freshness checks and unit conversion. Browser auto-displays a current-received reading, trend arrow, time-series chart or explicit STALE / OFFLINE state (no substituted sample data).
- Added localhost-only, paired-bearer-authenticated `/api/device/glucose`; route excluded from existing HTTP LAN allowlist. No CGM data available to real ESP32 devices through this prototype transport. Added `tests/test_glucose_live.py`; real upstream/GlucoView/Gluroo account validation pending. Full account setup and privacy warnings in `docs/GLUCOSE-LIVE.md`.

## LibreView historical CSV browser importer (pending user testing) — 2026-10-25
- Added browser-local, file-only LibreView CSV/TSV importer for the glucose graph: historic record type 0, explicit date-order choice, unit conversion, 3/6/12h history views, timestamp labels, discontinuous line gaps, Clear action. No Abbott login or network API, no glucose upload, no real-time values; explicitly **HISTORY · NOT LIVE**. Restricted to simulator views hosted on 127.0.0.1/localhost on the importing PC. Existing physical media controls and Spotify player preserved.
- Added pure JS parser and synthetic offline assertions, updated Python static/allowlist tests and cache versions. Assistant-side parser assertions and JS parsing passed; **Windows browser runtime tests for CSV import are pending**.
- Manual LibreView Glucose History CSV download is documented in `docs/DASHBOARDS.md`. An unofficial automated LibreLinkUp integration is intentionally not included pending lawful and secure integration research.

## Multi-dashboard browser preview, Windows visual validation — 2026-10-25
- User pulled additive Home / Spotify / Weather / sample Glucose `/device` preview through `16d78d0`, installed a Windows Python 3.13 virtual environment and dependencies, and provided screenshots of all four screens. Browser device state showed `PC · Paired`/CONNECTED; Home clock and summary rendered, Bournemouth weather retrieved real Open-Meteo data (11°C, 5 hourly tiles in sample screenshot), glucose page showed labelled mock graph with no live value. User indicated preview works.
- `node --check` and four dashboard-specific Python checks passed, but the **full Windows suite was 42/44 passing**; two pre-existing Linux-only companion tests error on Windows (`KeyError: has_playback`). Nonfatal test file-handle ResourceWarnings remain. Spotify PC playback/buttons, all glucose chart range buttons, Omarchy and ESP32 not freshly runtime tested. The original `/` Spotify OAuth returned `client_id: Invalid` in a separate flow; resolve developer app ID/status later.
- Documentation/checkpoint update only; no additional dashboard/firmware code or real Libre 2 Plus integration in this entry.

## Removable underside hatch and Waveshare LCD mounting reference — 2026-10-23
- Generated new R5 4mm media-control case STEP with screen support cantilevers, rear/underside seating lip, four attached screw bosses and **separate 2mm lift-out underside lid STEP** with 0.4mm nominal edge allowance; both installed and exploded assembly STEP outputs in separate chat ZIP.
- Screen stand-off targets from manufacturer's actual 2023 reference: 98×60mm pitch, nominal contact W15.85mm; candidate M2.5 lid/screen fasteners require part-specific pilot/strength verification. **16 assistant-side tests pass** including actual STEP CAD validity and zero lid/case solid overlap. Not print/fabrication approved; board installation through underside hatch and screw access unproven.
- CAD generator, editable parameters, 16 tests and 2 vector coordinate drawings subsequently checked into `mechanical/revB/cad/` after transfer recovery, with source Git blob hashes independently verified. Full STEP outputs remain separately downloadable; original 4mm keycap CAD and earlier baselines unchanged.

## Preferred 4mm MX cap design and keycap procurement research — 2026-10-21
- User pulled `3b3c7f0`, independently ran 20 geometry/CAD study tests on Windows (**18 passed, 2 skipped** for optional CadQuery/Shapely), and generated reports for 2/4/6mm. **User selected 4mm resting cap height**, with the assumed 9.5mm inward retainer plate. No physical test or print approval.
- Final UK purchasing review covers Tech Toppers 4× custom MX PBT £14.95 + £3.95 standard UK delivery (requires black/white reverse dye-sub/print confirmation), Mechbox 4× blank black OEM MX PBT £1.56 + shipping, Krome 3 individually UV-printed Cherry PBT at £8 each. No guaranteed matching off-the-shelf printed trio was located; requested stem, skirt and print-method confirmations remain before any purchase or CAD dimensional lock.

## Independent 2/4/6mm keycap-height rounded enclosure STEP designs — 2026-10-21
- User requested actual CAD for all three cap rest heights. Generated **3 separate R5/USB-left single-solid case STEP** and **3 cap/knob/MX-reference assembly STEP**, with dimensioned front/section SVGs, CAD-derived isometric previews, report, reproducible source and offline ZIP.
- Switch support top W adjusted 11.5/9.5/7.5mm for 2/4/6mm caps to preserve mathematical stem projection and 1.5mm full-press skirt-to-retainer margin; front, USB, knob and screen positions unchanged. Exact cap profile/stem and print fit not proven.
- **20 new assistant-side tests passed** including actual CadQuery roundtrips of all six STEP files; 2mm shell volume identical to preceding study. User Windows test and choice of height pending; no original CAD replaced.

## Media-cap Windows tests, raised styling and cheaper supplier options — 2026-10-21
- User pulled `9322af3` and passed 13 of 15 tests on Windows, with two optional CadQuery B-Rep tests skipped. Both overview and mechanical cross-section generated/opened. Assistant full 15/15 had passed earlier independently.
- Created an illustrative **2mm recessed vs 6mm raised-at-rest** media-cap appearance comparison; 6mm not yet recalculated as mechanical design, 2mm experimental case unchanged.
- Identified cheaper MX cap options: Mechbox 4 blank black 1U PBT caps £1.56 (DIY legends), Tech Toppers 4 custom 1U MX caps £14.95 + £3.95 standard delivery, compared to Krome 3 custom singles £24 + delivery. Suitable dye-sub white on black and true cap measurements are unverified; no order placed.

## Rounded R180 media keycaps and recessed MX retention study — 2026-10-21
- User visually preferred R5 rounded enclosure and USB-left physical orientation; asked to see the three playback icon keycaps and knob and evaluate switch recess/travel before purchasing.
- Produced independent rounded STEP CAD with three 19.2mm cap wells, behind-face 1.5mm nominal plate retaining 14mm square MX switches and an exploded reference assembly with three 18mm caps, white icons and Ø15.1mm knob. 15 assistant-side Python/CadQuery tests passed, not a physical fit check.
- Published three printable original white SVG legend drafts (previous/play-pause/next), configuration and technical drawing. Krome Keycaps custom Cherry 1U PBT candidate listed £8 each (≈£24 three + delivery), colour/profile and actual cap underside need confirmation. Generated STEP outputs remain in separate conversation ZIP; legacy CAD unmodified.

## Rotated-180 Rev B Windows test checkpoint — 2026-10-21
- User pulled commit `f186eac` and ran rotated prototype tests on Windows 11: **8 passed, 2 skipped** because CadQuery/Shapely absent (solid validity and true cut subtraction). Assistant B-Rep tests passed independently, not revalidated on Windows.
- User generated front overview SVG with anticipated 156mm geometry, (13.33,17.09) display aperture origin and experimental left USB slot, and opened via `Invoke-Item`. No confirmation of user FreeCAD inspection or preference decision yet.

## Rotated-180 Rev B experimental sharp and R5 STEP case models — 2026-10-21
- User passed 12/12 rotation-comparison tests on Windows; assistant developed separate 180° experimental sharp and R5-rounded CAD enclosure solids, front aperture moved +4.74mm down and trial USB-C1 access slot cut through left wall; nominal 156×83.093×106.107mm external dimensions and three keys retained.
- Added reproducible CadQuery generator, editable assumptions, 10 assistant-passing regression checks and engineering-gate documentation. Exported STEP files and independent reference assemblies provided in chat ZIP, not committed as third-party source or silently substituted for original Rev B CAD.
- **No approval** of the physical orientation/port choice or actual cable, standoff, encoder, touch, firmware and printable fit; all remain open.

## Rev B proposed 180-degree Waveshare mounting alternative — 2026-10-21
- User passed 10/10 manufacturer STEP normal-orientation comparator tests on Windows and produced both assumption scenarios; suggested turning whole board 180° to move USB power port to left side of case.
- Verified Waveshare publishes 5V USB-C input and separate USB vs USB-UART functions; added a **separate** side-by-side X/V/W orientation study, SVG and 12 locally passing tests. In 180° layout, USB becomes left and I2C right; visible window should shift 4.74mm down to align the existing display area; USB service tunnel/harness remains an open requirement.
- Design alternative pending user acceptance and real LVGL/GT911 firmware rotation test. **Both existing Rev B sharp/R5 STEP files unchanged.**

## Manufacturer Waveshare STEP analysed and front/rear corrected — 2026-10-21
- Uploaded original Waveshare source ZIP independently hashed/CRC-verified; OCCT imported the single 31.34MB Creo STEP and located 693 solid bodies, the two USB-C sockets, 4-pin I2C socket, four M2.5-named standoffs and actual overall 3D assembly bounds.
- Corrected earlier **front-vs-rear mirrored connector placement**: front USB-C1/C2 RIGHT toward encoder, I2C four-pin LEFT toward inner left sidewall. Archived old scenario scripts are explicitly labelled historical hypotheses.
- Added extracted measured part boxes (no third-party CAD redistribution), front-layout SVG, pure Python cable/shell clearance scenarios and 10 passing local tests. Neither sharp nor rounded Rev B STEP design has been modified; no physical fit or Windows execution of the new tool confirmed.

## Manufacturer STEP download confirmed on Windows — 2026-10-21
- User ran the new PowerShell inspection helper after successful Git pull; downloaded official Waveshare ZIP (5,677,592 bytes, SHA-256 `8721FAC43DE47B35771C438829A3251A4C0723227D83696B5517EFE7D854DE15`) and extracted the sole STEP `esp32-s3-touch-lcd-4_3.stp` (31,338,066 bytes).
- ZIP member listing is now confirmed by user PowerShell output, but **the actual STEP model has not been opened or analysed**, touch SKU 25948/PCB revision alignment remains open. Manufacturer bytes stay outside GitHub pending rights/fit review.

## Rev B Windows tests and official manufacturer CAD discovery — 2026-10-21
- User confirmed `internal_packaging.py` generates expected nominal and expanded cable scenarios on Windows; **8/8 Python tests passed**. No physical assembly, electrical or OpenSCAD user visual test accepted.
- Waveshare publishes an official 3D Drawing ZIP for the original ESP32-S3-Touch-LCD-4.3 model. Added a PowerShell archive downloader and listing tool with SHA-256; keeping manufacturer models separate from the repository until exact contents, revisions and distribution terms are checked.

## Rev B internal packaging model (design-only) — 2026-10-21
- Added Python standard-library 3D envelope collision report, configurable right I2C and left USB scenarios, OpenSCAD reference scene, assumptions JSON, SCAD parameters and eight tests.
- Assistant environment: 8 Python tests passed and OpenSCAD CGAL generated geometry without errors. Original sharp/R5 STEP reference designs unchanged; user Windows validation still pending.
- Trial 20mm I2C reach overlaps a nominal encoder reference prism; provisional left USB extension enters nominal wall. These are **unmeasured box assumptions**, not physical collisions or a dimension decision.

## Rev B Windows fit-audit validation — 2026-10-21
- User pulled commit `fd82d35` on Windows 11 and ran the Rev B Python clearance auditor successfully; 14/17/20/25mm scenarios reported the expected nominal 3.3/0.3/−2.7/−7.7mm gaps.
- User's Windows 11 Python ran all **5 fit-audit unit tests successfully**; this validates the calculation tooling on Windows, **not** physical CAD fit or the desktop media companion.
- User explicitly confirmed the project is **still designing**. Next mechanical task is parameterized 3D packaging/keep-out exploration using clearly marked assumptions; no real-world measurement or hardware purchase claimed.

## Rev B component-fit preparation — 2026-10-21
- Reviewed manufacturer LCD rear board/connectors, Bourns PEC11 encoder mounting geometry, KZ0087 specs and standard Cherry MX plate cutouts.
- Added a pure-Python cable-clearance scenario audit, explanatory vector overlay export, five OpenSCAD mounting coupons, five regression tests and a measured-fit checklist. The script retains original 156mm Rev B dimensions; no existing STEP assemblies changed.
- Static validation: five Python tests passed; OpenSCAD produced valid coupon geometry. No measurements, physical parts, print trials or final manufacturer tolerance confirmation yet.

## Rev B CAD package archived on GitHub — 2026-10-21
- User pushed [`6ae257e`](https://github.com/Cousinsuke/Spotify-Desk/commit/6ae257e2ce01256b320417fd21e14d9339bd9ed1) containing the original Rev B ZIP and 13 extracted STEP, DXF, PDF, PNG, generator and metadata files to `mechanical/revB/`.
- Verified that all 13 GitHub blobs match the original ZIP's entries byte-for-byte. Added `.gitattributes` to prevent Windows CRLF conversion of CAD and binary data on future checkout.
- Both sharp and R5-rounded variants retained as concept geometry; no final manufacturing signoff, wiring or firmware test.

## Repository migration — 2026-10-20
- Imported exact accepted Phase 5.2 desktop/simulator source into `main`: commit `7172c2e`.
- Uploaded 16 historical ZIP archives with SHA-256 manifest: commit `f781506`.
- Omitted 2 generated Python bytecode/cache entries from archived Phase 2.2 ZIP; originals in Downloads unchanged.
- GitHub source and archives verified; this housekeeping work is not a new software phase or hardware runtime validation.

## Phase 5.2 — Last user-accepted prototype on Omarchy (2026-10-20)
- PC artwork reliability: preserve direct HTTPS cover URLs from MPRIS; use local thumbnail proxy only when applicable.
- Validate artwork key against current track; bounded retries and fallback cover; delayed Windows artwork retry.
- 39 Python tests passed on Omarchy; user confirmed issue resolved.
- Windows Phase 5.2 specific retest still to do.

## Phase 5.1 — Simulator design restoration
- Restored established 800×480 screen layout, album glow, proper speaker icon/slider and optimistic playback/skip feedback.
- Preserved device pairing and K1–K4 + encoder simulation.

## Phase 5.0 — Virtual hardware and pairing
- Added `/device`, `/pair`, pairing tokens, authenticated state/control/events bridge and optional restricted `--lan`.
- Public Spotify Client ID persisted locally via `--configure`.

## Phase 4.2 — Spotify volume routing
- Synchronized PC Spotify volume with matching Spotify Connect playback.
- SYSTEM fallback for other/unmatched player sessions; Windows and Omarchy user-accepted.

## Phase 4.1 — Linux companion
- MPRIS/playerctl, PipeWire default volume and monitor integration; initial Omarchy tests.

## Phase 3.3 — Windows audio stream
- Replaced high-frequency HTTP audio polling with SSE stream; Windows user-accepted.

## Phase 3.1–3.2 — Windows companion & dependencies
- Native media sessions, playback, output volume and audio signal capture; added missing WinRT Collections dependency.

## Phase 2.1–2.7 — Browser UI
- 800×480 music player, Spotify controls, skip feedback, audio/album-colour glow, and glow confinement.

## Phase 1 — Initial prototype
- Spotify developer application using PKCE; basic browser API controls.

## Future versioning

The Phase 5.2 source checkpoint exists at `7172c2e` and was imported with a checksum-verified source archive. Consider tagging only after confirming platform tests from the checked-in repository. For future changes, use normal Git history and release artifacts instead of reconstructions of older snapshots.

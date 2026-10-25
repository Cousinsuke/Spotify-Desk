# Multi-dashboard browser preview — Home, Weather and Glucose

**Status (2026-10-25):** Implemented and **visually/user validated on Windows 11** in the `/device` browser simulator. The user provided screenshots of Home, Spotify, live Bournemouth Weather, and sample Glucose, reported that it looks like it works, and confirmed the device view was PC-paired. This validates screen rendering/navigation and real weather fetching, **not** actual Spotify transport/volume controls, glucose range interactions, Omarchy, physical ESP32 or live Libre 2 Plus readings. Real ESP32 firmware does not exist.

**Windows Python validation (user log, 2026-10-25):** `unittest discover -s tests -v` ran 44 tests: **42 passed, 2 errors** in `test_linux_companion` because its Linux-only code ran under Windows; the four dashboard static tests and new LAN static-allowlist test passed. Node JS syntax check passed. Nonfatal `ResourceWarning` for Flask static-response file handles was observed. Do not report a clean 44/44 suite.

## Live glucose feed now available as opt-in integration (2026-10-25)

**Implementation completed, live account validation pending.** The Glucose screen can now consume a frequently updated **Gluroo Global Connect / Nightscout-compatible HTTPS source** through the local PC server, with reading timestamps, trend arrows, 3/6/12h history, caching and stale-data labels. This is not an Abbott API and not a standalone ESP32 connection; it requires setting up a LibreLinkUp follower account, connecting it through Gluroo and supplying private GGC credentials in the PC environment. No personal readings have been tested. **See [GLUCOSE-LIVE.md](GLUCOSE-LIVE.md)** for setup, security and third-party privacy implications. The historical CSV importer remains an optional fallback when no live source is configured. The health endpoint is restricted to localhost and excluded from plain-HTTP device LAN routes.

## Screens
## Glucose UI polish — 2026-10-25 (preview awaiting visual review)

User confirmed an authenticated local Gluroo feed delivering recent readings and graph on Windows 11; all six focused Python backend tests passed. The Glucose v0.4 screen now makes **the reading and trend arrow the primary focus**, keeps a compact latest-reading age/time, trims duplicated labels and clutter, and retains a visible LIVE/STALE/OFFLINE pill and one low-profile **NOT FOR TREATMENT** reminder. A simplified graph retains 3/6/12h navigation and gap handling. No CGM data or credentials are committed. This appearance change has **not yet been visually approved**. Other dashboard screens and proven Spotify playback behavior are intended to remain unchanged.


- **Home (default):** local clock/date, music shortcut reflecting the existing player, current weather summary once loaded, and glucose connection status.
- **Spotify:** the unmodified Phase 5.2 paired hardware player, playback/volume actions, artwork retry, album glow, and PC/Wi-Fi mode.
- **Weather:** city search, temperature, condition, feels-like temperature, humidity, wind, rain and five hourly forecast tiles, with a 15-minute in-memory update interval. Open-Meteo geocoding and forecast are fetched directly by the simulator browser over HTTPS. No API key for non-commercial prototype use. **Initial city is example London**; a selected city is remembered locally in the browser. No precise geolocation requested. On errors the app reports the problem and retains the last successful forecast in memory.
- **Glucose:** disconnected status and an explicitly identified **synthetic sample graph** with 3h/6h/12h options. The current-reading field deliberately shows --.- mmol/L. **No sensor connection, real Abbott/Libre credentials, live glucose value, LibreLinkUp scraping or real glucose data is stored or transmitted.**

Navigate by touchscreen tabs or horizontal swipes over non-control areas. Existing physical media controls keep their current purpose. The old four-key simulator is deliberately unchanged until separately adapted to the agreed three-key plus push-knob physical layout.

## Files

- static/desk-dashboard.js: isolated navigation, clock, weather requests and synthetic chart.
- static/desk-dashboard.css: 800×480 UI styles, local to /device with responsive simulator sizing.
- templates/device.html: imports both new assets after original Phase 5.2 assets.
- device_bridge.py: allows two new read-only static resources through the existing restricted LAN device surface, **without new API routes**.
- tests/test_dashboard_preview.py: source, security-label and optional Node syntax assertions.
- tests/test_device_bridge.py: new LAN asset allowlist regression.

## Libre 2 Plus safety and integration gate

Displaying real Libre 2 Plus data would require a **supported and permitted** export/sharing route, secure credentials, transport/privacy protection, timestamps, stale-data handling, unit validation and recovery for missing/out-of-order readings. No authorised personal data API has been selected or proven for this project. Do not implement unofficial Abbott cloud authentication or publish credentials, readings or real graph history in GitHub.

The prototype --lan pairing bridge uses **HTTP bearer tokens without TLS**. **Do not transmit real medical readings over the existing LAN bridge.** Use an appropriate private architecture and threat review first. A Windows/Omarchy companion or Raspberry Pi is a possible later integration host, not implemented.

The Desk Thing is a **secondary information display only**, not a medical device. It must never replace the official Libre app, its alerts or insulin decision-making. Label simulated, live, delayed and missing data unmistakably.

## Windows 11 PowerShell validation

Run these commands from an existing checkout in your Projects directory:

    cd "$HOME\Projects\Spotify-Desk"
    git pull --ff-only origin main
    .\.venv\Scripts\python.exe -m unittest discover -s tests -v
    node --check .\static\desk-dashboard.js
    .\.venv\Scripts\python.exe desk_ui.py

Open http://127.0.0.1:8888/device and pair using http://127.0.0.1:8888/pair if necessary.

1. Home opens first; clock updates; London weather tile populates when online.
2. Weather supports another city, shows five hourly tiles, and displays an error if a city is invalid or the weather service cannot be reached.
3. Glucose remains clearly SAMPLE DATA and Not connected; 3/6/12-hour preview graphs change without real readings.
4. Spotify remains functional: previous/play/next, PC/Wi-Fi, volume routing, artwork, pairing/reconnect.
5. All tabs and swipe interactions remain within the 800×480 screen.
6. The restricted --lan simulator loads new assets but desktop/OAuth endpoints stay blocked.
7. Repeat appropriate checks in Omarchy and distinguish implementation from actual user acceptance.


## Historical LibreView CSV import — implementation added 2026-10-25

**Status:** Implemented in browser code on `main`; **not yet tested by the user** with an actual LibreView export or visually accepted. This does not change the existing Windows-validated Home/Weather/Spotify pages. No real-time Libre 2 Plus integration is present.

The new **Import CSV** control appears only when viewing `http://127.0.0.1:8888/device` on the **same PC** (localhost or 127.0.0.1). It is deliberately absent if browsing the simulator from a LAN address. The downloaded data is parsed by browser JavaScript entirely in memory; it is **not uploaded to Flask**, not sent to Abbott or Open-Meteo, and not persisted to disk or localStorage by our app. The user-selected CSV remains wherever they saved it (for example Windows Downloads) until they delete it. Closing/reloading the tab or pressing **Clear** discards parsed data from the page.

**Obtaining a supported manual export:**
1. Open https://www.libreview.com/ in a separate browser tab and sign in using the existing LibreView account credentials **there**. Never enter credentials into Desk Thing.
2. Open **Glucose History** and choose **Download Glucose Data**, complete the website's verification and download CSV. Menu wording may vary by version.
3. On the local PC `/device` page, open **Glucose**, set CSV timestamp date order **UK D/M/Y** or **US M/D/Y** to match the exported file, and choose **Import CSV**.
4. The preview shows **last exported historical value**, its **actual timestamp**, and selectable 3h/6h/12h history anchored to the latest available file record. Gaps longer than 20 minutes render as disconnected segments, not interpolated lines. Current sensor status remains **not connected**; neither an automated refresh nor an alarm is provided.
5. **Clear** returns to synthetic sample data. Refresh the page if you want to reset everything.

The importer understands CSV/TSV with LibreView `Device Timestamp`, `Record Type` and `Historic Glucose mmol/L` or `Historic Glucose mg/dL` columns. It uses only **Record Type 0 (historic glucose)**, converts mg/dL into mmol/L where needed, sorts/deduplicates timestamps and skips invalid values. Files are limited to 12 MB through the UI. The export can contain identifying and other medical fields such as name, device serial, food and insulin events; the parser ignores those fields. **Never upload a real CSV to the public repository, GitHub issues or a chat.**

**Limitations:** LibreView historical export is not the same as the sensor's minute-by-minute live display, historical data may be sampled at ~15-minute intervals, and device timestamps have no explicit timezone. Day/month order is user-selected; daylight-saving-time ambiguity can affect local chart placement. This is a graph preview, **not intended for treatment decisions**. The phone app and its alerts remain authoritative.

**Research:**
- Abbott Libre 2 Plus compatibility: https://pro.freestyle.abbott/uk-en/help-support/faq/question-answer.html?q=FreeStyle+Libre+2+Systemquestion-14
- Official cloud sharing: https://www.freestyle.abbott/uk-en/managing-your-diabetes/start-your-journey/librelinkup.html
- Manual LibreView CSV export instructions from Glooko: https://support.glooko.com/hc/en-gb/articles/4531230605843-How-to-import-your-blood-glucose-data-from-an-Abbott-FreeStyle-Libre-1-Libre-2-or-Libre-3
- Abbott's LibreView user terms restrict automated access: https://files.libreview.io/files/documents/en-US/pat-TOU_2026-07-06.html

**New files:** `static/glucose-history.js` (isolated pure parser), `tests/check_glucose_history.cjs` (synthetic/offline fixture checks). The existing dashboard JS adds import controls, safe labels and discontinuity-aware historical chart rendering; template and restricted LAN allowlist include the parser JavaScript **but no health API route**. The history CSV never goes through the server.

**Developer checks (PowerShell):**

    node --check .\static\glucose-history.js
    node --check .\static\desk-dashboard.js
    node .\tests\check_glucose_history.cjs
    .\.venv\Scripts\python.exe -m unittest discover -s tests -p test_dashboard_preview.py -v
    .\.venv\Scripts\python.exe -m unittest discover -s tests -p test_device_bridge.py -v

The broader Windows suite previously reported 42 passes and 2 Linux-only failures; this feature does not claim to fix those unrelated platform tests.


## Next steps

1. User runtime validation and UI polish.
2. Weather location selection and richer forecasts after first-pass testing.
3. User-test local LibreView CSV import with a real file privately (without sharing it), verify the date order, graph gaps and historical labels; then research permitted live-data routes and an appropriately secured bridge.
4. Port designs into ESP-IDF/LVGL only after Waveshare hardware and firmware proof-of-concept. Browser CSS/JS cannot run directly on ESP32.

# Multi-dashboard browser preview — Home, Weather and Glucose

**Status (2026-10-25):** Implemented and **visually/user validated on Windows 11** in the `/device` browser simulator. The user provided screenshots of Home, Spotify, live Bournemouth Weather, and sample Glucose, reported that it looks like it works, and confirmed the device view was PC-paired. This validates screen rendering/navigation and real weather fetching, **not** actual Spotify transport/volume controls, glucose range interactions, Omarchy, physical ESP32 or live Libre 2 Plus readings. Real ESP32 firmware does not exist.

**Windows Python validation (user log, 2026-10-25):** `unittest discover -s tests -v` ran 44 tests: **42 passed, 2 errors** in `test_linux_companion` because its Linux-only code ran under Windows; the four dashboard static tests and new LAN static-allowlist test passed. Node JS syntax check passed. Nonfatal `ResourceWarning` for Flask static-response file handles was observed. Do not report a clean 44/44 suite.

## Screens

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

## Next steps

1. User runtime validation and UI polish.
2. Weather location selection and richer forecasts after first-pass testing.
3. Research permitted Libre data routes; design a separate secure, mockable bridge before any real connection.
4. Port designs into ESP-IDF/LVGL only after Waveshare hardware and firmware proof-of-concept. Browser CSS/JS cannot run directly on ESP32.

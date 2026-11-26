# Software and Raspberry Pi deployment design

Last updated 2026-11-26. Design proposal, not implemented on a Pi or Echo Show.

## Requirements

- 5.5-inch touchscreen, responsive 960 x 480, full-screen kiosk, no custom physical buttons required.
- Home: clock/date, Spotify now playing, weather icon/temperature, glucose value/trend only when fresh.
- Spotify Wi-Fi mode: Spotify Web API + Spotify Connect; control active Xbox/PC/phone device over internet, including play/pause, previous/next, artwork, device selection when available, and volume only if supported. Premium required for Web API playback control; verify current developer app restrictions, OAuth/PKCE and scope. Audio plays on the selected device, not necessarily the Echo Show.
- Echo mode (user requested 2026-11-26, experimental): local speaker playback via official Spotify Android app as Connect target if viable; Web API alone cannot stream audio. Preserve power/privacy button and use a compact Wi-Fi/PC/Echo touchscreen dropdown (current mode + chevron), distinct from playback-device selection; physical volume forwarding needs Android-side integration with target-aware routing. See UI-DESIGN.md for research and fallback. New seek/shuffle/repeat/save actions need scope and endpoint validation.
- PC mode: optional separate Windows/Omarchy companion for OS-level media controls, system volume and audio visualiser. Do not treat Pi's headless local Linux media session as the desktop. If PC offline, show PC mode unavailable and retain Wi-Fi mode.
- Weather: fixed Bournemouth, Open-Meteo and existing 15-minute refresh. User accepted large current weather above forecast cards, temperature/condition/feels-like/rain probability/humidity/sunrise/sunset, configurable forecast duration and icon styles, static condition-themed images, tap-day details; no city input. Proposed three-day default, swipeable longer forecast and Pi-side cache/static assets; verify fields and supported durations before implementation. Label forecast probability interval and stale data.
- Glucose: supplementary near-real-time data, mmol/L, source trend arrow, reading timestamp/age, LIVE/GRAPH/BOTH, selected history windows, configurable display band and existing AUTO/FULL chart behavior. No permanent local medical history; no invented readings. Preserve existing display preferences in docs/DASHBOARDS.md without adding personal health information here.
- Future widgets optional. No Home Assistant dependency desired.

## Selected UI direction (2026-11-26)

The user provided a rough clock-first home mock-up with a right-side vertical icon rail, and confirmed the Pi backend direction. Keep the frontend lightweight and expandable, with Home / Spotify / Weather / Glucose and a proposed More entry. Detailed proposals and outstanding decisions are in [UI-DESIGN.md](UI-DESIGN.md); no redesigned UI has been implemented.

## Proposed architecture

```text
Spotify Connect / Spotify API        Open-Meteo
             |                          |
             +---- Raspberry Pi 4 ------+
                         |
CGM -> official phone app -> sharing cloud -> Gluroo GGC HTTPS -> Pi reader
                         |
             isolated dashboard service
                         |
         authenticated HTTPS on private LAN
                         |
            Echo Show 5 Android kiosk

Optional Windows/Omarchy PC companion <-> authenticated service
```

The Pi is selected by the user because it can remain on when Windows is off and has 8 GB RAM; the user clarified on 2026-11-26 that it is powered off and Nextcloud is no longer used. It can potentially be dedicated to this project; inspect existing OS/storage and preserve old data unless user approves wiping. No paid hosting or new hardware planned (existing internet/services and power still required). Direct native Android app is a possible later alternative but not validated on 1 GB RAM. No Home Assistant required unless a selected kiosk app cannot function without it.

## Hosting alternatives (2026-11-26)

- Pi (recommended first): existing Python code, separate always-on Linux host, protected Gluroo secret, less CPU/memory burden on Echo Show. Requires Pi power/network and secure local TLS/device authorization. No extra purchase assumed if working storage/power available.
- Native Android app: potential fully standalone Wi-Fi Spotify/weather/CGM via HTTPS and PKCE, with Android Keystore-backed storage. Needs a port of backend and interface, compatible app auth, stale-state/restart tests and evaluation of security on unlocked old Android. No external server required in principle; untested.
- Termux: Android >=7 is supported by upstream; potential to run modified Python headless backend on device loopback and a kiosk frontend, avoiding a LAN data hop. Not tested on checkers. Memory, package architecture, lifecycle/autostart, browser/origin authorization and credential protection must be evaluated. Do not expose service beyond loopback.
- Free external hosting: technically possible but quotas/sleep, data privacy, credentials and public exposure add complexity. Not preferred for personal CGM data.
- Desktop host: useful for development only; must be on to serve dashboard.

Keep API/data model portable so a native/Termux experiment later does not require discarding Pi work. No change to requirement for official sensor-phone connection, internet and upstream cloud. Sources: https://github.com/termux/termux-app ; https://developer.spotify.com/documentation/web-api/concepts/authorization ; https://gluroo.com/support/gluroo-global-connect-ggc-nightscout-compatible-api/ .

## Existing code and known limitations

- [desk_ui.py](../desk_ui.py): Flask, Spotify PKCE, loopback callback 127.0.0.1:8888, local OS adapters.
- [device_bridge.py](../device_bridge.py): paired bearer tokens, private LAN route allowlist, SSE; current LAN mode is HTTP and not suitable for medical data.
- [glucose_live.py](../glucose_live.py): HTTPS Nightscout-compatible reader, cache, source validation, rate limit handling, mmol conversion and stale status.
- [Dashboard design](../docs/DASHBOARDS.md), [CGM integration](../docs/GLUCOSE-LIVE.md), [architecture](../docs/ARCHITECTURE.md), [install](../docs/INSTALL.md).
- The detailed CGM docs record six targeted Windows tests and a prior user-observed live-feed result. Some README/older notes still say not validated; distinguish prior observed desktop test from new Pi/device validation. Current code has no secure external glucose endpoint.
- Existing PC mode is host-local. Splitting the desktop companion from the headless Pi service needs implementation, not just deployment.

## Free glucose integration and security requirements

Use the existing documented Gluroo Global Connect (GGC) Nightscout-compatible API rather than automating Abbott logins. Existing upstream sharing/account configuration should be verified locally; no private account status or data needs to be published. GGC is documented as free; service terms/limits can change. The distinct Write to Nightscout feature was announced discontinued 2026-11-03, not GGC. Check current docs before deployment.

Existing reader polls at most every 150 seconds, caches across callers, and labels data stale at 600 seconds or when the upstream request fails. GGC downstream sync can add minutes; never claim true 60-second end-to-end updates. Previous research found a 5,000/day GGC account request cap (verify before deployment); 150 seconds corresponds to up to 576 polls/day, excluding other clients. Preserve backoff and avoid multiple pollers.

Read only required glucose entries over TLS, use timestamps and known trend codes, do not write treatments or other records. Phone must remain connected to its sensor and upload to the upstream service. Gluroo is a third-party processor; review terms/privacy. Keep official monitoring and alerts authoritative; supplementary display must never be used to make insulin or treatment decisions.

- Credentials: GGC endpoint and API secret hash are private; the hash is equivalent to a read/write credential. Store only on Pi with restricted permissions (systemd credentials or equivalent), no JS, URL parameters, repository, chat or logs. Spotify tokens also remain protected.
- Network: bind application to loopback; use a dedicated reverse proxy with an explicit allowlist and server-side scoped device authentication. Do not simply expose the existing Flask app or forward every path, since loopback trust could otherwise accidentally expose privileged routes via proxy. Reject spoofed forwarding headers; separate admin/OAuth routes from kiosk endpoints.
- HTTPS: use a trusted certificate with hostname validation on Echo Show; test older Android WebView trust and certificate renewal. No bypass of TLS checks, mixed HTTP or public forwarding. Restrict inbound access to trusted LAN/device; isolate the old Android device from unrelated devices if feasible.
- Device authorization: unique revocable limited-scope credential, secure storage, short pairing window, explicit origin and host checks; consider secure HttpOnly same-site session cookie and CSRF defenses for actions. Never place GGC secret in the browser.
- No health values or secrets in access logs, debug logs, screenshots, backups, analytics, URLs, persistent browser cache/localStorage or service worker caches. Use no-store and in-memory rolling data. When stale/offline, visibly mark time/age and suppress Home value or mark unavailable; do not replace with synthetic data.
- Treat ROM/Android 11 patch limitations as a reason for isolation, not as a guarantee of security.

Sources: https://gluroo.com/support/gluroo-global-connect-ggc-nightscout-compatible-api/ ; https://gluroo.com/support/libre-cgm-troubleshooting/ ; https://developer.spotify.com/documentation/web-api ; https://kiosksatellite.com/docs/custom-pages/ ; existing docs above.

## Pi preflight — run on Raspberry Pi, Linux

Read-only commands; do not install until output reviewed. Redact local IPs, names, tokens and other identifiers before sharing publicly.

```bash
cat /etc/os-release
uname -m
free -h
df -h /
sudo ss -tlnp
command -v docker || true
command -v podman || true
```

Choose a separate unprivileged systemd service/venv or isolated container after checking current Nextcloud stack. Reserve separate ports, avoid touching Nextcloud's web proxy until planned, make startup/recovery automatic, test resource use and backup/rollback. Use a production WSGI setup (not Flask debug server) and design concurrency/caching explicitly; avoid duplicated upstream polling by multiple workers.

## UI performance

Developer-reported free RAM around 400 MB on kiosk image is encouraging, not measured here. Keep rendering lightweight: resize artwork, limit animation/blur, bounded chart points, minimal JS, avoid simultaneous background streams, test page switches and long uptime. Preserve current album colour styling if smooth; PC audio visualisation optional and not needed for Wi-Fi mode.

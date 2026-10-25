# Live glucose integration — Libre 2 Plus → LibreLinkUp → Gluroo → Desk Thing

**Stage (2026-10-25):** Backend + browser live-feed integration implemented on `main`, tested only with synthetic/mock data so far. **No actual Libre 2 Plus credentials or readings have been connected or verified.** The existing validated browser Home/Weather/Spotify pages are retained; this is **not physical ESP32 firmware**.

## Why this is the intended live path

The original Libre 2 Plus sensor connects to the wearer's official LibreLink app (iPhone) and uploads readings through Abbott's internet service. Abbott's LibreLinkUp app is an authorised way to share readings with a follower account. Commercial secondary displays (GlucyView, Glucose Display, Glowcose) advertise compatibility by consuming LibreLinkUp-sharing data, generally via their own implementation or service. No confirmed public personal-developer Abbott API was identified. Abbott's LibreLinkUp licence restricts automated access to its cloud; **do not implement/ship an independent automated Abbott login in this project**.

Gluroo is a separate service that supports Libre 2/2+/3 data from LibreLinkUp and publishes its own **experimental Nightscout-compatible Gluroo Global Connect API** (GGC). This project reads that *documented Gluroo API* rather than automating Abbott itself. Users choosing this route disclose their CGM readings and follower account credentials to Gluroo, and must review Gluroo and Abbott terms/privacy and accept the risk of third-party service outages/breakage. Gluroo's API has no read-only token: **its SHA-1 access hash is an all-powerful credential** even if it resembles only a digest. Protect it exactly like a password.

Compatible standard Nightscout installations that expose `GET /api/v1/entries/sgv.json` with a SHA-1 `api-secret` header can use the same backend. A standard Nightscout readable role token may require a different request auth mechanism, not implemented/tested here.

**Architecture:**

```text
Libre 2 Plus
    ↓ Bluetooth
iPhone official LibreLink app
    ↓ Abbott cloud (online)
LibreLinkUp follower account
    ↓ Gluroo import (third-party service)
Gluroo Global Connect HTTPS Nightscout-compatible API
    ↓ HTTPS with private api-secret SHA-1 header
Python glucose_live.py on Windows / Omarchy companion
    ↓ authenticated, loopback-only /api/device/glucose
Browser simulator /device on the SAME PC
    → live-received mmol/L reading, trend, up to 12h history
```

The phone still needs to be connected to the internet and uploading sensor readings. Neither this dashboard nor Gluroo replaces the official app or its alarms. This is **near-real-time at best**: sensor updates may be minute-level on the phone, but Gluroo's downstream CGM sync can be 2–5 minutes, and our server polls every **150 seconds**. Do not claim 60-second end-to-end latency.

## 1. Set up the sharing chain — on your iPhone

1. Check **LibreLink** is already showing current automatic readings from Libre 2 Plus (a Libre 2 reader used to start the sensor may not provide automatic live phone readings).
2. In LibreLink: **Connected Apps → LibreLinkUp → Manage / Connect → Add Connection**. Invite a **separate email address** to act as your follower.
3. Open **LibreLinkUp** (Apple App Store), sign up/log in with the *invited follower account*, accept the invitation, and verify you can see current readings. Do not use the LibreLink wearer account credentials as the follower credentials.
4. Install the **Gluroo** iPhone app. In Gluroo: **Menu → Settings → CGM**, select FreeStyle Libre, supply the **follower LibreLinkUp** sign-in to Gluroo, and connect. Wait until Gluroo itself shows current glucose readings. This step shares your health data and follower credentials with the Gluroo service.
5. In **Gluroo → Connections → DIY / Nightscout (Loop)**, generate the **Nightscout URL** and **API Secret Header (SHA-1)** value. These are the ONLY two values Desk Thing requires. **Keep them private.** Do not share them in a chat, screenshots, issues or GitHub. The SHA-1 header grants both read and write rights to the Gluroo GGC account.

Sources:
- https://gluroo.com/support/libre-cgm-troubleshooting/
- https://gluroo.com/support/gluroo-global-connect-ggc-nightscout-compatible-api/
- https://www.freestyle.abbott/en-us/support/faq/apps/how-the-librelinkup-app-shares-glucose-data.html
- https://files.libreview.io/files/documents/en-US/LLU_EULA_2026-07-30.html

## 2. Set up the Windows companion — PowerShell only

In PowerShell, **stop the currently running server** with Ctrl+C and then:

```powershell
cd "$HOME\Projects\Spotify-Desk"
git pull --ff-only origin main
.\.venv\Scripts\python.exe -m pip install -r requirements-ui.txt -r requirements-windows.txt

$env:DESK_GLUCOSE_URL = Read-Host "Gluroo Nightscout base URL (https://...ns.gluroo.com)"
$secureHash = Read-Host "Gluroo API Secret Header SHA-1 (40 characters)" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureHash)
try {
  $env:DESK_GLUCOSE_API_SECRET_SHA1 = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
  Remove-Variable secureHash,pointer -ErrorAction SilentlyContinue
}

# Run just the new offline glucose tests, no actual service connection needed.
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_glucose_live.py -v
node --check .\static\desk-dashboard.js

# This launches the server with those environment settings in the current session.
.\.venv\Scripts\python.exe desk_ui.py
```

The hash and URL are **not** written to files by Desk Thing. They live in the current PowerShell/process environment and are lost after that session ends. For a later persistent setup, use Windows Credential Manager/DPAPI, not Git or a plain-text .env file. Never paste credentials into the browser or URL query string. The Spotify login error on the old `/` page is unrelated to the CGM data bridge and need not be fixed to test the paired PC `/device` page.

## 3. Test the local display

1. On the **same Windows computer**, visit `http://127.0.0.1:8888/device` and pair through `/pair` if needed.
2. Select **Glucose**. With correctly configured Gluroo and current readings, the dashboard will automatically update, showing the mmol/L number, a trend arrow when available, latest reading timestamp and up to 12 hours of records.
3. The Home tile mirrors the last received value only while the source status is **LIVE FEED**. If readings are older than ten minutes, or the HTTPS source errors, it shows **Not live**.
4. Reload the tab once after pulling the new files; versioned `?v=0.3` JS/CSS URLs prevent stale cached code. Check whether the time shown on the dashboard is close to LibreLinkUp/Gluroo and whether it updates over several source refreshes.
5. If status shows **STALE / OFFLINE**, validate the upstream chain in order: official LibreLink → LibreLinkUp → Gluroo, check Gluroo’s Nightscout URL and SHA-1 header, and ensure internet access. A rate-limit response stops automatic upstream polling until the next UTC day.

**Do not send screenshots containing glucose values, access hashes, personal identifiers or CGM history to GitHub or public issue trackers.** If asking for technical assistance, give only the status label and redacted error information.

## Security and medical limitations

- The Flask device bridge is plain HTTP and its existing `--lan` protocol is not suitable for personal health information. The new `/api/device/glucose` route explicitly requires a **loopback client IP, a valid paired-device bearer token, and same-origin requests**. It is **not on the device LAN allowlist**. The actual physical ESP32 CANNOT use this yet; device-to-companion transport needs a secure, reviewed design first.
- Glucose HTTPS fetch uses a fixed validated HTTPS base URL and a secret sent in an `api-secret` **header**, never in query parameters. No HTTP redirects; no insecure TLS mode; no backend logging of glucose records. Upstream requests are cached per server process for at least 150 seconds.
- The service reads only recent CGM `sgv` items, converts mg/dL → mmol/L, checks values and timestamps, does not read treatments/insulin/food or write to the source, and stores received records only in PC memory.
- **LIVE FEED** is labelled only when the upstream request succeeds and the most recent received entry is under 10 minutes old. Stale/errors display **STALE / OFFLINE**, without showing the synthetic demo graph as if it were real.
- An experimental Gluroo API may be delayed, discontinued or restricted, and there can be third-party, phone and network outages. The official CGM app, receiver and medical alarms remain essential, and any treatment decisions must be based on the approved system, not this desk display.
- The existing manual CSV importer remains only as an optional unconnected fallback and is hidden while an active live source is configured.

## Validation boundary

- **Code implemented** on `main`: `glucose_live.py`, authenticated local Flask route, updated dashboard JS/CSS and versioned assets, unit tests `tests/test_glucose_live.py`.
- **Assistant static review** performed for source and tests; full user Windows tests/actual API integration and browser results **still pending**.
- The former Python full-suite Windows run reported 42 passes and two Linux-only test errors, unrelated to the new glucose bridge. Run the focused glucose tests above first.

## Next engineering tasks

1. Validate real Gluroo GGC readings and freshness (do not infer success just from an authenticated response).
2. Confirm chart 3/6/12-hour navigation, 800×480 layout and correct trend arrows; support recoveries after connection loss.
3. Evaluate alternative approved, appropriately scoped sources and secure BLE/phone sharing if available.
4. Design mutually authenticated, encrypted ESP32 local transport before any physical real-data dashboard.

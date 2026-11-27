# Pre-arrival preparation

2026-11-26: User has ordered the Echo Show 5. Device delivery pending. These tasks can proceed without the device; no Pi deployment or new application code has been implemented yet.

## 1. Omarchy workstation

**Completed 2026-11-26:** user verified ADB 1.0.41 / 37.0.0p1, Fastboot 37.0.0p1, usbutils 019 on Arch x86_64 (kernel 7.2.2-arch1-1); android-tools 37.0.0.p1-1 was already current. No device attached, so this proves tool availability only. Reference commands:

```bash
command -v adb
command -v fastboot
adb version
fastboot --version
```

If missing, use `sudo pacman -S --needed android-tools` (on a current Arch system; avoid partial upgrades). Re-run the checks. Do not run unlock scripts or flash commands before the actual unit's model and LK are verified. Cable detection is pending physical delivery. Download ROM and amonet only from linked upstream releases after checking current instructions; do not assume a specific older release remains appropriate. See INSTALLATION-AND-USB.md.

## 2. Raspberry Pi read-only preflight (next action)

The user clarified the Pi is powered off on a shelf, no longer used for Nextcloud. Power it on and inspect the existing OS before deciding whether to reuse it or install a fresh Raspberry Pi OS Lite on separate storage. Do not erase existing data without explicit approval. SSH into existing Raspberry Pi using its known hostname/user; do not guess credentials. Run on the Pi, not Omarchy workstation:

```bash
echo '=== OS ==='
cat /etc/os-release
uname -m
echo '=== MEMORY ==='
free -h
echo '=== STORAGE ==='
df -h /
echo '=== LOAD ==='
uptime
echo '=== PYTHON ==='
python3 --version
echo '=== PORTS ==='
sudo ss -tlnp
echo '=== CONTAINERS ==='
if command -v docker >/dev/null; then
  sudo docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
fi
if command -v podman >/dev/null; then
  podman ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}'
fi
echo '=== WEB SERVICES ==='
systemctl is-active nginx apache2 caddy docker 2>/dev/null || true
```

These are read-only diagnostics; no package installs or configuration changes. If a command is unavailable, report that rather than installing software to complete the check. Redact usernames, addresses, identifiers, credentials and any sensitive container names before sharing. Do not dump container environment, Nextcloud config or secret files. Pi OS, architecture, load and actual Nextcloud deployment are not yet known.

## 3. Software while waiting

User confirmed Pi hosting and supplied a rough right-side navigation concept. All seven main design stages accepted; read [UI-DESIGN.md](UI-DESIGN.md) for latest requirements. Begin isolated synthetic-data frontend prototype on echo-show/prototype while Pi preflight remains pending. Preserve existing functionality and use synthetic data for design previews.

Proposed implementation order:
1. Review existing root UI and Python code; preserve desktop baseline. Use an isolated development branch for application changes, keep original CAD intact.
2. In parallel with UI prototyping, create a headless server mode with Wi-Fi Spotify playback independent from local Linux audio/PC mode. Ensure the current OAuth loopback flow can be completed securely via an SSH tunnel or other reviewed local setup, and verify current Spotify app restrictions. No public callback/Flask debug exposure.
3. Reuse Home/Spotify/Weather/Glucose views in a 960 x 480 browser test. Test at 100% scaling with touch emulation, graph legibility, overflow, navigation, reduced animation and clear unavailable states. Actual Echo Show performance is a later gate.
4. Implement a distinct authenticated HTTPS device boundary on the Pi; protect existing admin/OAuth paths and do not expose existing loopback-only glucose route simply by proxying it. Test using synthetic data first. See SOFTWARE-AND-PI.md for security requirements.
5. Once preflight and security tests pass, deploy isolated service, verify Nextcloud unchanged, authorize Spotify locally, test playback on Xbox with PC off, and enable real Gluroo feed only after protected credential setup. Official glucose app remains authoritative; no real data or tokens in logs or Git.
6. Test with another browser on the private LAN via HTTPS before device delivery if possible. Verify autostart and restart recovery. PC-local control is a separate companion feature, not a requirement for initial standalone Wi-Fi mode.

## 4. Delivery gates

Confirm actual unit/model and accessories, inspect hardware offline, check cable data capability and query product/LK read-only. Only then choose the model-specific ROM and unlocking method. Keep the old case/PCB work unchanged and use TESTING-AND-ROADMAP.md to record evidence.

**Current blocker:** Pi preflight results and physical Echo Show delivery. No guarantee of a compatible installed LK or kiosk performance until tested.


### Latest checkpoint — System Information accepted

2026-11-27: User approved System Information appearance and supplied browser screenshot confirming populated Omarchy host CPU, RAM, storage, temperature, uptime, network link and all five service status rows. Record user visual acceptance and live endpoint output; no independent metric accuracy check, exact Python test output, expanded rail or physical Echo hardware verification reported. Do not commit screenshot or personal data. Main dashboard app design phase accepted; next action Raspberry Pi 4 (8 GB) read-only preflight per PRE-ARRIVAL.md. Existing Pi OS/storage and old Nextcloud services unknown; power on and access via known SSH account or local terminal, no installs/erase/service changes until reviewed. Keep current Omarchy preview available; secure authenticated HTTPS boundary required before real Gluroo data is accessible over LAN. Echo delivery/model/LK validation separate. Documentation-only checkpoint.


### Latest checkpoint — Raspberry Pi preflight received

2026-11-27: User provided read-only Raspberry Pi preflight. Debian 13.3 (trixie), aarch64, Python 3.13.5, 1.8 GiB reported RAM (1.1 GiB available; not the previously assumed 8 GB; physical model/memory configuration unverified), 1.8 GiB swap unused, low load 0.09, ~29 GiB root with 19 GiB free, separate ~461 GiB mounted ext4 external disk. SSH/rpcbind/CUPS/containerd and Docker Nextcloud stack still active (app exposed on 8080, cron, Redis and MariaDB); nginx/apache2/caddy inactive; no listener on 8765 shown. Do not store identifying hostname, username, mount labels or raw process dump. Recommend retaining Debian and existing storage, isolating dashboard in separate checkout and venv, testing Python 3.13/ARM64 compatibility and loopback-only preview first. Nextcloud is reportedly unused; recommend reversible stop only after explicit user agreement, no removal/volume changes, no restart policy changes yet. Existing service/drive data preserved. Next ask for board model and stage checkout of echo-show/prototype, install existing requirements-ui.txt into venv and run offline tests; no credentials needed. If git/venv missing install only required packages after checking. No public/LAN real-data exposure; SSH local port forward with a different workstation port is suitable for initial non-OAuth browser test (existing host guard requires canonical 127.0.0.1:8765; use 8765 on both ends for actual browser/OAuth after stopping workstation preview). Production single-worker server, systemd and authenticated HTTPS device boundary not implemented; do not change host bind or proxy raw glucose endpoint. Pi performance and actual device model pending. No code changes in this checkpoint.


### Raspberry Pi board confirmation

2026-11-27: User confirmed physical board Raspberry Pi 4 Model B Rev 1.5, ARM64 Cortex-A72, four cores, reported maximum 1.8 GHz, Git 2.47.3 already installed. Earlier 1.8 GiB visible RAM remains the sizing basis; physical RAM capacity not independently verified. Next stage isolated checkout and Python 3.13 virtual environment on existing Debian. Install requirements-ui.txt; for full historical regression suite also install prototype/requirements-calendar.txt (inactive Apple adapter tests need these optional packages; public Calendar runtime does not). No credentials required for offline tests; Nextcloud and external storage untouched. Production startup and secure device transport still pending. No Pi changes or test execution reported yet.


### Raspberry Pi compatibility tests passed

2026-11-27: User supplied Raspberry Pi Python unittest discover output: 58 tests ran in 0.544s, OK, including historical Apple Calendar (9), Glucose (6), Spotify server (34), public Calendar (5), System Information (4), plus launcher synthetic assertions executed on import. Expected synthetic setup/cache warning messages are not real credential failures; launcher tests use temporary directories. Confirms tested dependencies and offline regressions work on Debian 13.3 ARM64 Python 3.13.5. Real upstream connectivity, actual Pi runtime and performance still pending. Next transfer only existing three required .env keys over SSH to owner-only Pi prototype/.env without overwriting existing credentials; omit inactive Apple keys. Do not transfer refresh token while workstation may still refresh it; stop workstation preview and authorize on Pi through encrypted SSH local port forward using canonical 127.0.0.1:8765 on both ends. Keep Pi server loopback-only; no raw LAN exposure, no new proxy. Existing Nextcloud and external disk untouched pending separate decision. After live verification, production single-worker service/systemd and authenticated HTTPS device boundary remain outstanding. No code changes or actual secret transfer by assistant.


### Raspberry Pi SSH access confirmed

2026-11-27: User confirmed successful SSH login to Pi via dedicated Ed25519 key from Omarchy. Hostname resolution failed; Pi has Ethernet and Wi-Fi addresses on local subnet; use Ethernet address supplied privately by user, not committed. Raspberry Pi Connect remote shell provided existing authorized access despite forgotten account password. Initial authorized_keys entry lacked valid full public-key format; corrected full single-line ssh-ed25519 public key and permissions (home/.ssh owner-only, authorized_keys 600), fingerprint check and successful login. Private key passphrase prompt expected; no password reset, SSH daemon changes or private key transfer required. Next transfer three required configuration keys through SSH with no overwrite, start Pi loopback preview, forward canonical 8765 on workstation to Pi, reauthorize Spotify and verify services. No credential transfer or live Pi run confirmed yet. No actual keys, local IPs, hostnames or user identifiers stored in repository.


### Pi live preview accepted — automatic startup

2026-11-27: User approved Pi-hosted System Information screenshot: Raspberry Pi 4 Model B Rev 1.5, Debian ARM64, four logical CPUs, CPU 2%, RAM 36%, storage 32%, temperature 35 C, dashboard/Weather/Glucose/Calendar ready and Spotify connected idle. Confirms Pi-hosted live endpoint and service readiness at time of screenshot; not independent playback/control, CGM accuracy, stress or reboot validation. Nextcloud still running; no need to stop based on observed load, no changes to existing containers or disks. Prototype [4fe329b](https://github.com/Cousinsuke/Spotify-Desk/commit/4fe329b9e21d750e3bee82e91a3fdd34d3bd42ce) adds optional Waitress >=3.0.2,<4 production mode and unprivileged systemd user unit, using one request worker to preserve existing serialized Spotify state and background source refresh threads, loopback 127.0.0.1:8765 only, same credential loader and refresh cache, no forwarded-header trust, bounded connections/headers/body, no tracebacks to clients. Waitress docs https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html. Service restarts on failure with rate limit, owner-only umask, no new privileges; boot persistence requires linger. Uses current checkout path and existing venv; no secrets in unit, no sudo for user unit install, linger may require authorization. Existing start-live dev mode unchanged. Three additional mocked Python startup tests authored, not executed; previous 58 passed on Pi. Install requirements-production.txt, rerun regression tests, stop manual server before enabling user service, verify active/listener/browser/restart and Linger=yes; reboot test only after user chooses. Rollback disable --now unit and start original launcher. SSH tunnel still required for browser; authenticated HTTPS Echo network boundary remains a separate gate. No actual systemd installation or boot verification by assistant. No screenshots or credentials committed.


### Pi production service verified

2026-11-27: User supplied successful production installation output on Pi: prototype 4fe329b pulled, Waitress 3.0.2 installed, all 61 unittest cases passed in 0.261s plus launcher assertions. systemd user unit installed, enabled and active; loginctl Linger=yes; listener confirmed 127.0.0.1:8765 only; startup log confirms saved Spotify authorization restored. Brief Waitress queue depth warnings 1 and 2 observed after startup, consistent with deliberately serialized single request worker; no failure shown, actual latency not measured. Keep single worker until evidence warrants concurrency redesign. Service configured for boot startup without login; reboot survival not yet tested. Next verify manual restart and optional controlled reboot, reconnect SSH tunnel, verify service readiness and Spotify persistence. User should be aware reboot interrupts existing Nextcloud and remote connections; no container changes. Then design authenticated HTTPS device access (no raw reverse proxy of loopback endpoints, no real glucose on LAN until protections verified). No secrets, raw logs, hostname/IP or identifying process IDs stored. No code changes in this documentation checkpoint.


### Pi reboot recovery verified

2026-11-27: User verified manual restart and full Pi reboot. Post-reboot uptime ~2 minutes, service active/enabled and started automatically at boot, saved Spotify authorization restored, 127.0.0.1:8765 listener present. User reports runs fine. Initial workstation inactive/not-found output was from local Omarchy after SSH disconnected, not a Pi failure. Boot persistence accepted; no code changes. Actual post-reboot individual upstream data accuracy/playback not separately measured. Next design authenticated HTTPS device access with synthetic data first; keep existing loopback and OAuth path isolated. Physical Echo model/LK, Android trust and kiosk capabilities remain unverified. No public exposure, router forwarding, credential or Nextcloud changes; no identifying raw logs committed.


### Secure device access — sample-only gateway

2026-11-27: User agreed secure direct LAN access next. Prototype [744fc33](https://github.com/Cousinsuke/Spotify-Desk/commit/744fc33bebc287f5d1489a5f8b7524074bb498fe) adds independently running sample-only HTTPS gateway (device_gateway.py), never imports or proxies live app, no access to real Spotify/Gluroo or OAuth, explicit static route allowlist, sample root strips query, TLS+exact host+local subnet guard, cross-origin POST rejection. Gunicorn 27.0.1+ TLS (latest PyPI release checked Nov 27; settings reference https://gunicorn.org/reference/settings/), specific RFC1918 IPv4 interface and /24 or narrower, port 8443, one worker/two threads, bounded connections/headers and form size, no access logs; separate user service supplied but not enabled. OpenSSL local CA/IP SAN leaf (365 days), private CA signing key temporary and removed after issuance; owner-only state outside repo, only public CA copied via SSH with fingerprint verification and client trust, never bypass TLS; renewal/IP change requires fresh trust. Device pairing 16 hex digits, single-use ten-minute code, max 8 failed attempts; 30-day HttpOnly Secure SameSite Strict cookie, hashed tokens stored in private SQLite, eight devices maximum, local list/revoke CLI. Exact port, certificate lifetime and pairing limits implementation choices. Seven new offline tests authored, not run; expected 68 total on Pi. First install requirements-device, run suite, init with local Ethernet IP and /24, manually serve sample gateway, verify curl with trusted CA, unpaired/paired browser access, blocked live endpoints and revocation; stop after test. No change to existing loopback production service, Nextcloud, router, credentials or real data. Live API scoped gateway not implemented yet; real data remains on loopback until security verification, then explicit allowlist and tests. Android CA trust and actual Echo device integration pending. Chromium Linux CA guide https://chromium.googlesource.com/chromium/src.git/+/master/docs/linux/cert_management.md . No identifying local network details stored.

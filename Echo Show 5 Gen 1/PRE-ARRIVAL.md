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

#!/usr/bin/env bash
# Installs user units only; activation is a separate, explicit step.
set -euo pipefail
if [[ $# != 1 || ! "$1" =~ ^[a-zA-Z_][a-zA-Z0-9_-]*@[a-zA-Z0-9][a-zA-Z0-9.-]*$ ]]; then
    echo "Usage: bash install-pc-services.sh USER@PI_HOST" >&2
    exit 2
fi
if [[ "$(id -u)" == 0 || "$(uname -s)" != Linux ]]; then
    echo "Run as your normal Linux desktop user (no sudo)." >&2
    exit 2
fi
root="$HOME/Projects/Spotify-Desk-PC-Agent"
source_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
expected_dir="$(cd -- "$root/Echo Show 5 Gen 1/prototype" && pwd -P)"
if [[ "$source_dir" != "$expected_dir" ]]; then
    echo "Run from the dedicated Spotify-Desk-PC-Agent checkout." >&2
    exit 2
fi
for tool in /usr/bin/python3 /usr/bin/ssh /usr/bin/ssh-agent /usr/bin/ssh-add /usr/bin/playerctl /usr/bin/wpctl /usr/bin/busctl; do
    if [[ ! -x "$tool" ]]; then
        echo "Missing executable: $tool" >&2
        exit 2
    fi
done
if [[ ! -r "$HOME/.ssh/spotify-desk-pi" || ! -s "$HOME/.spotify-desk/pc-agent-token" ]]; then
    echo "Existing Pi SSH key and PC token are required." >&2
    exit 2
fi
systemctl --user show-environment >/dev/null
umask 077
config="$HOME/.config/spotify-desk-pc"
unit_dir="$HOME/.config/systemd/user"
mkdir -p -- "$config" "$unit_dir"
chmod 700 -- "$config"
tmp="$(mktemp "$config/tunnel.env.XXXXXX")"
trap 'rm -f -- "$tmp"' EXIT
printf 'DESK_PI_TARGET=%s\n' "$1" > "$tmp"
mv -f -- "$tmp" "$config/tunnel.env"
for unit in spotify-desk-pc-agent.service spotify-desk-pc-key-agent.service spotify-desk-pc-tunnel.service; do
    install -m 644 -- "$source_dir/$unit" "$unit_dir/$unit"
done
systemctl --user daemon-reload
echo "User services installed but not started. Stop manual agent/tunnel before enabling."

"""Read-only diagnostics for Phase 4.1 on Omarchy / Arch Linux."""
import os
import shutil
import subprocess
import sys
from linux_companion import linux


def run(*args):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=4, check=False)
        return (result.stdout if result.returncode == 0 else result.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f'ERROR: {exc}'


print('=== Spotify Desk Thing | Omarchy / Arch Diagnostics ===')
print('Platform:', sys.platform)
print('DISPLAY:', os.environ.get('DISPLAY', '(not set)'))
print('WAYLAND_DISPLAY:', os.environ.get('WAYLAND_DISPLAY', '(not set)'))
print('XDG_RUNTIME_DIR:', os.environ.get('XDG_RUNTIME_DIR', '(not set)'))
print('D-Bus session:', 'present' if os.environ.get('DBUS_SESSION_BUS_ADDRESS') else 'not set (may be auto-discovered)')
print('\n--- Required commands ---')
for name in ('playerctl','wpctl','pactl','parec'):
    print(f'{name}:', shutil.which(name) or 'NOT FOUND')
print('\n--- MPRIS players ---')
print(run('playerctl','-l') or '(none found)')
print('\n--- Active media ---')
for name, value in linux.status(force=True).items():
    if name == 'artwork' and value:
        value = '(artwork present)'
    print(f'{name}: {value}')
print('\n--- PipeWire / audio ---')
print('wpctl status:', run('wpctl','get-volume','@DEFAULT_AUDIO_SINK@'))
print('Default output:', run('pactl','get-default-sink'))
print('PulseAudio compatibility:', run('pactl','info').splitlines()[0:5])
print('\nNo credentials or raw audio saved.')

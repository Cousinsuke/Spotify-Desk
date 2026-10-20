"""Read-only Windows companion diagnostics. No audio recording files or tokens."""
from windows_companion import windows

print('=== Spotify Desk Thing · Windows Diagnostics ===')
print('\n--- Media session ---')
status = windows.status(force=True)
for field in ('ok', 'error', 'source', 'title', 'artist', 'playing', 'volume'):
    if field in status:
        print(f'{field}: {status[field]}')

print('\n--- Windows audio output ---')
try:
    from pycaw.pycaw import AudioUtilities
    dev = AudioUtilities.GetSpeakers()
    print('Windows default:', dev.FriendlyName)
    print('Master volume:', round(dev.EndpointVolume.GetMasterVolumeLevelScalar() * 100), '%')
except Exception as exc:
    print('Volume unavailable:', exc)

print('\n--- WASAPI output devices ---')
try:
    import soundcard as sc
    for dev in sc.all_speakers():
        print('  -', dev.name)
    print('Default loopback input:', sc.default_speaker().name)
except Exception as exc:
    print('Loopback enumeration unavailable:', exc)
print('\nNo Spotify credentials or raw audio recorded.')

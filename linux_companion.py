"""Omarchy / Arch Linux local MPRIS + PipeWire companion.

Requires playerctl, wpctl, pactl, parec and a graphical session D-Bus.
No shell command construction, no network listening and no raw audio persistence.
"""
from __future__ import annotations

from array import array
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse
import logging
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time

LOG = logging.getLogger(__name__)


@dataclass
class Snapshot:
    value: dict
    valid_until: float


class LinuxCompanion:
    def __init__(self) -> None:
        self._guard = threading.RLock()
        self._cached: Snapshot | None = None
        self._art_key = ''
        self._art_bytes = b''
        self._art_type = 'image/jpeg'
        self._rms = 0.0
        self._audio_status = 'Starting PipeWire audio meter'
        self._audio_device = ''
        self._audio_ok = False
        self._capture_started = False

    @staticmethod
    def _run(*args: str, timeout: float = 2.5, check: bool = True) -> str:
        cp = subprocess.run(args, capture_output=True, text=True,
                            timeout=timeout, check=False)
        if check and cp.returncode != 0:
            message = (cp.stderr or cp.stdout or 'Command failed').strip()[:180]
            raise RuntimeError(message)
        return cp.stdout.strip()

    def _select_player(self) -> str | None:
        if not shutil.which('playerctl'):
            raise RuntimeError('playerctl missing: sudo pacman -S --needed playerctl')
        players = list(dict.fromkeys(x.strip() for x in self._run('playerctl', '-l', check=False).splitlines() if x.strip()))
        if not players:
            return None
        # Prefer Spotify if it has a session, matching the Windows companion.
        spotify = next((x for x in players if 'spotify' in x.casefold()), None)
        if spotify:
            return spotify
        for name in players:
            if self._run('playerctl', '-p', name, 'status', check=False).casefold() == 'playing':
                return name
        return players[0]

    def _volume(self) -> int | None:
        if not shutil.which('wpctl'):
            return None
        raw = self._run('wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@', check=False)
        match = re.search(r'Volume:\s*([0-9.]+)', raw)
        if not match:
            return None
        if '[MUTED]' in raw:
            return 0
        return max(0, min(100, round(float(match.group(1)) * 100)))

    def _local_art(self, art_url: str, track_key: str) -> str | None:
        if art_url.startswith('https://'):
            return art_url
        # MPRIS players sometimes supply local cache artwork. Never disclose
        # arbitrary local paths: read ONLY cached image files within HOME/.cache.
        parsed = urlparse(art_url)
        if parsed.scheme != 'file' or parsed.netloc not in ('', 'localhost'):
            return None
        with self._guard:
            if self._art_key == track_key and self._art_bytes:
                return f'/api/pc/artwork?key={abs(hash(track_key))}'
        try:
            path = Path(unquote(parsed.path)).resolve(strict=True)
            cache = (Path.home() / '.cache').resolve(strict=False)
            if not path.is_relative_to(cache) or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
                return None
            data = path.read_bytes()
            if data.startswith(b'\x89PNG\r\n\x1a\n'):
                content_type = 'image/png'
            elif data.startswith(b'\xff\xd8\xff'):
                content_type = 'image/jpeg'
            elif data.startswith(b'RIFF') and data[8:12] == b'WEBP':
                content_type = 'image/webp'
            else:
                return None
            with self._guard:
                self._art_key = track_key
                self._art_bytes = data
                self._art_type = content_type
            return f'/api/pc/artwork?key={abs(hash(track_key))}'
        except (OSError, ValueError):
            return None

    def _media_info(self) -> dict:
        if sys.platform != 'linux':
            raise RuntimeError('Linux companion requires Linux.')
        player = self._select_player()
        if not player:
            return {'ok':True, 'connected':True, 'has_playback':False, 'source':'MPRIS'}
        # The format uses delimiters unlikely to appear in song text; no shell.
        fmt = '{{title}}\x1f{{artist}}\x1f{{album}}\x1f{{mpris:length}}\x1f{{mpris:artUrl}}\x1f{{mpris:trackid}}'
        metadata = self._run('playerctl','-p',player,'metadata','--format',fmt, check=False)
        fields = (metadata.split('\x1f') + [''] * 6)[:6]
        title, artist, album, duration_raw, cover_url, trackid = fields
        status = self._run('playerctl','-p',player,'status', check=False)
        if not status and not title:
            return {'ok':True, 'connected':True, 'has_playback':False, 'source':'MPRIS'}
        pos_raw = self._run('playerctl','-p',player,'position',check=False)
        try:
            pos_ms = max(0, int(float(pos_raw) * 1000))
        except ValueError:
            pos_ms = 0
        try:
            duration_ms = max(0, round(float(duration_raw) / 1000)) # mpris:length = microseconds
        except ValueError:
            duration_ms = 0
        key = f'{player}|{trackid or title}|{artist}'
        artwork = None
        if cover_url:
            artwork = self._local_art(cover_url, key)
        if not cover_url or not cover_url.startswith('file:'):
            with self._guard:
                self._art_key = key
                self._art_bytes = b''
        volume = self._volume()
        return {'ok':True, 'connected':True, 'has_playback':True,
                'source':f'MPRIS · {player}', 'title':title or 'Unknown track',
                'artist':artist or 'Unknown artist', 'album':album or '',
                'track_key':key, 'artwork':artwork,
                'playing':status.casefold() == 'playing',
                'duration_ms':duration_ms, 'progress_ms':pos_ms,
                'device':player, 'device_id':player,
                'volume':volume, 'supports_volume':volume is not None}

    def status(self, force=False) -> dict:
        with self._guard:
            if self._cached and not force and time.monotonic() < self._cached.valid_until:
                return dict(self._cached.value)
            try:
                result = self._media_info()
                self._cached = Snapshot(result, time.monotonic() + .55)
                return dict(result)
            except Exception as exc:
                LOG.warning('Linux MPRIS status error: %s', exc)
                return {'ok':False, 'error':str(exc)[:240]}

    def command(self, action, value=None):
        if action == 'volume':
            if type(value) is not int or not 0 <= value <= 100:
                raise ValueError('Volume must be an integer between 0 and 100.')
            self._run('wpctl','set-volume','@DEFAULT_AUDIO_SINK@',f'{value / 100:.2f}')
            if value > 0:
                self._run('wpctl','set-mute','@DEFAULT_AUDIO_SINK@','0')
            elif value == 0:
                self._run('wpctl','set-mute','@DEFAULT_AUDIO_SINK@','1')
            accepted = True
        elif action in ('toggle','next','previous'):
            player = self._select_player()
            if not player:
                return False
            cmd = {'toggle':'play-pause','next':'next','previous':'previous'}[action]
            self._run('playerctl','-p',player,cmd)
            accepted = True
        else:
            raise ValueError('Unknown Linux media command')
        with self._guard:
            self._cached = None
        return accepted

    def artwork(self):
        with self._guard:
            return self._art_bytes, self._art_type

    def meter_state(self):
        with self._guard:
            return {'ok':True, 'available':self._audio_ok,
                    'level':self._rms if self._audio_ok else 0.0,
                    'device':self._audio_device, 'message':self._audio_status}

    def start_meter(self):
        with self._guard:
            if self._capture_started:
                return
            self._capture_started = True
        threading.Thread(target=self._capture_audio, daemon=True, name='desk-linux-audio').start()

    def _capture_audio(self):
        if not shutil.which('parec') or not shutil.which('pactl'):
            with self._guard:
                self._audio_status = 'Install libpulse (provides pactl and parec).'
            return
        attempts = 0
        while True:
            proc = None
            try:
                # This records only the monitor of the currently selected output,
                # never the microphone. No raw samples are stored or streamed.
                sink = self._run('pactl','get-default-sink')
                if not sink:
                    raise RuntimeError('PipeWire has no default output sink')
                device = sink + '.monitor'
                proc = subprocess.Popen([
                    'parec','--device='+device,'--format=s16le',
                    '--rate=16000','--channels=1','--raw',
                ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)
                if not proc.stdout:
                    raise RuntimeError('parec has no output stream')
                with self._guard:
                    self._audio_device = sink
                    self._audio_status = 'PipeWire monitor active'
                    self._audio_ok = True
                attempts = 0
                last_sink_check = time.monotonic()
                while proc.poll() is None:
                    raw = proc.stdout.read(2048)
                    if not raw:
                        break
                    samples = array('h')
                    samples.frombytes(raw[:len(raw)//2*2])
                    if samples:
                        rms = math.sqrt(sum(s*s for s in samples) / len(samples)) / 32768
                        level = max(0.0, min(1.0, (rms - .004) * 8))
                        with self._guard:
                            self._rms = self._rms * .72 + level * .28
                    if time.monotonic() - last_sink_check >= 5:
                        last_sink_check = time.monotonic()
                        if self._run('pactl','get-default-sink',check=False) != sink:
                            break
                raise RuntimeError('Audio output changed or monitor disconnected')
            except Exception as exc:
                attempts += 1
                with self._guard:
                    self._audio_ok = False
                    self._rms = 0.0
                    self._audio_status = f'Audio monitor unavailable: {str(exc)[:130]}'
                LOG.debug('Linux audio monitor retry %d: %s', attempts, exc)
                time.sleep(min(10, max(2, attempts * 2)))
            finally:
                if proc:
                    try:
                        proc.terminate()
                        proc.wait(timeout=1)
                    except Exception:
                        try:
                            proc.kill()
                        except Exception:
                            pass


linux = LinuxCompanion()

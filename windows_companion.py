"""Windows 11 local media adapter for Spotify Desk Thing.

Only accessed from the existing Flask loopback server. No elevated privileges.
Requires PyWinRT media control + pycaw; soundcard is optional for real audio levels.
"""
from __future__ import annotations

import asyncio
import io
import logging
import math
import os
import sys
import threading
import time
from dataclasses import dataclass

LOG = logging.getLogger(__name__)

@dataclass
class Snapshot:
    value: dict
    valid_until: float

class WindowsCompanion:
    def __init__(self) -> None:
        self._guard = threading.RLock()
        self._cached: Snapshot | None = None
        self._art_key = ""
        self._art_bytes: bytes = b""
        self._art_type: str = "image/jpeg"
        self._art_attempts = 0
        self._art_retry_at = 0.0
        self._rms = 0.0
        self._audio_status = "Starting audio meter"
        self._audio_device = ""
        self._audio_ok = False
        self._capture_started = False

    @staticmethod
    def _imports():
        if sys.platform != 'win32':
            raise RuntimeError('Windows companion only runs on Windows 11.')
        try:
            from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
        except ImportError as exc:
            raise RuntimeError('Missing Windows media package. Install requirements-windows.txt.') from exc
        return GlobalSystemMediaTransportControlsSessionManager

    @staticmethod
    def _seconds(value) -> float:
        try:
            return max(0., float(value.total_seconds()))
        except (AttributeError, ValueError, TypeError):
            try:
                # A WinRT TimeSpan is 100-nanosecond ticks when exposed as an int.
                return max(0., float(value.duration) / 10_000_000)
            except (AttributeError, ValueError, TypeError):
                return 0.

    @staticmethod
    def _status_is_playing(info) -> bool:
        status = info.playback_status if info is not None else None
        return str(getattr(status, 'name', status)).casefold() == 'playing'

    async def _select_session(self, manager):
        sessions = list(manager.get_sessions())
        # Spotify session wins if Spotify exposes SMTC; otherwise use Windows' preferred session.
        for s in sessions:
            if 'spotify' in str(s.source_app_user_model_id).casefold():
                return s
        return manager.get_current_session()

    async def _read_thumb(self, props) -> tuple[bytes,str]:
        thumb = getattr(props, 'thumbnail', None)
        if not thumb:
            return b'', 'image/jpeg'
        # Thumbnail access is optional. Failure must not disable transport controls.
        try:
            from winrt.windows.storage.streams import Buffer, InputStreamOptions
            stream = await thumb.open_read_async()
            try:
                cap = min(int(stream.size), 1024 * 1024)
                if cap < 1:
                    return b'', 'image/jpeg'
                buffer = Buffer(cap)
                result = await stream.read_async(buffer, cap, InputStreamOptions.READ_AHEAD)
                raw = bytes(result)
                if raw.startswith(b'\x89PNG'):
                    kind = 'image/png'
                elif raw.startswith(b'RIFF') and raw[8:12] == b'WEBP':
                    kind = 'image/webp'
                elif raw.startswith(b'\xff\xd8'):
                    kind = 'image/jpeg'
                else:
                    return b'', 'image/jpeg'
                return raw, kind
            finally:
                close = getattr(stream, 'close', None)
                if close:
                    close()
        except Exception as exc:
            LOG.debug('Windows media thumbnail unavailable: %s', exc)
            return b'', 'image/jpeg'

    async def _media_info(self) -> dict:
        manager_cls = self._imports()
        manager = await manager_cls.request_async()
        target = await self._select_session(manager)
        if target is None:
            with self._guard:
                self._art_bytes = b''
                self._art_key = ''
            return {'ok':True,'connected':True,'has_playback':False, 'source':'Windows media sessions'}
        props = await target.try_get_media_properties_async()
        play = target.get_playback_info()
        timeline = target.get_timeline_properties()
        source = str(target.source_app_user_model_id or 'Windows media')
        title = str(getattr(props,'title','') or 'Unknown track')
        artist = str(getattr(props,'artist','') or 'Unknown artist')
        album = str(getattr(props,'album_title','') or '')
        track_key = '|'.join((source,title,artist,album))
        # Some Windows media sessions expose the thumbnail shortly AFTER
        # reporting the new track. Retry a few times with backoff rather than
        # permanently caching an empty image for the whole song.
        with self._guard:
            if track_key != self._art_key:
                self._art_key = track_key
                self._art_bytes = b''
                self._art_attempts = 0
                self._art_retry_at = 0.0
            need_art = (not self._art_bytes and self._art_attempts < 4
                        and time.monotonic() >= self._art_retry_at)
            if need_art:
                self._art_attempts += 1
                self._art_retry_at = time.monotonic() + (1.0, 2.0, 4.0, 8.0)[self._art_attempts-1]
        if need_art:
            raw, content_type = await self._read_thumb(props)
            with self._guard:
                if self._art_key == track_key:
                    self._art_bytes = raw
                    self._art_type = content_type
        duration = self._seconds(timeline.end_time) - self._seconds(timeline.start_time)
        position = self._seconds(timeline.position) - self._seconds(timeline.start_time)
        try:
            from pycaw.pycaw import AudioUtilities
            endpoint = AudioUtilities.GetSpeakers().EndpointVolume
            volume = round(endpoint.GetMasterVolumeLevelScalar() * 100)
            if bool(endpoint.GetMute()):
                volume = 0
        except Exception as exc:
            LOG.debug('Windows master volume unavailable: %s', exc)
            volume = None
        playing = self._status_is_playing(play)
        # A local thumbnail URL does not expose file paths or token data.
        art_url = '/api/pc/artwork?key=' + str(abs(hash(track_key))) if self._art_bytes else None
        return {'ok':True,'connected':True,'has_playback':True,
                'title':title, 'artist':artist, 'album':album,
                'track_key':track_key, 'artwork':art_url,
                'playing':playing,
                'duration_ms':max(0,round(duration*1000)),
                'progress_ms':max(0,round(position*1000)),
                'device':source.split('!')[0], 'device_id':source,
                'volume':volume, 'supports_volume':volume is not None,
                'source':source}

    def status(self, force=False) -> dict:
        with self._guard:
            if self._cached and not force and time.monotonic() < self._cached.valid_until:
                return dict(self._cached.value)
            try:
                state = asyncio.run(self._media_info())
                self._cached = Snapshot(state, time.monotonic()+.55)
                return dict(state)
            except Exception as exc:
                LOG.warning('Windows media session error: %s', exc)
                return {'ok':False,'error':str(exc)[:250]}

    async def _media_command(self, action):
        manager_cls = self._imports()
        manager = await manager_cls.request_async()
        session = await self._select_session(manager)
        if session is None:
            return False
        methods = {'toggle':'try_toggle_play_pause_async',
                   'next':'try_skip_next_async','previous':'try_skip_previous_async'}
        return bool(await getattr(session,methods[action])())

    def command(self, action, value=None):
        if action == 'volume':
            if type(value) is not int or not 0 <= value <= 100:
                raise ValueError('Volume must be an integer between 0 and 100.')
            from pycaw.pycaw import AudioUtilities
            endpoint = AudioUtilities.GetSpeakers().EndpointVolume
            endpoint.SetMasterVolumeLevelScalar(value / 100, None)
            if value > 0 and endpoint.GetMute():
                endpoint.SetMute(0, None)
            accepted = True
        elif action in ('toggle','previous','next'):
            accepted = asyncio.run(self._media_command(action))
        else:
            raise ValueError('Unsupported local media command.')
        with self._guard:
            self._cached = None
        return accepted

    def artwork(self):
        with self._guard:
            return self._art_bytes, self._art_type

    def meter_state(self):
        with self._guard:
            return {'ok':True,'available':self._audio_ok,
                    'level':self._rms if self._audio_ok else 0.0,
                    'device':self._audio_device,
                    'message':self._audio_status}

    def start_meter(self):
        with self._guard:
            if self._capture_started:
                return
            self._capture_started = True
        threading.Thread(target=self._capture_audio, daemon=True, name='desk-thing-audio').start()

    def _capture_audio(self):
        try:
            import soundcard as sc
            import numpy as np
        except ImportError as exc:
            with self._guard:
                self._audio_status = 'Audio dependencies missing: pip install -r requirements-windows.txt'
            return
        retry = 0
        # WASAPI capture is speaker output, not microphone input; no audio samples are saved.
        while True:
            try:
                configured = os.environ.get('DESK_AUDIO_DEVICE','').strip()
                speaker = sc.get_speaker(configured) if configured else sc.default_speaker()
                microphone = sc.get_microphone(speaker.id, include_loopback=True)
                with self._guard:
                    self._audio_device = speaker.name
                    self._audio_ok = True
                    self._audio_status = 'WASAPI loopback active'
                with microphone.recorder(samplerate=48000, blocksize=2048) as rec:
                    while True:
                        start = time.monotonic()
                        samples = rec.record(numframes=2048)
                        if samples is None or not samples.size:
                            level = 0.0
                            time.sleep(0.04)
                        else:
                            rms = math.sqrt(float(np.mean(samples.astype('float32') ** 2)))
                            # Smooth, subtle UI amplitude; not clipping or passing raw audio over HTTP.
                            level = max(0., min(1., (rms - 0.004) * 8))
                        with self._guard:
                            self._rms = self._rms * .72 + level * .28
                        # Some WASAPI devices yield immediate silent buffers: cap CPU use.
                        time.sleep(max(0.0, 0.035 - (time.monotonic() - start)))
                retry = 0
            except Exception as exc:
                retry += 1
                with self._guard:
                    self._audio_ok = False
                    self._audio_status = 'Audio loopback unavailable: ' + str(exc)[:150]
                    self._rms = 0.0
                LOG.warning('Audio meter attempt %s: %s', retry, exc)
                time.sleep(min(10, max(2, retry * 2)))

windows = WindowsCompanion()

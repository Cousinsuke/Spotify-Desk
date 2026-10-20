"""Pure mocked Linux companion tests; no Spotify, D-Bus or audio hardware needed."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from linux_companion import LinuxCompanion


class LinuxTests(unittest.TestCase):
    def setUp(self):
        self.adapter = LinuxCompanion()
        self.calls = []
        self.metadata = ('Example Track\x1fExample Artist\x1fExample Album\x1f'
                         '187000000\x1fhttps://i.scdn.co/image/test\x1fspotify:track:test')

    def fake_run(self, *args, **kwargs):
        self.calls.append(args)
        if args == ('playerctl', '-l'): return 'vlc\nspotify\n'
        if args[:4] == ('playerctl', '-p', 'spotify', 'metadata'): return self.metadata
        if args == ('playerctl', '-p', 'spotify', 'status'): return 'Playing'
        if args == ('playerctl', '-p', 'spotify', 'position'): return '15.25'
        if args == ('wpctl', 'get-volume', '@DEFAULT_AUDIO_SINK@'): return 'Volume: 0.40'
        return ''

    @patch('linux_companion.shutil.which', return_value='/usr/bin/tool')
    def test_spotify_track(self, _):
        self.adapter._run = self.fake_run
        result = self.adapter.status(force=True)
        self.assertTrue(result['has_playback'])
        self.assertEqual(result['title'], 'Example Track')
        self.assertEqual(result['artist'], 'Example Artist')
        self.assertEqual(result['duration_ms'], 187000)
        self.assertEqual(result['progress_ms'], 15250)
        self.assertEqual(result['volume'], 40)
        self.assertEqual(result['device_id'], 'spotify')
        self.assertEqual(result['artwork'], 'https://i.scdn.co/image/test')

    @patch('linux_companion.shutil.which', return_value='/usr/bin/tool')
    def test_transport_and_volume(self, _):
        self.adapter._run = self.fake_run
        self.assertTrue(self.adapter.command('toggle'))
        self.assertTrue(self.adapter.command('next'))
        self.assertTrue(self.adapter.command('previous'))
        self.assertIn(('playerctl','-p','spotify','play-pause'),self.calls)
        self.assertIn(('playerctl','-p','spotify','next'),self.calls)
        self.assertIn(('playerctl','-p','spotify','previous'),self.calls)
        self.assertTrue(self.adapter.command('volume',20))
        self.assertIn(('wpctl','set-volume','@DEFAULT_AUDIO_SINK@','0.20'),self.calls)
        self.assertTrue(self.adapter.command('volume',0))
        self.assertIn(('wpctl','set-mute','@DEFAULT_AUDIO_SINK@','1'),self.calls)

    @patch('linux_companion.shutil.which', return_value='/usr/bin/tool')
    def test_empty_player_list(self, _):
        self.adapter._run = lambda *a, **k: ''
        self.assertFalse(self.adapter.status(force=True)['has_playback'])
        self.assertFalse(self.adapter.command('toggle'))

    @patch('linux_companion.shutil.which', return_value='/usr/bin/tool')
    def test_muted_volume(self, _):
        self.adapter._run = lambda *a, **k: 'Volume: 0.63 [MUTED]'
        self.assertEqual(self.adapter._volume(), 0)

    def test_bad_volumes(self):
        for value in (None, '10', -1, 101, 50.0):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.adapter.command('volume', value)


if __name__ == '__main__':
    unittest.main()

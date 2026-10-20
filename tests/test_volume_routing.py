"""Offline regression tests for volume source selection, no Flask/Spotify login required."""
import ast
import sys
import time
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'desk_ui.py'
mod = ast.parse(SOURCE.read_text())
functions = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in (
    '_same_spotify_track', '_cached_spotify_volume_state', '_pc_with_volume_source'
)]
for node in functions:
    node.decorator_list = []
code = compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec')

class FakeSpotifyException(Exception):
    pass

class VolumeRoutingTests(unittest.TestCase):
    def setUp(self):
        self.spot_state = {'has_playback': True, 'title':'Same Thing', 'artist':'A Little Sound',
                           'volume':37,'supports_volume':True}
        self.ns = {
            'time': time, 'lock': threading.RLock(), 'cooldown_until': 0.,
            'auth': Mock(get_cached_token=Mock(return_value=True)),
            'state_cache': {'value':None, 'expires':0.},
            'POLL_SECONDS': 5,
            'playback_state': lambda: self.spot_state,
            'SpotifyException': FakeSpotifyException,
            'error_json': Mock(),
        }
        exec(code,self.ns)
        self.local = {'ok':True,'has_playback':True,'source':'MPRIS · spotify',
                      'title':'Same Thing','artist':'A Little Sound','volume':100,'supports_volume':True}

    def test_spotify_volume_overrides_system(self):
        result = self.ns['_pc_with_volume_source'](self.local)
        self.assertEqual(result['volume_source'],'spotify')
        self.assertEqual(result['volume'],37)
        self.assertEqual(self.local['volume'],100)

    def test_different_local_player_keeps_system_volume(self):
        self.local['source'] = 'MPRIS · vlc'
        result = self.ns['_pc_with_volume_source'](self.local)
        self.assertEqual(result['volume_source'],'system')
        self.assertEqual(result['volume'],100)

    def test_mismatched_track_keeps_system_volume(self):
        self.spot_state['title'] = 'Other Song'
        result = self.ns['_pc_with_volume_source'](self.local)
        self.assertEqual(result['volume_source'],'system')

    def test_unauthorized_spotify_keeps_system_volume(self):
        self.ns['auth'].get_cached_token.return_value = False
        result = self.ns['_pc_with_volume_source'](self.local)
        self.assertEqual(result['volume_source'],'system')

    def test_disabled_spotify_volume(self):
        self.spot_state['supports_volume'] = False
        result = self.ns['_pc_with_volume_source'](self.local)
        self.assertEqual(result['volume_source'],'spotify')
        self.assertFalse(result['supports_volume'])

    def test_cache_reduces_api_requests(self):
        fn=Mock(return_value=self.spot_state)
        self.ns['playback_state']=fn
        self.ns['_pc_with_volume_source'](self.local)
        self.ns['_pc_with_volume_source'](self.local)
        self.assertEqual(fn.call_count,1)

if __name__ == '__main__':
    unittest.main()

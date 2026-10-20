"""Offline Phase 5 security/protocol regression tests (no Spotify or audio needed)."""
import json
import tempfile
import unittest
from pathlib import Path
try:
    from flask import Flask, jsonify
except ImportError:
    raise unittest.SkipTest("Flask not installed in build environment; test on Windows/Omarchy venv")

from device_bridge import PairingStore, install_device_bridge

LOCAL = {'REMOTE_ADDR': '127.0.0.1'}
LAN = {'REMOTE_ADDR': '192.168.1.77'}


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        # Only templates/static resolution; the test callbacks are fully offline.
        self.app = Flask('device_test', template_folder=str(Path(__file__).resolve().parents[1] / 'templates'),
                         static_folder=str(Path(__file__).resolve().parents[1] / 'static'))
        self.app.testing = True
        self.calls = []
        self.current_artwork = 'https://i.scdn.co/image/test'
        self.art_data = b'test'
        @self.app.get('/private-desktop')
        def priv(): return jsonify({'secret':'hidden'})
        def state(mode):
            return {'ok':True,'connected':True,'has_playback':True,'title':'Same Thing',
                    'artist':'A Little Sound','artwork':self.current_artwork,
                    'playing':True,'volume':45,'supports_volume':True}
        def cmd(mode, action, value):
            self.calls.append((mode,action,value))
            return jsonify({'ok':True,'action':action})
        self.store = install_device_bridge(self.app, base=root, lan_enabled=True, state_cb=state,
                                           command_cb=cmd, artwork_cb=lambda:(self.art_data,'image/jpeg'),
                                           meter_cb=lambda:{'available':True,'level':0.3})
        self.client = self.app.test_client()

    def pair(self):
        r=self.client.post('/api/device/pair',json={'code':self.store.code,'name':'Test device'},environ_overrides=LAN)
        self.assertEqual(r.status_code,200,r.json)
        return r.json['token']

    def auth(self, token):
        return {'Authorization':f'Bearer {token}'}

    def test_unauthenticated_device_endpoints_reject(self):
        self.assertEqual(self.client.get('/api/device/state',environ_overrides=LAN).status_code,401)
        self.assertEqual(self.client.post('/api/device/action',json={'action':'next'},environ_overrides=LAN).status_code,401)
        self.assertEqual(self.client.get('/api/device/artwork',environ_overrides=LAN).status_code,401)
        self.assertEqual(self.client.get('/api/device/events',environ_overrides=LAN).status_code,401)

    def test_lan_cannot_access_original_apis_or_pair_page(self):
        for path in ['/','/login','/api/status','/api/pc/control','/private-desktop','/pair','/api/device/pairing']:
            self.assertEqual(self.client.get(path,environ_overrides=LAN).status_code,403,path)
        self.assertEqual(self.client.get('/device',environ_overrides=LAN).status_code,200)
        self.assertEqual(self.client.get('/static/ui.css',environ_overrides=LAN).status_code,200)
        self.assertEqual(self.client.get('/private-desktop',environ_overrides=LOCAL).status_code,200)

    def test_pairing_one_time_and_token_authentication(self):
        code=self.store.code
        token=self.pair()
        self.assertEqual(len(token),64)
        self.assertEqual(self.client.post('/api/device/pair',json={'code':code},environ_overrides=LAN).status_code,403)
        r=self.client.get('/api/device/state',headers=self.auth(token),environ_overrides=LAN)
        self.assertEqual(r.json['title'],'Same Thing')
        self.assertEqual(r.json['mode'],'pc')
        # HTTPS artwork from Linux MPRIS must NOT be redirected to the
        # Windows-style local thumbnail route; it previously caused 404s.
        self.assertEqual(r.json['artwork'],'https://i.scdn.co/image/test')
        self.assertEqual(self.client.get('/api/device/artwork',headers=self.auth(token),environ_overrides=LAN).status_code,404)

    def test_local_thumb_proxy_and_missing_art(self):
        token=self.pair()
        headers=self.auth(token)
        self.current_artwork='/api/pc/artwork?key=123'
        r=self.client.get('/api/device/state',headers=headers,environ_overrides=LAN)
        self.assertEqual(r.json['artwork'],'/api/device/artwork?key=123')
        ok=self.client.get('/api/device/artwork?key=123',headers=headers,environ_overrides=LAN)
        self.assertEqual(ok.status_code,200)
        self.assertEqual(ok.data,b'test')
        # Stale requests after a track change cannot show the wrong image.
        self.assertEqual(self.client.get('/api/device/artwork?key=111',headers=headers,environ_overrides=LAN).status_code,404)
        self.art_data=b''
        self.assertEqual(self.client.get('/api/device/artwork?key=123',headers=headers,environ_overrides=LAN).status_code,404)
        self.current_artwork=None
        self.assertIsNone(self.client.get('/api/device/state',headers=headers,environ_overrides=LAN).json['artwork'])

    def test_controls_mode_and_knob(self):
        token=self.pair()
        headers=self.auth(token)
        self.assertEqual(self.client.post('/api/device/action',json={'action':'volume_step','value':5},headers=headers,environ_overrides=LAN).status_code,200)
        self.assertEqual(self.calls.pop(),('pc','volume',50))
        self.assertEqual(self.client.post('/api/device/action',json={'action':'mode','value':'spotify'},headers=headers,environ_overrides=LAN).status_code,200)
        self.assertEqual(self.client.post('/api/device/action',json={'action':'next'},headers=headers,environ_overrides=LAN).status_code,200)
        self.assertEqual(self.calls.pop(),('spotify','next',None))
        self.assertEqual(self.client.post('/api/device/action',json={'action':'volume','value':101},headers=headers,environ_overrides=LAN).status_code,400)
        self.assertEqual(self.client.get('/api/device/state',headers=headers,environ_overrides=LAN).json['artwork'],'https://i.scdn.co/image/test')

    def test_bad_origin_and_pairing_attempts(self):
        self.assertEqual(self.client.post('/api/device/pair',json={'code':self.store.code},headers={'Origin':'http://malicious.test'},environ_overrides=LAN).status_code,403)
        for i in range(5):
            self.assertEqual(self.client.post('/api/device/pair',json={'code':'000000' if self.store.code!='000000' else '000001'},environ_overrides=LAN).status_code,403)
        self.assertEqual(self.client.post('/api/device/pair',json={'code':self.store.code},environ_overrides=LAN).status_code,429)

    def test_local_only_revoke(self):
        token=self.pair()
        self.assertEqual(self.client.post('/api/device/pairing/revoke-all',json={},environ_overrides=LAN).status_code,403)
        self.assertEqual(self.client.post('/api/device/pairing/revoke-all',json={},environ_overrides=LOCAL).status_code,200)
        self.assertEqual(self.client.get('/api/device/state',headers=self.auth(token),environ_overrides=LAN).status_code,401)
        self.assertEqual(self.store.devices,{})

    def test_tokens_survive_restart_no_pair_code_persistence(self):
        token=self.pair()
        other=PairingStore(Path(self.tmp.name)/'.desk_devices.json')
        self.assertIsNotNone(other.get('Bearer '+token))
        self.assertNotEqual(self.store.code,other.code)

    def test_stream_emits_state_and_meter(self):
        token=self.pair()
        response=self.client.get('/api/device/events',headers=self.auth(token),environ_overrides=LAN,buffered=False)
        it=iter(response.response)
        self.assertIn(b'retry:', next(it))
        self.assertIn(b'event: state',next(it))
        self.assertIn(b'event: meter',next(it))
        response.close()


if __name__=='__main__':unittest.main()

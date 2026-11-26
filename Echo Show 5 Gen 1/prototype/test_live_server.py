"""Run locally using the preview virtual environment. No network or credentials."""
import unittest
from unittest.mock import patch
import live_server as s

class LocalTests(unittest.TestCase):
    def setUp(self):
        self.client=s.app.test_client()
        s.backoff=0.0
        s.token=None
        s.pending=None
        s.playback_cache=None
        s.devices_cache=None
        s.saved_cache.clear()
        s.last_snapshot=None
        s.last_seen=None
        s.resume_blocked=False
        self.url=s.ORIGIN
        self.headers={"X-Desk-Preview":"1","Origin":self.url}
    def test_requires_header(self):
        self.assertEqual(self.client.get("/api/spotify/state",base_url=self.url).status_code,403)
    def test_wrong_host(self):
        self.assertEqual(self.client.get("/",base_url="http://evil.invalid").status_code,403)
    def test_wrong_origin(self):
        self.assertEqual(self.client.post("/api/spotify/command",base_url=self.url,headers={"X-Desk-Preview":"1","Origin":"http://evil.invalid"},json={"action":"toggle"}).status_code,403)
    def test_no_token(self):
        self.assertFalse(self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json["connected"])
    def test_no_source_files_served(self):
        self.assertEqual(self.client.get("/live_server.py",base_url=self.url).status_code,404)
    def test_callback_rejects_missing_state(self):
        self.assertEqual(self.client.get("/spotify/callback?code=fake",base_url=self.url).status_code,400)
    def test_unknown_command(self):
        self.assertEqual(self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"unknown"}).status_code,400)
    def test_real_state_mock(self):
        s.token={"access_token":"test"}
        sample={"item":{"name":"Synthetic","type":"track","uri":"spotify:track:abc","duration_ms":100000,"artists":[{"name":"Example"}]},"device":{"id":"d","name":"Mock"},"is_playing":True,"progress_ms":12000}
        with patch.object(s,"player",return_value=sample),patch.object(s,"saved_status",return_value=False):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertEqual(data["title"],"Synthetic")
            self.assertEqual(data["position"],12)
            self.assertTrue(data["controllable"])
            self.assertNotIn("access_token",data)
    def test_command_device_changed(self):
        with patch.object(s,"player",return_value={"device":{"id":"new"}}),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"toggle","device":"old"})
            self.assertEqual(r.status_code,409)
            api.assert_not_called()
    def test_pause_non_json_success(self):
        s.token={"access_token":"test","expires_at":s.time.monotonic()+3600}
        player={"device":{"id":"d"},"is_playing":True}
        response=s.requests.Response()
        response.status_code=200
        response._content=b"OK"
        with patch.object(s,"player",return_value=player),patch.object(s.requests,"request",return_value=response) as upstream:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"toggle","device":"d"})
            self.assertEqual(r.status_code,200)
            self.assertTrue(r.json["ok"])
            self.assertIsNone(s.playback_cache)
            self.assertEqual(upstream.call_args.args[0],"PUT")
            self.assertTrue(upstream.call_args.args[1].endswith("/pause"))
    def test_success_204_with_body(self):
        s.token={"access_token":"test","expires_at":s.time.monotonic()+3600}
        response=s.requests.Response()
        response.status_code=204
        response._content=b"not JSON"
        with patch.object(s.requests,"request",return_value=response):
            self.assertIsNone(s.spotify("PUT","/me/player/pause"))
            self.assertIsNone(s.spotify("GET","/me/player"))
    def test_invalid_get_is_controlled_error(self):
        s.token={"access_token":"test","expires_at":s.time.monotonic()+3600}
        response=s.requests.Response()
        response.status_code=200
        response._content=b"not JSON"
        with patch.object(s.requests,"request",return_value=response):
            with self.assertRaises(s.ApiError) as err:
                s.spotify("GET","/me/player")
            self.assertEqual(err.exception.status,502)
    def test_failed_write_not_treated_as_success(self):
        s.token={"access_token":"test","expires_at":s.time.monotonic()+3600}
        response=s.requests.Response()
        response.status_code=403
        response._content=b"Forbidden"
        with patch.object(s.requests,"request",return_value=response):
            with self.assertRaises(s.ApiError) as err:
                s.spotify("PUT","/me/player/pause")
            self.assertEqual(err.exception.status,403)
    def test_inactive_keeps_last_track_and_verified_device(self):
        s.token={"access_token":"test"}
        s.last_snapshot={"title":"Last track","deviceId":"d","playing":True,"position":12}
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[{"id":"d","name":"Phone","restricted":False,"active":False}]):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertEqual(data["title"],"Last track")
            self.assertTrue(data["inactive"])
            self.assertFalse(data["playing"])
            self.assertTrue(data["controllable"])
            self.assertEqual(data["deviceId"],"d")
            self.assertIsNone(data["saved"])
    def test_inactive_unavailable_device_disables_controls(self):
        s.token={"access_token":"test"}
        s.last_snapshot={"title":"Last track","deviceId":"d"}
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[]):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertFalse(data["controllable"])
            self.assertIsNone(data["deviceId"])
    def test_skip_after_empty_playback_uses_verified_same_device(self):
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[{"id":"d","name":"Phone","restricted":False,"active":False}]),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"previous","device":"d"})
            self.assertEqual(r.status_code,200)
            api.assert_called_once_with("POST","/me/player/previous",{"device_id":"d"})
    def test_skip_never_targets_other_active_device(self):
        rows=[{"id":"d","restricted":False,"active":False},{"id":"other","restricted":False,"active":True}]
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=rows),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"previous","device":"d"})
            self.assertEqual(r.status_code,409)
            api.assert_not_called()
    def test_explicit_pause_does_not_invert_stale_state(self):
        with patch.object(s,"player",return_value={"device":{"id":"d"},"is_playing":False}),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"toggle","device":"d","value":False})
            self.assertEqual(r.status_code,200)
            api.assert_not_called()
    def test_resume_on_verified_device_without_active_playback(self):
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[{"id":"d","restricted":False,"active":False}]),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"toggle","device":"d","value":True})
            self.assertEqual(r.status_code,200)
            api.assert_called_once_with("PUT","/me/player/play",{"device_id":"d"})
    def remember_device(self, age=0):
        s.last_snapshot={"title":"Last track","device":"Phone","deviceId":"d","controllable":True,"playing":False,"position":12}
        s.last_seen=s.time.monotonic()-age
    def test_recent_unlisted_device_keeps_resume_enabled(self):
        s.token={"access_token":"test"}
        self.remember_device()
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[]):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertTrue(data["controllable"])
            self.assertEqual(data["recovery"],"recent")
            self.assertEqual(data["deviceId"],"d")
            self.assertFalse(data["playing"])
            self.assertTrue(data["disallows"]["skipping_next"])
    def test_recent_unlisted_device_explicit_resume(self):
        self.remember_device()
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[]),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"toggle","device":"d","value":True})
            self.assertEqual(r.status_code,200)
            api.assert_called_once_with("PUT","/me/player/play",{"device_id":"d"})
    def test_recent_unlisted_device_no_skip(self):
        self.remember_device()
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[]),patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"next","device":"d"})
            self.assertEqual(r.status_code,409)
            api.assert_not_called()
    def test_expired_recent_device(self):
        self.remember_device(age=301)
        self.assertIsNone(s.recovery_target("d",[]))
    def test_recent_other_active_or_restricted_device(self):
        self.remember_device()
        self.assertIsNone(s.recovery_target("d",[{"id":"other","active":True,"restricted":False}]))
        self.assertIsNone(s.recovery_target("d",[{"id":"d","active":False,"restricted":True}]))
        self.assertIsNone(s.recovery_target("unseen",[]))
    def test_resume_404_blocks_unlisted_fallback(self):
        self.remember_device()
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[]),patch.object(s,"spotify",side_effect=s.ApiError(404,"Not found")) as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"toggle","device":"d","value":True})
            self.assertEqual(r.status_code,404)
            self.assertTrue(s.resume_blocked)
            self.assertIsNone(s.recovery_target("d",[]))
            api.assert_called_once()
    def test_verified_target_restores_recovery_after_rejection(self):
        self.remember_device()
        s.resume_blocked=True
        s.token={"access_token":"test"}
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[{"id":"d","name":"Phone","active":False,"restricted":False}]):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertEqual(data["recovery"],"verified")
            self.assertFalse(s.resume_blocked)
if __name__=="__main__":unittest.main()

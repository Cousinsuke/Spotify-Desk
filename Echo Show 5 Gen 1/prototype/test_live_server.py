"""Run locally using the preview virtual environment. No network or credentials."""
import unittest
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import live_server as s

class LocalTests(unittest.TestCase):
    def setUp(self):
        self.client=s.app.test_client()
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        cache=patch.object(s,'TOKEN_PATH',Path(self.temp.name)/'.spotify_token.json')
        cache.start();self.addCleanup(cache.stop)
        s.refresh_retry_at=0.0
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
    def test_volume_fields_strict_types_and_bounds(self):
        for device,expected in [
            ({"supports_volume":True,"volume_percent":0},{"supportsVolume":True,"volumePercent":0}),
            ({"supports_volume":False,"volume_percent":100},{"supportsVolume":False,"volumePercent":100}),
            ({},{"supportsVolume":None,"volumePercent":None}),
            ({"supports_volume":1,"volume_percent":True},{"supportsVolume":None,"volumePercent":None}),
            ({"supports_volume":"true","volume_percent":101},{"supportsVolume":None,"volumePercent":None}),
            ({"volume_percent":-1},{"supportsVolume":None,"volumePercent":None}),
        ]:
            self.assertEqual(s.volume_fields(device),expected)
    def test_device_list_reports_volume_capability(self):
        with patch.object(s,"spotify",return_value={"devices":[
            {"id":"d","name":"Example","type":"Computer","supports_volume":True,"volume_percent":42},
            {"id":"e","supports_volume":False,"volume_percent":None},
        ]}):
            data=self.client.get("/api/spotify/devices",base_url=self.url,headers=self.headers).json["devices"]
            self.assertEqual(data[0]["type"],"Computer")
            self.assertIs(data[0]["supportsVolume"],True)
            self.assertEqual(data[0]["volumePercent"],42)
            self.assertIs(data[1]["supportsVolume"],False)
            self.assertIsNone(data[1]["volumePercent"])
    def test_current_state_volume_and_inactive_clear(self):
        s.token={"access_token":"test"}
        sample={"item":{"name":"Synthetic","type":"track","uri":"spotify:track:abc"},"device":{"id":"d","name":"Example","supports_volume":True,"volume_percent":40},"is_playing":True}
        with patch.object(s,"player",return_value=sample),patch.object(s,"saved_status",return_value=False):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertIs(data["supportsVolume"],True)
            self.assertEqual(data["volumePercent"],40)
        with patch.object(s,"player",return_value={}),patch.object(s,"devices",return_value=[{"id":"d","name":"Example","restricted":False,"active":False}]):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertTrue(data["inactive"])
            self.assertIsNone(data["supportsVolume"])
            self.assertIsNone(data["volumePercent"])
    def test_remote_volume_targets_active_device(self):
        player={"device":{"id":"d","is_active":True,"supports_volume":True,"volume_percent":100}}
        with patch.object(s,"player",return_value=player) as read,patch.object(s,"spotify") as api:
            r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"volume","device":"d","value":-5})
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.json["requestedVolume"],95)
            read.assert_called_once_with(True)
            api.assert_called_once_with("PUT","/me/player/volume",{"device_id":"d","volume_percent":95})
    def test_remote_volume_rejects_invalid_and_unsupported(self):
        base={"id":"d","is_active":True,"supports_volume":True,"volume_percent":50}
        for device in [dict(base,id="other"),dict(base,is_active=False),dict(base,is_restricted=True),dict(base,supports_volume=False),dict(base,volume_percent=None),{}]:
            with patch.object(s,"player",return_value={"device":device}),patch.object(s,"spotify") as api:
                r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"volume","device":"d","value":-5})
                self.assertEqual(r.status_code,409);api.assert_not_called()
        for value in [True,0,1,30,-30,5.0,None]:
            with patch.object(s,"player") as read,patch.object(s,"spotify") as api:
                r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"volume","device":"d","value":value})
                self.assertEqual(r.status_code,400);read.assert_not_called();api.assert_not_called()
    def test_remote_volume_clamps_and_noop(self):
        for current,delta,expected in [(2,-5,0),(98,5,100),(100,5,100),(0,-5,0)]:
            device={"id":"d","is_active":True,"supports_volume":True,"volume_percent":current}
            with patch.object(s,"player",return_value={"device":device}),patch.object(s,"spotify") as api:
                r=self.client.post("/api/spotify/command",base_url=self.url,headers=self.headers,json={"action":"volume","device":"d","value":delta})
                self.assertEqual(r.status_code,200);self.assertEqual(r.json["requestedVolume"],expected)
                if current==expected:api.assert_not_called()
                else:api.assert_called_once_with("PUT","/me/player/volume",{"device_id":"d","volume_percent":expected})
    def test_state_reports_playback_sample_age(self):
        s.token={"access_token":"test"}
        sample={"item":{"name":"Synthetic","type":"track","uri":"spotify:track:abc","duration_ms":100000},"device":{"id":"d"},"is_playing":True,"progress_ms":12000}
        s.playback_cache=(100.0,sample)
        with patch.object(s,"player",return_value=sample),patch.object(s,"saved_status",return_value=False),patch.object(s.time,"monotonic",return_value=101.25):
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertEqual(data["positionMs"],12000)
            self.assertEqual(data["sampleAgeMs"],1250)
    def test_fast_state_does_not_block_on_library_lookup(self):
        s.token={"access_token":"test"}
        sample={"item":{"name":"Synthetic","type":"track","uri":"spotify:track:abc","duration_ms":100000},"device":{"id":"d"},"is_playing":True,"progress_ms":1000}
        with patch.object(s,"player",return_value=sample) as read,patch.object(s,"saved_status",return_value=True) as saved:
            data=self.client.get("/api/spotify/state?fresh=1&fast=1",base_url=self.url,headers=self.headers).json
            self.assertEqual(data["title"],"Synthetic")
            self.assertEqual(data["trackKey"],"spotify:track:abc")
            self.assertIsNone(data["saved"])
            read.assert_called_once_with(True)
            saved.assert_not_called()
            s.saved_cache["spotify:track:abc"]=(s.time.monotonic(),False)
            data=self.client.get("/api/spotify/state?fresh=1&fast=1",base_url=self.url,headers=self.headers).json
            self.assertIs(data["saved"],False)
            saved.assert_not_called()
            data=self.client.get("/api/spotify/state",base_url=self.url,headers=self.headers).json
            self.assertIs(data["saved"],True)
            saved.assert_called_once_with("spotify:track:abc")
    def test_track_diagnostics_redacts_and_compares(self):
        s.token={"access_token":"test"}
        first={"item":{"uri":"spotify:track:old","name":"Private title"},"device":{"id":"private-device"},"timestamp":100,"progress_ms":5000,"is_playing":True}
        second={"item":{"uri":"spotify:track:new"},"timestamp":200,"progress_ms":200,"is_playing":True}
        with patch.object(s,"spotify",side_effect=[first,second]) as api:
            data=self.client.get("/api/spotify/diagnostics/track",base_url=self.url,headers=self.headers).json
            self.assertNotEqual(data["player"]["track"],data["currentlyPlaying"]["track"])
            self.assertEqual(data["currentlyPlaying"]["timestamp"],200)
            self.assertIsNone(data["sameDevice"])
            self.assertNotIn("private-device",str(data))
            self.assertNotIn("Private title",str(data))
            self.assertNotIn("spotify:track:",str(data))
            self.assertEqual([c.args for c in api.call_args_list],[("GET","/me/player"),("GET","/me/player/currently-playing")])
    def test_track_diagnostics_stops_on_rate_limit(self):
        s.token={"access_token":"test"}
        with patch.object(s,"spotify",side_effect=s.ApiError(429,"rate limit")) as api:
            data=self.client.get("/api/spotify/diagnostics/track",base_url=self.url,headers=self.headers).json
            self.assertEqual(data["player"]["status"],429)
            self.assertNotIn("currentlyPlaying",data)
            api.assert_called_once()
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
    def token_response(self, status=200, data=None):
        r=s.requests.Response();r.status_code=status
        r._content=json.dumps(data if data is not None else {"access_token":"synthetic-access","refresh_token":"synthetic-refresh","expires_in":3600}).encode()
        return r
    def test_auth_persists_refresh_only_and_restores(self):
        with patch.object(s.requests,"post",return_value=self.token_response()):
            s.exchange({"grant_type":"authorization_code","code":"synthetic"})
        self.assertEqual(s.TOKEN_PATH.stat().st_mode & 0o777,0o600)
        self.assertNotIn("access_token",json.loads(s.TOKEN_PATH.read_text()))
        s.token=s.read_refresh()
        self.assertEqual(s.token,{"refresh_token":"synthetic-refresh","expires_at":0})
        with patch.object(s.requests,"post",return_value=self.token_response(data={"access_token":"new-access","expires_in":3600})) as post,patch.object(s.requests,"request",return_value=self.token_response(204)):
            self.assertIsNone(s.spotify("GET","/me/player"))
            self.assertEqual(post.call_args.kwargs["data"]["refresh_token"],"synthetic-refresh")
        self.assertEqual(s.token["refresh_token"],"synthetic-refresh")
    def test_rotated_refresh_is_saved(self):
        s.save_refresh("old")
        s.token=s.read_refresh()
        with patch.object(s.requests,"post",return_value=self.token_response()):
            s.exchange({"grant_type":"refresh_token","refresh_token":"old"})
        self.assertEqual(s.read_refresh()["refresh_token"],"synthetic-refresh")
    def test_expired_refresh_removes_cache(self):
        s.save_refresh("old");s.token=s.read_refresh()
        with patch.object(s.requests,"post",return_value=self.token_response(400,{"error":"invalid_grant"})):
            with self.assertRaises(s.ApiError):s.exchange({"grant_type":"refresh_token","refresh_token":"old"})
        self.assertIsNone(s.token);self.assertFalse(s.TOKEN_PATH.exists())
    def test_network_failure_keeps_cache_and_backs_off(self):
        s.save_refresh("old");s.token=s.read_refresh()
        with patch.object(s.requests,"post",side_effect=s.requests.ConnectionError) as post:
            for _ in range(2):
                with self.assertRaises(s.ApiError):s.exchange({"grant_type":"refresh_token","refresh_token":"old"})
            post.assert_called_once()
        self.assertEqual(s.read_refresh()["refresh_token"],"old")
    def test_wrong_client_and_scopes_not_restored(self):
        s.save_refresh("old")
        with patch.object(s,"CLIENT","different-client"):self.assertIsNone(s.read_refresh())
        with patch.object(s,"SCOPES","different-scopes"):self.assertIsNone(s.read_refresh())
    def test_cache_permissions_and_symlink(self):
        s.save_refresh("old");s.TOKEN_PATH.chmod(0o644)
        self.assertIsNone(s.read_refresh())
        s.TOKEN_PATH.unlink()
        target=s.TOKEN_PATH.with_name("target");target.write_text("not a cache")
        s.TOKEN_PATH.symlink_to(target)
        self.assertIsNone(s.read_refresh())
    def test_api_401_does_not_replay_write(self):
        s.save_refresh("old")
        s.token={"refresh_token":"old","access_token":"old-access","expires_at":s.time.monotonic()+3600}
        with patch.object(s.requests,"request",return_value=self.token_response(401)) as api:
            with self.assertRaises(s.ApiError):s.spotify("PUT","/me/player/pause")
            api.assert_called_once()
        self.assertEqual(s.token["expires_at"],0)
        self.assertEqual(s.read_refresh()["refresh_token"],"old")
    def test_cache_not_served(self):
        s.save_refresh("old")
        self.assertEqual(self.client.get("/.spotify_token.json",base_url=self.url).status_code,404)
if __name__=="__main__":unittest.main()

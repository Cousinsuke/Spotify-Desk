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
if __name__=="__main__":unittest.main()

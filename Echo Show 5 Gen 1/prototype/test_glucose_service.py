"""Offline tests of the preview adapter and route; no actual Gluroo connection."""
import unittest
from unittest.mock import Mock,patch
import glucose_service as g
import live_server as s

class GlucoseTests(unittest.TestCase):
    def setUp(self):
        self.now=1800000000
        self.reader=Mock(config_error=False,url="https://example.invalid")
        self.svc=g.GlucoseService(self.reader,clock=lambda:self.now,monotonic=lambda:100)
        self.rows=[{"timestamp":self.now*1000-60000,"mmol":6.1,"direction":"Flat"}]
        self.reader.state.return_value={"status":"live","readings":self.rows,"retry_seconds":150}
    def test_refresh_and_age(self):
        self.svc.refresh()
        self.assertEqual(self.svc.snapshot()["status"],"live")
        self.now+=600
        self.assertEqual(self.svc.snapshot()["status"],"stale")
        self.now+=86400
        self.assertEqual(self.svc.snapshot()["status"],"unavailable")
        self.assertEqual(self.svc.snapshot()["readings"],[])
    def test_failure_retains_stale(self):
        self.svc.refresh()
        self.reader.state.side_effect=RuntimeError("private error")
        self.svc.refresh()
        result=self.svc.snapshot()
        self.assertEqual(result["status"],"stale")
        self.assertNotIn("private error",str(result))
    def test_unconfigured(self):
        self.reader.url=""
        service=g.GlucoseService(self.reader)
        self.assertEqual(service.snapshot()["status"],"not_configured")
        self.reader.state.assert_not_called()
    def test_nonblocking(self):
        with patch.object(g.threading,"Thread") as thread:
            self.assertEqual(self.svc.snapshot()["status"],"loading")
            self.svc.snapshot()
            thread.assert_called_once()
            self.reader.state.assert_not_called()
    def test_local_route(self):
        c=s.app.test_client()
        with patch.object(g.service,"snapshot",return_value={"status":"not_configured","readings":[]}):
            self.assertEqual(c.get("/api/glucose",base_url=s.ORIGIN).status_code,403)
            self.assertEqual(c.get("/api/glucose",base_url=s.ORIGIN,headers={"X-Desk-Preview":"1","Sec-Fetch-Site":"cross-site"}).status_code,403)
            self.assertEqual(c.get("/api/glucose",base_url=s.ORIGIN,headers={"X-Desk-Preview":"1"},environ_overrides={"REMOTE_ADDR":"192.168.1.20"}).status_code,403)
            r=c.get("/api/glucose",base_url=s.ORIGIN,headers={"X-Desk-Preview":"1"},environ_overrides={"REMOTE_ADDR":"127.0.0.1"})
            self.assertEqual(r.status_code,200)
            self.assertEqual(r.headers["Cache-Control"],"no-store")
            self.assertEqual(r.json["status"],"not_configured")
    def test_source_not_served(self):
        c=s.app.test_client()
        self.assertEqual(c.get("/glucose_service.py",base_url=s.ORIGIN).status_code,404)
if __name__=="__main__":unittest.main()

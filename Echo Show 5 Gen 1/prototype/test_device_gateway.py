"""Sample gateway authorization regression tests, no network or actual user data."""
import tempfile
import unittest
from pathlib import Path
import device_gateway as g

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"devices.sqlite"
        g.setup_db(self.path)
        self.now=1000
        self.app=g.create_app(self.path,"192.168.50.10","192.168.50.0/24",lambda:self.now)
        self.client=self.app.test_client()
        self.base="https://192.168.50.10:8443"
    def req(self,path,method="GET",**kwargs):
        kwargs.setdefault("environ_overrides",{"REMOTE_ADDR":"192.168.50.20"})
        kwargs.setdefault("base_url",self.base)
        return self.client.open(path,method=method,**kwargs)
    def pair(self):
        return self.req("/pair","POST",data={"code":g.issue(self.path,self.now)},headers={"Origin":self.base})
    def test_unpaired(self):
        self.assertEqual(self.req("/").status_code,303)
        self.assertEqual(self.req("/app.js").status_code,401)
        self.assertEqual(self.req("/pair").status_code,200)
    def test_pair_cookie_and_sample(self):
        response=self.pair()
        self.assertEqual(response.status_code,303)
        cookie=response.headers["Set-Cookie"]
        for flag in ("Secure","HttpOnly","SameSite=Strict","Path=/","__Host-desk_device"):
            self.assertIn(flag,cookie)
        self.assertEqual(self.req("/").status_code,200)
        self.assertEqual(self.req("/?live=1").status_code,303)
        self.assertEqual(self.req("/app.js").status_code,200)
        self.assertEqual(self.req("/").headers["Cache-Control"],"no-store")
    def test_no_live_paths(self):
        self.pair()
        for path in ("/api/glucose","/api/spotify/state","/api/system","/spotify/login","/spotify/callback","/.env","/.spotify_token.json","/device_gateway.py","/ca.crt","/server.key"):
            self.assertEqual(self.req(path).status_code,404,path)
        self.assertEqual(self.req("/api/spotify/command","POST",headers={"Origin":self.base}).status_code,404)
    def test_boundary(self):
        self.assertEqual(self.req("/pair",base_url="http://192.168.50.10:8443").status_code,403)
        self.assertEqual(self.req("/pair",base_url="https://other:8443").status_code,403)
        self.assertEqual(self.req("/pair",environ_overrides={"REMOTE_ADDR":"192.168.51.20"}).status_code,403)
        self.assertEqual(self.req("/pair",headers={"Sec-Fetch-Site":"cross-site"}).status_code,403)
        self.assertEqual(self.req("/pair","POST",data={"code":"x"}).status_code,403)
    def test_one_time_and_expiry(self):
        code=g.issue(self.path,self.now)
        token=g.exchange(self.path,code,self.now)
        self.assertTrue(g.authorized(self.path,token,self.now))
        self.assertIsNone(g.exchange(self.path,code,self.now))
        self.assertFalse(g.authorized(self.path,token,self.now+g.SESSION_SECONDS))
        code=g.issue(self.path,self.now)
        self.assertIsNone(g.exchange(self.path,code,self.now+600))
    def test_attempt_limit_and_revocation(self):
        code=g.issue(self.path,self.now)
        for _ in range(8):self.assertIsNone(g.exchange(self.path,"wrong",self.now))
        self.assertIsNone(g.exchange(self.path,code,self.now))
        self.pair()
        g.revoke(self.path)
        self.assertEqual(self.req("/").status_code,303)
    def test_private_network(self):
        for bind,network in (("0.0.0.0","0.0.0.0/0"),("192.168.50.10","192.168.0.0/16"),("8.8.8.8","8.8.8.0/24")):
            with self.assertRaises(ValueError):g.validate_network(bind,network)

if __name__=="__main__":unittest.main()

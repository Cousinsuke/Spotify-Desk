import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from pc_agent import handler_for, snapshot, valid_token


class Adapter:
    calls = 0
    def status(self):
        self.calls += 1
        return {"ok": True, "has_playback": True, "title": "Synthetic",
                "artist": "Example", "track_key": "private-key", "playing": True,
                "progress_ms": 1000, "duration_ms": 2000, "volume": 45,
                "artwork": "file:///private", "device_id": "private"}


class PcAgentTests(unittest.TestCase):
    def test_snapshot(self):
        state = snapshot(Adapter())
        self.assertTrue(state["playing"])
        self.assertEqual(state["positionMs"], 1000)
        self.assertEqual(state["volume"], 45)
        self.assertNotIn("private", json.dumps(state))
        self.assertNotIn("artwork", state)
        self.assertEqual(len(state["trackKey"]), 64)

    def test_failure(self):
        class Broken:
            def status(self):
                raise RuntimeError("secret")
        self.assertEqual(snapshot(Broken()), {"ok": False, "error": "PC media adapter unavailable"})

    def test_token(self):
        self.assertTrue(valid_token("a" * 64))
        self.assertFalse(valid_token("A" * 64))
        self.assertFalse(valid_token("a" * 63))

    def test_http(self):
        adapter = Adapter()
        token = "a" * 64
        with HTTPServer(("127.0.0.1", 0), handler_for(adapter, token)) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            auth = {"Authorization": "Bearer " + token}
            try:
                for path, headers, method, code in [
                    ("/state", {}, "GET", 401),
                    ("/state", {"Authorization": "Bearer wrong"}, "GET", 401),
                    ("/state?fresh=1", auth, "GET", 404),
                    ("/control", auth, "POST", 405),
                ]:
                    with self.assertRaises(HTTPError) as cm:
                        urlopen(Request(base + path, headers=headers, method=method), timeout=3)
                    try:
                        self.assertEqual(cm.exception.code, code)
                    finally:
                        cm.exception.close()
                self.assertEqual(adapter.calls, 0)
                with urlopen(Request(base + "/state", headers=auth), timeout=3) as response:
                    self.assertEqual(response.headers["Cache-Control"], "no-store")
                    self.assertTrue(json.load(response)["ok"])
                self.assertEqual(adapter.calls, 1)
            finally:
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main()

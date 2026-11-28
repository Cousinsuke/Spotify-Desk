import json
import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from pc_agent import handler_for, snapshot, valid_token
from pc_protocol import track_key, approved_art, command_body


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

    def test_artwork_and_command_validation(self):
        self.assertEqual(approved_art("https://i.scdn.co/image/a"), "https://i.scdn.co/image/a")
        for bad in ("file:///private", "https://i.scdn.co.evil.test/image/a", "https://user@i.scdn.co/image/a"):
            self.assertEqual(approved_art(bad), "")
        for data in ({"action": "volume", "trackKey": "a"*64}, {"action": "next", "trackKey": "x"}, {"action": "next", "trackKey": "a"*64, "device": "x"}, {"action": [], "trackKey": "a"*64}):
            with self.assertRaises(ValueError):
                command_body(data)

    def test_authenticated_commands(self):
        class Controlled(Adapter):
            commands = []
            def command_for(self, action, expected):
                if expected != track_key("private-key"):
                    return False
                self.commands.append(action)
                return True
        adapter = Controlled()
        token = "a"*64
        with HTTPServer(("127.0.0.1", 0), handler_for(adapter, token, True)) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            base = f"http://127.0.0.1:{server.server_port}"
            auth = {"Authorization": "Bearer "+token, "Content-Type": "application/json"}
            try:
                with urlopen(Request(base+"/state", headers=auth), timeout=3) as response:
                    state = json.load(response)
                self.assertTrue(state["canControl"])
                for headers, data, code in [
                    ({"Content-Type":"application/json"}, {"action":"pause","trackKey":state["trackKey"]}, 401),
                    (auth, {"action":"toggle","trackKey":state["trackKey"]}, 400),
                    (auth, {"action":"pause","trackKey":"b"*64}, 409),
                ]:
                    with self.assertRaises(HTTPError) as cm:
                        urlopen(Request(base+"/command", headers=headers, data=json.dumps(data).encode()), timeout=3)
                    try:
                        self.assertEqual(cm.exception.code, code)
                    finally:
                        cm.exception.close()
                self.assertEqual(adapter.commands, [])
                with urlopen(Request(base+"/command", headers=auth, data=json.dumps({"action":"pause","trackKey":state["trackKey"]}).encode()), timeout=3) as response:
                    self.assertEqual(json.load(response), {"ok":True})
                self.assertEqual(adapter.commands, ["pause"])
            finally:
                server.shutdown()
                thread.join()

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

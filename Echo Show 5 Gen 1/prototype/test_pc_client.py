import unittest
from unittest.mock import patch
import pc_client


class PCClientTests(unittest.TestCase):
    def test_normalization(self):
        data = pc_client.normalize({"ok": True, "hasPlayback": True, "title": "Synthetic", "artist": "Example", "playing": False, "durationMs": 1000, "positionMs": 2000, "volume": 40, "trackKey": "private"})
        self.assertEqual(data["positionMs"], 1000)
        self.assertEqual(data["volume"], 40)
        self.assertFalse(data["playing"])
        self.assertNotIn("trackKey", data)

    def test_no_playback(self):
        data = pc_client.normalize({"ok": True, "hasPlayback": False, "title": "Old", "playing": True, "volume": True})
        self.assertEqual(data["title"], "")
        self.assertFalse(data["playing"])
        self.assertIsNone(data["volume"])

    def test_invalid(self):
        for value in (None, {}, {"ok": True, "hasPlayback": 1}):
            with self.assertRaises(ValueError):
                pc_client.normalize(value)

    @patch("pc_client.read_token", side_effect=FileNotFoundError)
    def test_unconfigured(self, _):
        self.assertFalse(pc_client.snapshot()["connected"])

    @patch("pc_client.read_token", return_value="a"*64)
    @patch("pc_client.requests.Session")
    def test_redirect_rejected(self, session, _):
        response = session.return_value.__enter__.return_value.get.return_value.__enter__.return_value
        response.status_code = 302
        self.assertFalse(pc_client.snapshot()["connected"])
        call = session.return_value.__enter__.return_value.get.call_args
        self.assertEqual(call.args[0], "http://127.0.0.1:8877/state")
        self.assertFalse(call.kwargs["allow_redirects"])

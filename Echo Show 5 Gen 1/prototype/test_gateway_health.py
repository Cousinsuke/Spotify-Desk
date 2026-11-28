"""Mocked local health checks; never contacts or restarts a real service."""
import unittest
from unittest.mock import patch, Mock
from pathlib import Path
import ssl
import gateway_health as h

class HealthTests(unittest.TestCase):
    @patch.object(h, "active", return_value=False)
    @patch.object(h, "probe")
    def test_stopped(self, probe, active):
        self.assertEqual(h.check(), 0)
        probe.assert_not_called()

    @patch.object(h, "active", return_value=True)
    @patch.object(h, "config", return_value=("192.168.50.10", "192.168.50.0/24"))
    @patch.object(h.time, "sleep")
    @patch.object(h.subprocess, "run")
    @patch.object(h, "probe")
    def test_health_decisions(self, probe, run, sleep, config, active):
        for results, expected, restarts in [
            (["ok"], 0, 0),
            (["unhealthy", "ok"], 0, 0),
            (["certificate"], 1, 0),
            (["unhealthy", "certificate"], 1, 0),
            (["unhealthy", "unhealthy"], 0, 1),
        ]:
            with self.subTest(results=results):
                probe.side_effect = results
                run.reset_mock()
                run.return_value.returncode = 0
                self.assertEqual(h.check(), expected)
                self.assertEqual(run.call_count, restarts)
                if restarts:
                    self.assertEqual(run.call_args.args[0], ["systemctl", "--user", "--no-block", "try-restart", h.UNIT])

    @patch.object(h.ssl, "create_default_context")
    @patch.object(h.http.client, "HTTPSConnection")
    def test_probe_requires_exact_redirect_and_closes(self, connect, context):
        conn = connect.return_value
        response = conn.getresponse.return_value.__enter__.return_value
        response.status = 303
        response.getheader.return_value = "/pair"
        self.assertEqual(h.probe(Path("/synthetic"), "192.168.50.10"), "ok")
        context.assert_called_once_with(cafile="/synthetic/ca.crt")
        conn.close.assert_called_once()
        response.getheader.return_value = "/other"
        self.assertEqual(h.probe(Path("/synthetic"), "192.168.50.10"), "unhealthy")
        conn.request.side_effect = ssl.SSLCertVerificationError("test")
        self.assertEqual(h.probe(Path("/synthetic"), "192.168.50.10"), "certificate")
        conn.request.side_effect = TimeoutError()
        self.assertEqual(h.probe(Path("/synthetic"), "192.168.50.10"), "unhealthy")

if __name__ == "__main__":
    unittest.main()

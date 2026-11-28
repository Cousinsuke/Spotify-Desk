"""Source regression checks for opt-in Omarchy user services."""
import configparser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent


def unit(name):
    parser = configparser.ConfigParser(interpolation=None)
    with (ROOT / name).open(encoding="utf-8") as handle:
        parser.read_file(handle)
    return parser


class PcServicesTests(unittest.TestCase):
    def test_agent(self):
        service = unit("spotify-desk-pc-agent.service")
        self.assertIn("pc_agent.py", service["Service"]["ExecStart"])
        self.assertTrue(service["Service"]["ExecStart"].endswith("serve --controls"))
        self.assertCountEqual(service["Service"]["Environment"].split(), [
            "PYTHONUNBUFFERED=1", "DBUS_SESSION_BUS_ADDRESS=unix:path=%t/bus", "XDG_RUNTIME_DIR=%t"
        ])
        self.assertEqual(service["Service"]["Restart"], "always")
        self.assertEqual(service["Install"]["WantedBy"], "default.target")

    def test_key_agent(self):
        service = unit("spotify-desk-pc-key-agent.service")
        self.assertEqual(service["Service"]["RuntimeDirectoryMode"], "0700")
        self.assertEqual(service["Service"]["ExecStart"], "/usr/bin/ssh-agent -D -a %t/spotify-desk-pc/agent.sock")

    def test_tunnel(self):
        service = unit("spotify-desk-pc-tunnel.service")
        command = service["Service"]["ExecStart"]
        for flag in ("IdentityAgent=%t/spotify-desk-pc/agent.sock", "IdentitiesOnly=yes",
                     "BatchMode=yes", "StrictHostKeyChecking=yes", "ForwardAgent=no",
                     "ExitOnForwardFailure=yes", "ServerAliveInterval=15",
                     "ServerAliveCountMax=3", "-N -T -R 127.0.0.1:8877:127.0.0.1:8877",
                     "-- ${DESK_PI_TARGET}"):
            self.assertIn(flag, command)
        self.assertEqual(service["Service"]["Restart"], "always")
        self.assertEqual(service["Service"]["RestartSec"], "15")
        self.assertEqual(service["Unit"]["StartLimitIntervalSec"], "0")
        self.assertEqual(service["Install"]["WantedBy"], "default.target")

    def test_install_does_not_activate(self):
        script = (ROOT / "install-pc-services.sh").read_text()
        self.assertIn("systemctl --user daemon-reload", script)
        self.assertNotIn("systemctl --user enable", script)
        self.assertNotIn("systemctl --user start ", script)
        self.assertNotIn("enable-linger", script)


if __name__ == "__main__":
    unittest.main()

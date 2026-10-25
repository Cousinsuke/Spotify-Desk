"""Offline checks for the additive multi-dashboard browser preview."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DashboardPreviewTests(unittest.TestCase):
    def test_device_template_loads_dashboard_after_existing_player(self):
        html = (ROOT / "templates/device.html").read_text(encoding="utf-8")
        self.assertIn('/static/desk-dashboard.css?v=0.2', html)
        self.assertIn('/static/glucose-history.js?v=0.2', html)
        self.assertIn('/static/desk-dashboard.js?v=0.2', html)
        self.assertLess(html.index('/static/device.js?v=5.2'),
                        html.index('/static/desk-dashboard.js?v=0.2'))
        for legacy_id in ('modeSpotify', 'modePC', 'track', 'artist', 'cover',
                          'back', 'play', 'next', 'volume', 'pairOverlay'):
            self.assertIn('id="' + legacy_id + '"', html)

    def test_preview_pages_and_weather_are_present(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        for name in ('home', 'spotify', 'weather', 'glucose'):
            self.assertIn("['" + name + "',", js)
        self.assertIn('geocoding-api.open-meteo.com', js)
        self.assertIn('api.open-meteo.com/v1/forecast', js)
        self.assertIn('desk_weather_city_v1', js)
        self.assertIn('data-desk-page="spotify"', css)
        self.assertIn('desk-panel[hidden]', css)

    def test_glucose_only_uses_clearly_labeled_sample_values(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        self.assertIn('SAMPLE DATA', js)
        self.assertIn('HISTORY · NOT LIVE', js)
        self.assertIn('file.text()', js)
        self.assertIn("location.hostname === '127.0.0.1'", js)
        self.assertNotIn('fetch(file', js)
        self.assertIn('NOT FOR TREATMENT', js)
        self.assertIn('No live glucose integration configured', js)
        self.assertIn('Current glucose is unavailable.', js)
        self.assertIn('6.3 + 1.05 * Math.sin', js)
        self.assertNotIn('https://api.libreview', js.lower())
        self.assertNotIn('librelinkup.com', js.lower())

    def test_browser_script_syntax(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node.js not installed; check JS in browser')
        result = subprocess.run(
            [node, '--check', str(ROOT / 'static/desk-dashboard.js')],
            capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_historical_parser(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node.js not installed')
        result = subprocess.run(
            [node, str(ROOT / 'tests' / 'check_glucose_history.cjs')],
            capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()

"""Offline checks for the additive multi-dashboard browser preview."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DashboardPreviewTests(unittest.TestCase):
    def test_device_template_loads_dashboard_after_existing_player(self):
        html = (ROOT / "templates/device.html").read_text(encoding="utf-8")
        self.assertIn('/static/desk-dashboard.css?v=1.1', html)
        self.assertIn('/static/glucose-history.js?v=0.2', html)
        self.assertIn('/static/glucose-chart.js?v=0.8', html)
        self.assertIn('/static/desk-dashboard.js?v=1.1', html)
        self.assertLess(html.index('/static/device.js?v=5.2'),
                        html.index('/static/desk-dashboard.js?v=1.1'))
        for legacy_id in ('modeSpotify', 'modePC', 'track', 'artist', 'cover',
                          'back', 'play', 'next', 'volume', 'pairOverlay'):
            self.assertIn('id="' + legacy_id + '"', html)

    def test_preview_pages_and_weather_are_present(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        for name in ('home', 'spotify', 'weather', 'glucose'):
            self.assertIn("['" + name + "',", js)
        self.assertIn('api.open-meteo.com/v1/forecast', js)
        self.assertIn("name: 'Bournemouth'", js)
        self.assertIn("latitude: 50.72098, longitude: -1.87669", js)
        self.assertIn('&forecast_days=3&timezone=Europe%2FLondon', js)
        self.assertIn('&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max', js)
        self.assertNotIn('geocoding-api.open-meteo.com', js)
        self.assertNotIn('desk_weather_city_v1', js)
        self.assertIn('data-desk-page="spotify"', css)
        self.assertIn('desk-panel[hidden]', css)

    def test_weather_fixed_bournemouth_daily_cards(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        self.assertIn('id="deskDaily"', js)
        self.assertIn('3-DAY FORECAST', js)
        self.assertIn('Math.min(3, dates.length)', js)
        self.assertIn("day.textContent = i === 0 ? 'Today' : i === 1 ? 'Tomorrow'", js)
        self.assertIn("timeZone:'Europe/London'", js)
        for field in ('weather_code', 'temperature_2m_max',
                      'temperature_2m_min', 'precipitation_probability_max'):
            self.assertIn('daily.' + field, js)
        self.assertIn('desk-day-temperatures', js)
        self.assertIn('desk-day-rain', js)
        self.assertIn('.screen .desk-days{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))', css)
        self.assertNotIn('desk-weather-search', css)
        self.assertNotIn('desk-hourly', css)
        for old_element in ('deskCity', 'deskWeatherForm', 'deskHourly', 'NEXT HOURS'):
            self.assertNotIn(old_element, js)
        self.assertIn('deskWeatherValue', js)
        self.assertIn('deskWeatherSub', js)
        self.assertIn("weatherInFlight", js)
        self.assertIn('15 * 60 * 1000', js)

    def test_weather_daily_cards_offline_fixture(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node.js not installed')
        result = subprocess.run(
            [node, str(ROOT / 'tests' / 'check_weather_daily.cjs')],
            capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_home_weather_icon_and_glucose_trend_and_footer_fit(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        self.assertIn('id="deskHomeWeatherIcon"', js)
        self.assertIn("setText('deskHomeWeatherIcon', icon)", js)
        self.assertIn('id="deskHomeGlucoseArrow"', js)
        self.assertIn('function updateHomeGlucose(status, latest, ageSeconds)', js)
        self.assertIn("const trend = TREND_SYMBOLS[latest.direction] || ''", js)
        self.assertIn("updateHomeGlucose('live', data.latest, data.age_seconds)", js)
        self.assertIn("updateHomeGlucose(data.status, data.latest, data.age_seconds)", js)
        self.assertNotIn("data.latest.mmol.toFixed(1) + ' mmol/L'", js)
        self.assertIn('.screen .desk-home-weather-symbol', css)
        self.assertIn('.screen .desk-home-glucose-arrow[hidden]{display:none}', css)
        self.assertIn('.screen #desk-weather .desk-weather-note', css)
        self.assertIn('Every 15 min', js)

    def test_home_glucose_unit_and_stale_safety_offline(self):
        node = shutil.which('node')
        if not node:
            self.skipTest('Node.js not installed')
        result = subprocess.run(
            [node, str(ROOT / 'tests' / 'check_home_glucose.cjs')],
            capture_output=True, text=True, timeout=15, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

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

    def test_minimal_glucose_screen_keeps_live_safety_and_chart_controls(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        self.assertIn('class="desk-glucose-readout"', js)
        self.assertIn('class="desk-glucose-trend"', js)
        self.assertIn('glucoseNumber.textContent = data.latest.mmol.toFixed(1)', js)
        self.assertIn('glucoseTrend.textContent = TREND_SYMBOLS[data.latest.direction]', js)
        self.assertIn("glucosePanel.dataset.feedStatus = 'live'", js)
        self.assertIn("glucoseBadge.textContent = data.status === 'stale' ? 'STALE' : 'OFFLINE'", js)
        self.assertIn("Never show a demo line as live data", js)
        self.assertIn('NOT FOR TREATMENT', js)
        self.assertIn('Use the Libre app for decisions and alarms', js)
        self.assertIn("['home', 'Home']", js)
        for hours in ('3','6','12'):
            self.assertIn('data-hours="' + hours + '"', js)
        self.assertIn('#desk-glucose[data-feed-status="live"]', css)
        self.assertIn('#desk-glucose[data-feed-status="offline"]', css)
        self.assertIn('#desk-glucose[hidden]{display:none}', css)

    def test_libre_style_glucose_chart_and_glucose_only_view_switch(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        html = (ROOT / "templates/device.html").read_text(encoding="utf-8")
        self.assertIn("setGlucoseView(mode)", js)
        for layout in ("live", "graph", "both"):
            self.assertIn("['" + layout + "',", js)
            self.assertIn('data-glucose-view="' + layout + '"', css)
        for hours in ("1", "3", "6", "12", "24"):
            self.assertIn('data-hours="' + hours + '"', js)
        self.assertIn('DeskGlucoseChart', js)
        self.assertIn("chartScale === 'auto' ? 'fixed' : 'auto'", js)
        self.assertIn('.surface[data-desk-page="glucose"] .topbar .mode-switch{display:none}', css)
        self.assertIn('.surface[data-desk-page="glucose"] .topbar .desk-glucose-modes{display:flex}', css)
        self.assertIn('id="modeSpotify"', html)
        self.assertIn('id="modePC"', html)
        self.assertIn('NOT FOR TREATMENT', js)
        renderer = (ROOT / "static/glucose-chart.js").read_text(encoding="utf-8")
        self.assertIn('const TARGET_LOW = 4;', renderer)
        self.assertIn('const TARGET_HIGH = 7;', renderer)
        self.assertIn("dateClock.format(new Date(t))", renderer)
        self.assertIn("segments", renderer)
        self.assertIn("GAP_MS", renderer)

    def test_spotify_inspired_both_layout_is_isolated(self):
        js = (ROOT / "static/desk-dashboard.js").read_text(encoding="utf-8")
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        html = (ROOT / "templates/device.html").read_text(encoding="utf-8")
        self.assertIn('<div class="desk-glucose-layout">', js)
        self.assertIn('<div class="desk-glucose-chart-column">', js)
        self.assertIn('data-glucose-view="both"] .desk-glucose-layout', css)
        self.assertIn('grid-template-columns:minmax(0, 218px) minmax(0,1fr)', css)
        self.assertIn('aspect-ratio:1/1', css)
        self.assertIn('max-height:240px', css)
        self.assertIn('data-glucose-view="live"] .desk-glucose-chart-column', css)
        self.assertIn('data-glucose-view="graph"] .desk-glucose-info{display:none}', css)
        self.assertIn('ResizeObserver', js)
        self.assertIn("chart.width + ' 196'", js)
        self.assertIn('width: svg.getBoundingClientRect().width >= 320', js)
        for page in ('home','spotify','weather','glucose'):
            self.assertIn("['" + page + "',", js)
        for old_element in ('modeSpotify','modePC','back','play','next','volume'):
            self.assertIn('id="' + old_element + '"', html)
        self.assertIn('NOT FOR TREATMENT', js)
        self.assertIn("glucoseBadge.textContent = 'LIVE'", js)
        self.assertIn("glucoseBadge.textContent = data.status === 'stale' ? 'STALE' : 'OFFLINE'", js)

    def test_both_graph_header_no_longer_pushes_graph_down(self):
        css = (ROOT / "static/desk-dashboard.css").read_text(encoding="utf-8")
        start = css.index("/* v0.9 — Align the BOTH graph border")
        alignment = css[start:]
        self.assertIn('data-glucose-view="both"] .desk-glucose-chart-column', alignment)
        self.assertIn('position:relative;', alignment)
        self.assertIn('height:calc(100% - 22px);', alignment)
        self.assertIn('bottom:calc(100% + 7px);', alignment)
        self.assertIn('position:absolute;', alignment)
        self.assertIn('height:100%;', alignment)
        self.assertIn('@media(max-width:610px)', alignment)
        self.assertIn('position:static;', alignment)
        # The existing views and playback selectors must remain unchanged.
        self.assertIn('data-glucose-view="live"] .desk-glucose-chart-column', css)
        self.assertIn('data-glucose-view="graph"] .desk-glucose-info{display:none}', css)
        self.assertIn('.surface[data-desk-page="glucose"] .topbar .mode-switch{display:none}', css)

    def test_libre_style_chart_parser(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable")
        for js_path in (ROOT / "static" / "glucose-chart.js",
                        ROOT / "static" / "desk-dashboard.js"):
            result = subprocess.run([node, "--check", str(js_path)],
                capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([node, str(ROOT / "tests" / "check_glucose_chart.cjs")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)

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

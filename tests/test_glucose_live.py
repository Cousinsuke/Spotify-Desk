"""Offline checks for live Nightscout-compatible glucose source. No network calls."""
import hashlib
import time
import unittest
from unittest.mock import Mock

from glucose_live import LiveGlucose, normalise_entries, validate_url, POLL_SECONDS
from device_bridge import EXPOSED


NOW = 1_800_000_000.0
HOST = 'https://demo.ns.gluroo.com'
SHA = hashlib.sha1(b'unit-test-secret').hexdigest()


def entry(seconds_ago, sgv=110, direction='Flat'):
    return {'type': 'sgv', 'date': int((NOW-seconds_ago) * 1000),
            'sgv': sgv, 'direction': direction}


def response(items, code=200):
    return Mock(status_code=code, content=b'[]',
                json=Mock(return_value=items))


class LiveGlucoseTests(unittest.TestCase):
    def test_https_config_and_no_lan_endpoint(self):
        self.assertEqual(validate_url(HOST), HOST)
        self.assertNotIn('/api/device/glucose', EXPOSED)
        for url in ('http://demo.ns.gluroo.com', 'https://localhost',
                    'https://127.0.0.1', 'https://u:p@example.com',
                    'https://example.com/api/v1', 'https://example.com/?token=abc',
                    'https://example.com:8080', 'https://example.com#secret'):
            with self.subTest(url=url):
                with self.assertRaises(ValueError): validate_url(url)

    def test_disabled_and_misconfigured(self):
        self.assertEqual(LiveGlucose().state()['status'], 'not_configured')
        self.assertEqual(LiveGlucose(HOST, 'bad').state()['status'], 'configuration_error')

    def test_parses_mgdl_to_mmol_sorts_and_skips_bad(self):
        data = normalise_entries([entry(60,108), entry(180,90,'SingleDown'),
                                  entry(120,5000), entry(60,108), {'type':'mbg','sgv':100,'date':int(NOW*1000)},
                                  {'sgv':105,'date':int((NOW+400)*1000)}], NOW)
        self.assertEqual(len(data), 2)
        self.assertAlmostEqual(data[-1]['mmol'], 5.99, places=1)
        self.assertEqual(data[0]['direction'], 'SingleDown')

    def test_refresh_caches_and_reports_stale(self):
        clock=[NOW]
        get=Mock(return_value=response([entry(90), entry(150,104,'SingleDown')]))
        svc=LiveGlucose(HOST,SHA,http_get=get,clock=lambda: clock[0])
        state=svc.state()
        self.assertEqual(state['status'],'live')
        self.assertEqual(state['latest']['direction'],'Flat')
        self.assertEqual(len(state['readings']),2)
        self.assertEqual(get.call_count,1)
        self.assertEqual(get.call_args.kwargs['allow_redirects'],False)
        self.assertNotIn('token', get.call_args.kwargs['params'])
        self.assertEqual(get.call_args.kwargs['headers']['api-secret'],SHA)
        clock[0]+=30
        self.assertEqual(svc.state()['status'],'live')
        self.assertEqual(get.call_count,1)
        clock[0]+=POLL_SECONDS
        self.assertEqual(svc.state()['status'],'live')
        self.assertEqual(get.call_count,2)
        clock[0]+=700
        self.assertEqual(svc.state()['status'],'stale')

    def test_upstream_error_or_no_readings_not_live(self):
        failed=LiveGlucose(HOST,SHA,http_get=lambda *a,**kw: response([],401),clock=lambda:NOW)
        self.assertEqual(failed.state()['status'],'unavailable')
        too_old=LiveGlucose(HOST,SHA,
          http_get=lambda *a,**kw: response([entry(1200)]),
          clock=lambda:NOW)
        self.assertEqual(too_old.state()['status'],'stale')
        server_down=Mock(side_effect=Exception('private test source'))
        # A request failure from requests is caught without exposing credentials.
        import requests
        server_down.side_effect=requests.ConnectionError('unavailable')
        svc=LiveGlucose(HOST,SHA,http_get=server_down,clock=lambda:NOW)
        self.assertEqual(svc.state()['status'],'unavailable')

    def test_rate_limit_backoff(self):
        clock=[NOW]
        svc=LiveGlucose(HOST,SHA, http_get=lambda *a,**kw:response([],429),
                        clock=lambda:clock[0])
        state=svc.state()
        self.assertEqual(state['status'],'unavailable')
        self.assertGreater(state['retry_seconds'],POLL_SECONDS)


if __name__=='__main__':
    unittest.main()

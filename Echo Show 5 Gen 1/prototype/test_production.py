"""Production startup contract; no real network or account access."""
import unittest
from unittest.mock import patch
import live_server as s

class ProductionTests(unittest.TestCase):
    def test_production_restores_token_and_binds_loopback(self):
        fake={"refresh_token":"synthetic","expires_at":0}
        with patch.object(s,"CLIENT","syntheticClient1234"), patch.object(s,"token",None), patch.object(s,"read_refresh",return_value=fake), patch("waitress.serve") as serve:
            s.run_server(production=True)
            self.assertEqual(s.token,fake)
            self.assertEqual(serve.call_args.kwargs["host"],"127.0.0.1")
            self.assertEqual(serve.call_args.kwargs["port"],8765)
            self.assertEqual(serve.call_args.kwargs["threads"],1)
            self.assertTrue(serve.call_args.kwargs["clear_untrusted_proxy_headers"])
            self.assertFalse(serve.call_args.kwargs["expose_tracebacks"])
    def test_preview_still_single_threaded(self):
        with patch.object(s,"CLIENT","syntheticClient1234"), patch.object(s,"token",None), patch.object(s,"read_refresh",return_value=None), patch.object(s.app,"run") as run:
            s.run_server()
            self.assertEqual(run.call_args.kwargs["host"],"127.0.0.1")
            self.assertFalse(run.call_args.kwargs["threaded"])
    def test_invalid_client_never_serves(self):
        with patch.object(s,"CLIENT",""), patch.object(s.app,"run") as run:
            with self.assertRaises(SystemExit):s.run_server()
            run.assert_not_called()

if __name__=="__main__":unittest.main()

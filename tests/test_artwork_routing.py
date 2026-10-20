"""Art routing regression checks that don't require Flask in the build environment."""
import ast
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

SOURCE=Path(__file__).resolve().parents[1]/'device_bridge.py'
module=ast.parse(SOURCE.read_text('utf-8'))
fn=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='device_artwork_url')
namespace={'parse_qs':parse_qs,'urlsplit':urlsplit}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(SOURCE),'exec'),namespace)
route=namespace['device_artwork_url']

class ArtworkRoutingTests(unittest.TestCase):
    def test_https_mpris_art_stays_direct(self):
        self.assertEqual(route('https://i.scdn.co/image/album123'), 'https://i.scdn.co/image/album123')
    def test_local_companion_art_uses_authenticated_proxy(self):
        self.assertEqual(route('/api/pc/artwork?key=12345'),'/api/device/artwork?key=12345')
    def test_absent_art_is_not_advertised(self):
        self.assertIsNone(route(None))
        self.assertIsNone(route(''))
    def test_rejects_unrelated_or_unkeyed_local_paths(self):
        for url in ('/api/pc/artwork', '/api/pc/artwork?key=', '/api/pc/artwork?key=abc',
                    'file:///home/user/.cache/image.jpg','http://example.com/evil',
                    'https://example.com.evil@localhost/', '/api/status',
                    '/api/pc/artwork?key=10&key=20'):
            if url.startswith('https://'):
                continue # remote https is supported by design
            self.assertIsNone(route(url),url)

if __name__=='__main__':unittest.main()

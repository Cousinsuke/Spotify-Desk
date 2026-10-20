"""Pairing logic tests that run without Flask dependencies."""
import ast
import ipaddress
import json
import os
import secrets
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'device_bridge.py'
tree = ast.parse(SOURCE.read_text('utf-8'))
node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PairingStore')
ns = {'Path': Path, 'json':json, 'os':os, 'secrets':secrets, 'threading':threading, 'time':time}
exec(compile(ast.Module(body=[node], type_ignores=[]),str(SOURCE),'exec'),ns)
PairingStore=ns['PairingStore']

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'devices.json';self.now=[1000.0]
        self.store=PairingStore(self.path,now=lambda:self.now[0])

    def test_code_is_six_digits(self):
        self.assertEqual(len(self.store.code),6)
        self.assertTrue(self.store.code.isascii() and self.store.code.isdigit())

    def test_one_time_pair_and_save_token(self):
        code=self.store.code
        token,err,status=self.store.pairing(code,'My Simulator','192.168.1.2')
        self.assertEqual(status,200)
        self.assertEqual(len(token),64)
        self.assertEqual(self.store.get('Bearer '+token)[1]['mode'],'pc')
        self.assertEqual(self.store.pairing(code,'Other','192.168.1.2')[2],403)
        self.assertEqual(PairingStore(self.path).get('Bearer '+token)[1]['name'],'My Simulator')

    def test_expired_pairing(self):
        code=self.store.code;self.now[0]+=601
        self.assertEqual(self.store.pairing(code,'Device','1.1.1.1')[2],403)

    def test_five_bad_attempts_lockout(self):
        for i in range(5):self.assertEqual(self.store.pairing('wrong','Device','1.1.1.1')[2],403)
        self.assertEqual(self.store.pairing(self.store.code,'Device','1.1.1.1')[2],429)

    def test_bearer_required(self):
        token,_,_=self.store.pairing(self.store.code,'Device','1.1.1.1')
        self.assertIsNone(self.store.get(token))
        self.assertIsNone(self.store.get('Bearer invalid'))
        self.assertIsNotNone(self.store.get('Bearer '+token))

    def test_device_mode_and_revoke(self):
        token,_,_=self.store.pairing(self.store.code,'Device','1.1.1.1')
        self.assertFalse(self.store.mode(token,'invalid'))
        self.assertTrue(self.store.mode(token,'spotify'))
        self.assertEqual(self.store.get('Bearer '+token)[1]['mode'],'spotify')
        self.store.clear()
        self.assertIsNone(self.store.get('Bearer '+token))

    def test_device_limit(self):
        for n in range(8):
            self.store.rotate()
            self.assertEqual(self.store.pairing(self.store.code,str(n),f'10.0.0.{n}')[2],200)
        self.store.rotate()
        self.assertEqual(self.store.pairing(self.store.code,'9','10.0.0.9')[2],409)

    def test_posix_file_permissions(self):
        self.store.pairing(self.store.code,'Test','1.1.1.1')
        if os.name=='posix':self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

if __name__=='__main__':unittest.main()

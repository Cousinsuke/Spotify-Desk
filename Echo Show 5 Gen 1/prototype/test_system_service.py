"""Offline fixture tests, no network or credentials."""
import unittest
from unittest.mock import patch
import system_service as s

class SystemTests(unittest.TestCase):
    def test_cpu(self):
        a=s.cpu_ticks("cpu 100 20 30 800 50 5 6 7 99 99")
        b=s.cpu_ticks("cpu 120 20 30 860 60 5 6 7 99 99")
        self.assertEqual(s.cpu_percent(a,b),22.2)
        self.assertIsNone(s.cpu_percent(a,a))
        self.assertIsNone(s.cpu_ticks("invalid"))
    def test_memory(self):
        self.assertEqual(s.memory_stats("MemTotal: 1000 kB\nMemAvailable: 400 kB"),{"used":614400,"total":1024000,"percent":60.0})
        self.assertIsNone(s.memory_stats("MemTotal: 0 kB\nMemAvailable: 0 kB"))
        self.assertIsNone(s.memory_stats(""))
    def test_percent(self):
        self.assertEqual(s.percent(110,100),100)
        self.assertEqual(s.percent(-1,100),0)
        self.assertIsNone(s.percent(1,0))
    def test_missing_temperature(self):
        with patch.object(s.Path,"glob",return_value=[]):
            self.assertIsNone(s.temperature())

if __name__=="__main__":unittest.main()

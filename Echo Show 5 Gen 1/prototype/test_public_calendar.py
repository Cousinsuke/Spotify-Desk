"""Offline public calendar fixtures; no network or credentials."""
import unittest
from datetime import date
from unittest.mock import patch
import public_calendar_service as s

class PublicTests(unittest.TestCase):
    def test_observances(self):
        rows=s.observances(2026)
        self.assertIn(("2026-11-05","Guy Fawkes Night"),[(r["date"],r["title"]) for r in rows])
        self.assertIn(("2026-11-08","Remembrance Sunday"),[(r["date"],r["title"]) for r in rows])
        self.assertEqual(s.easter(2026),date(2026,4,5))
    def test_holidays(self):
        self.assertEqual(s.holiday_rows({"england-and-wales":{"events":[{"date":"2026-12-25","title":"Christmas Day"}]}})[0]["kind"],"holiday")
    def test_f1(self):
        rows=s.f1_rows({"races":[{"name":"British","location":"Silverstone","sessions":{"gp":"2026-07-05T14:00:00Z","fp1":"2026-07-03T11:30:00Z"}}]})
        self.assertEqual(rows[0]["time"],"15:00")
        self.assertEqual(rows[0]["location"],"Silverstone")
        self.assertEqual(rows[0]["title"],"British Grand Prix · Race")
    def test_partial_sources(self):
        c=s.PublicCalendar()
        with patch.object(c,"source",side_effect=[([],"error"),([],"error")]):
            data=c.snapshot("2026-11-01")
        self.assertEqual(data["status"],"partial")
        self.assertTrue(any(r["title"]=="Guy Fawkes Night" for r in data["events"]))
    def test_refresh_failure_retains_rows(self):
        c=s.PublicCalendar();c.cache[2026]={"attempt":0,"ok":True,"rows":[{"title":"Synthetic"}]}
        with patch.object(s,"get_json",side_effect=ValueError):c.refresh(2026)
        self.assertEqual(c.cache[2026]["rows"],[{"title":"Synthetic"}])
        self.assertFalse(c.cache[2026]["ok"])

if __name__=="__main__":unittest.main()

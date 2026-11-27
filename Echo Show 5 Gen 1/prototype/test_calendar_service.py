"""Offline synthetic checks; never use the real .env or contact Apple."""
import unittest
from datetime import date, datetime, timezone
from unittest.mock import patch
import calendar_service as s

class CalendarTests(unittest.TestCase):
    def test_safe_destinations(self):
        self.assertEqual(s.safe_url(s.BASE,"/test/"),s.BASE+"test/")
        self.assertEqual(s.safe_url(s.BASE,"https://p01-caldav.icloud.com/test/"),"https://p01-caldav.icloud.com/test/")
        for url in ["http://caldav.icloud.com/","https://evil.invalid/","https://caldav.icloud.com.evil.invalid/","https://name:pass@caldav.icloud.com/","https://caldav.icloud.com:8080/"]:
            with self.subTest(url=url),self.assertRaises(s.CalendarError):
                s.safe_url(s.BASE,url)
    def test_merge_successful_propstats(self):
        root=s.ET.fromstring('<d:multistatus xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:response><d:href>/synthetic/</d:href><d:propstat><d:prop><d:resourcetype><d:collection/><c:calendar/></d:resourcetype></d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propstat><d:propstat><d:prop><c:supported-calendar-component-set><c:comp name="VTODO"/></c:supported-calendar-component-set></d:prop><d:status>HTTP/2 200</d:status></d:propstat><d:propstat><d:prop><d:displayname/></d:prop><d:status>HTTP/1.1 404 Not Found</d:status></d:propstat></d:response></d:multistatus>')
        props=list(s.Client.props(root))
        self.assertEqual(len(props),1)
        self.assertIsNotNone(props[0][1].find(s.DAV+"resourcetype/"+s.CAL+"calendar"))
        self.assertEqual(props[0][1].find(s.CAL+"supported-calendar-component-set")[0].get("name"),"VTODO")
        self.assertIsNone(props[0][1].find(s.DAV+"displayname"))
    def test_no_calendars_not_connected(self):
        with patch.object(s,"fetch_month",return_value=([],{"eventCalendars":0})):
            service=s.Service()
            service.refresh("2026-11-01")
            result=service.cache["2026-11-01"][1]
            self.assertEqual(result["status"],"empty")
            self.assertEqual(result["calendarCount"],0)
    def test_range(self):
        self.assertEqual(s.month_bounds("2026-11-01"),(date(2026,10,26),date(2026,12,21)))
        with self.assertRaises(ValueError):s.month_bounds("2026-11-02")
    def test_unconfigured(self):
        with patch.dict("os.environ",{"DESK_ICLOUD_USERNAME":"","DESK_ICLOUD_APP_PASSWORD":""}):
            self.assertEqual(s.Service().snapshot("2026-11-01")["status"],"unconfigured")
    def test_all_day_multiday(self):
        from icalendar import Event
        e=Event();e.add("summary","Synthetic");e.add("dtstart",date(2026,11,26));e.add("dtend",date(2026,11,28))
        rows=s.event_rows(e,date(2026,11,1),date(2026,12,1))
        self.assertEqual([x["date"] for x in rows],["2026-11-26","2026-11-27"])
        self.assertTrue(all(x["time"]=="All day" for x in rows))
    def test_timed_timezone(self):
        from icalendar import Event
        e=Event();e.add("summary","Synthetic");e.add("dtstart",datetime(2026,7,3,10,tzinfo=timezone.utc));e.add("dtend",datetime(2026,7,3,11,tzinfo=timezone.utc))
        self.assertEqual(s.event_rows(e,date(2026,7,1),date(2026,8,1))[0]["time"],"11:00 – 12:00")
    def test_cancelled(self):
        from icalendar import Event
        e=Event();e.add("dtstart",date(2026,11,26));e.add("status","CANCELLED")
        self.assertEqual(s.event_rows(e,date(2026,11,1),date(2026,12,1)),[])
    def test_recurrence(self):
        from icalendar import Calendar,Event
        import recurring_ical_events
        cal=Calendar();e=Event();e.add("uid","synthetic");e.add("summary","Synthetic");e.add("dtstart",date(2026,11,2));e.add("rrule",{"freq":"weekly","count":3});cal.add_component(e)
        rows=[row for event in recurring_ical_events.of(cal).between(s.local_dt(date(2026,11,1)),s.local_dt(date(2026,12,1))) for row in s.event_rows(event,date(2026,11,1),date(2026,12,1))]
        self.assertEqual([x["date"] for x in rows],["2026-11-02","2026-11-09","2026-11-16"])

if __name__=="__main__":unittest.main()

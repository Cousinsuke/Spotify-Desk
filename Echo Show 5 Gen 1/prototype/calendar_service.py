"""Private read-only iCloud CalDAV month cache. No event or credential logging."""
import os
import re
import time
import threading
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree as ET
import requests

TZ = ZoneInfo("Europe/London")
DAV = "{DAV:}"
CAL = "{urn:ietf:params:xml:ns:caldav}"
CS = "{http://calendarserver.org/ns/}"
BASE = "https://caldav.icloud.com/"
LIMIT = 4 * 1024 * 1024

class CalendarError(Exception):
    pass

def safe_url(base, href):
    url = urljoin(base, href)
    p = urlsplit(url)
    if (p.scheme != "https" or not re.fullmatch(r"(?:p[0-9]+-)?caldav\.icloud\.com", p.hostname or "")
            or p.username or p.password or p.port not in (None, 443) or p.fragment):
        raise CalendarError("Unexpected iCloud calendar address.")
    return url

def month_bounds(month):
    if not re.fullmatch(r"20[0-9]{2}-(?:0[1-9]|1[0-2])-01", month or ""):
        raise ValueError("Invalid month")
    first = date.fromisoformat(month)
    start = first - timedelta(days=first.weekday())
    return start, start + timedelta(days=56)

def local_dt(value):
    if isinstance(value, datetime):
        return value.astimezone(TZ) if value.tzinfo else value.replace(tzinfo=TZ)
    return datetime.combine(value, datetime.min.time(), TZ)

def event_rows(event, start, end):
    if str(event.get("STATUS", "")).upper() == "CANCELLED":
        return []
    if "DTSTART" not in event:
        return []
    a = event.decoded("DTSTART")
    all_day = not isinstance(a, datetime)
    b = event.decoded("DTEND") if "DTEND" in event else a + (event.decoded("DURATION") if "DURATION" in event else timedelta(days=1 if all_day else 0))
    begin, finish = local_dt(a), local_dt(b)
    title = str(event.get("SUMMARY", "Untitled event")).strip()[:200] or "Untitled event"
    if finish < begin:
        finish = begin
    if begin >= local_dt(end) or (finish <= local_dt(start) and begin < local_dt(start)):
        return []
    last = (finish - timedelta(microseconds=1)).date() if finish > begin else begin.date()
    day = max(start, begin.date())
    rows = []
    while day <= last and day < end:
        if all_day:
            label = "All day"
        else:
            left = begin.strftime("%H:%M") if day == begin.date() else "00:00"
            right = finish.strftime("%H:%M") if day == finish.date() else "24:00"
            label = left if begin == finish else left + " – " + right
        rows.append({"date":day.isoformat(), "title":title, "time":label, "sort":"" if all_day else left})
        day += timedelta(days=1)
    return rows

class Client:
    def __init__(self, username, password):
        self.session = requests.Session()
        self.session.trust_env = False
        self.session.auth = (username, password)
        self.deadline = time.monotonic() + 90
        self.counts = {"collections":0,"eventCalendars":0,"subscriptions":0,"reportResources":0,"calendarData":0,"occurrences":0}

    def xml(self, method, url, body, depth):
        url = safe_url(BASE, url)
        for _ in range(5):
            if time.monotonic() > self.deadline:
                raise CalendarError("iCloud request timed out.")
            with self.session.request(method, url, data=body.encode(), headers={"Depth":str(depth), "Content-Type":"application/xml; charset=utf-8"}, timeout=(5, 12), allow_redirects=False, stream=True) as response:
                if response.status_code in (301, 302, 307, 308):
                    url = safe_url(url, response.headers.get("Location", ""))
                    continue
                if response.status_code in (401, 403):
                    raise CalendarError("iCloud access denied. Check your Apple Account and app-specific password.")
                if response.status_code != 207:
                    raise CalendarError("iCloud returned HTTP " + str(response.status_code) + ".")
                chunks = bytearray()
                for chunk in response.iter_content(65536):
                    if time.monotonic() > self.deadline or len(chunks) + len(chunk) > LIMIT:
                        raise CalendarError("iCloud response exceeded the preview limit.")
                    chunks.extend(chunk)
                if b"<!DOCTYPE" in chunks.upper() or b"<!ENTITY" in chunks.upper():
                    raise CalendarError("Unexpected iCloud XML response.")
                return url, ET.fromstring(chunks)
        raise CalendarError("Too many iCloud redirects.")

    def propfind(self, url, prop, depth=0):
        return self.xml("PROPFIND", url, '<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop>'+prop+'</d:prop></d:propfind>', depth)

    @staticmethod
    def props(root):
        for response in root.findall(DAV+"response"):
            href = response.findtext(DAV+"href")
            merged = ET.Element(DAV+"prop")
            for ps in response.findall(DAV+"propstat"):
                status = (ps.findtext(DAV+"status") or "").split()
                if len(status) >= 2 and status[1] == "200":
                    prop = ps.find(DAV+"prop")
                    if prop is not None:
                        merged.extend(list(prop))
            if len(merged):
                yield href, merged

    def calendars(self):
        url, root = self.propfind(BASE, "<d:current-user-principal/>")
        principal = next((p.findtext(DAV+"current-user-principal/"+DAV+"href") for _,p in self.props(root) if p.find(DAV+"current-user-principal/"+DAV+"href") is not None), None)
        if not principal:
            raise CalendarError("Could not discover iCloud account calendars.")
        url, root = self.propfind(safe_url(url, principal), "<c:calendar-home-set/>")
        home = next((p.findtext(CAL+"calendar-home-set/"+DAV+"href") for _,p in self.props(root) if p.find(CAL+"calendar-home-set/"+DAV+"href") is not None), None)
        if not home:
            raise CalendarError("Could not discover iCloud calendar home.")
        url, root = self.propfind(safe_url(url, home), "<d:resourcetype/><c:supported-calendar-component-set/>", 1)
        found = []
        for href,p in self.props(root):
            if not href:
                continue
            kind = p.find(DAV+"resourcetype")
            if kind is None:
                continue
            if kind.find(DAV+"collection") is not None:
                self.counts["collections"] += 1
            if kind.find(CS+"subscribed") is not None:
                self.counts["subscriptions"] += 1
            if kind.find(CAL+"calendar") is None:
                continue
            components = p.find(CAL+"supported-calendar-component-set")
            if components is not None and not any(c.get("name")=="VEVENT" for c in components):
                continue
            candidate = safe_url(url, href)
            if candidate not in found:
                found.append(candidate)
        if len(found) > 30:
            raise CalendarError("Too many calendars for this preview.")
        self.counts["eventCalendars"] = len(found)
        return found

    def events(self, url, start, end):
        from icalendar import Calendar
        import recurring_ical_events
        def stamp(d):
            return local_dt(d).astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        body = ('<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">'
                '<d:prop><c:calendar-data/></d:prop><c:filter><c:comp-filter name="VCALENDAR">'
                '<c:comp-filter name="VEVENT"><c:time-range start="'+stamp(start)+'" end="'+stamp(end)+'"/>'
                '</c:comp-filter></c:comp-filter></c:filter></c:calendar-query>')
        _,root = self.xml("REPORT", url, body, 1)
        rows = []
        resources = root.findall(DAV+"response")
        self.counts["reportResources"] += len(resources)
        for resource in resources:
            statuses = [x.findtext(DAV+"status") or "" for x in resource.findall(DAV+"propstat")]
            if resource.find(DAV+"status") is not None:
                statuses.append(resource.findtext(DAV+"status") or "")
            if any(len(st.split()) >= 2 and st.split()[1] in ("401","403","500","503") for st in statuses):
                raise CalendarError("iCloud returned an error for a calendar resource.")
        for _,prop in self.props(root):
            data = prop.findtext(CAL+"calendar-data")
            if not data:
                continue
            self.counts["calendarData"] += 1
            calendar = Calendar.from_ical(data)
            for event in recurring_ical_events.of(calendar).between(local_dt(start), local_dt(end)):
                self.counts["occurrences"] += 1
                rows.extend(event_rows(event,start,end))
                if len(rows) > 2000 or time.monotonic() > self.deadline:
                    raise CalendarError("Calendar exceeds the preview limit.")
        return rows

def fetch_month(month, username, password):
    try:
        import icalendar
        import recurring_ical_events
    except ImportError:
        raise CalendarError("Install the Apple Calendar requirements, then restart.")
    start,end = month_bounds(month)
    client = Client(username,password)
    try:
        calendars = client.calendars()
        rows = []
        for url in calendars:
            rows.extend(client.events(url,start,end))
            if len(rows) > 2000:
                raise CalendarError("Calendar exceeds the preview limit.")
        rows.sort(key=lambda e:(e["date"],e["sort"],e["title"]))
        for row in rows:
            row.pop("sort",None)
        return rows,dict(client.counts)
    finally:
        client.session.close()

class Service:
    def __init__(self):
        self.username = os.environ.get("DESK_ICLOUD_USERNAME","")
        self.password = os.environ.get("DESK_ICLOUD_APP_PASSWORD","")
        self.lock = threading.Lock()
        self.cache = {}
        self.running = None

    def snapshot(self,month):
        month_bounds(month)
        if not self.username or not self.password:
            return {"status":"unconfigured","events":[],"message":"Apple credentials are not configured."}
        with self.lock:
            entry = self.cache.get(month)
            if (entry is None or time.monotonic()-entry[0] >= 300) and self.running is None:
                self.running = month
                threading.Thread(target=self.refresh,args=(month,),daemon=True).start()
            if entry:
                return {**entry[1], "status":"stale" if entry[1]["status"]=="fresh" and time.monotonic()-entry[0]>=300 else entry[1]["status"]}
            return {"status":"loading","events":[],"message":"Connecting to iCloud…"}

    def refresh(self,month):
        try:
            rows,counts = fetch_month(month,self.username,self.password)
            count = counts["eventCalendars"]
            result = {"status":"fresh" if count else "empty", "events":rows,"calendarCount":count,"counts":counts}
            if not count:
                result["message"] = "Signed in, but no readable iCloud event calendars were found. Check calendar sources on your iPhone."
            elif not rows:
                result["message"] = "No event dates returned in this date range. Check iCloud.com and calendar sources."
        except CalendarError as e:
            result = {"status":"error","events":[],"message":str(e)}
        except Exception:
            result = {"status":"error","events":[],"message":"Could not read iCloud Calendar. Check connection and try again."}
        with self.lock:
            self.cache[month] = (time.monotonic(),result)
            while len(self.cache)>3:
                self.cache.pop(next(iter(self.cache)))
            self.running = None

service = Service()

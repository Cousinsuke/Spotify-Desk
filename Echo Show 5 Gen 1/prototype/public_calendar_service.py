"""Public UK holidays and F1 calendar; no credentials or personal calendar access."""
import threading
import time
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
import requests
from calendar_service import month_bounds

TZ = ZoneInfo("Europe/London")
HOLIDAYS = "https://www.gov.uk/bank-holidays.json"
F1 = "https://raw.githubusercontent.com/sportstimes/f1/main/_db/f1/{year}.json"
SESSIONS = {"fp1":"Practice 1","fp2":"Practice 2","fp3":"Practice 3","qualifying":"Qualifying",
            "sprintQualifying":"Sprint qualifying","sprintShootout":"Sprint qualifying","sprint":"Sprint","gp":"Race"}
OBSERVANCES = [(1,25,"Burns Night"),(2,14,"Valentine’s Day"),(3,1,"St David’s Day"),(3,17,"St Patrick’s Day"),
               (4,23,"St George’s Day"),(10,31,"Halloween"),(11,5,"Guy Fawkes Night"),(11,11,"Remembrance Day"),
               (11,30,"St Andrew’s Day"),(12,24,"Christmas Eve"),(12,31,"New Year’s Eve")]

def row(day,title,kind,clock="All day",location=""):
    return {"date":day.isoformat(),"title":title,"time":clock,"kind":kind,"location":location}

def sunday(year, month, ordinal):
    first=date(year,month,1)
    return first+timedelta(days=(6-first.weekday())%7+7*(ordinal-1))

def easter(year):
    a=year%19; b,c=divmod(year,100); d,e=divmod(b,4)
    f=(b+8)//25; g=(b-f+1)//3; h=(19*a+b-d-g+15)%30
    i,k=divmod(c,4); l=(32+2*e+2*i-h-k)%7; m=(a+11*h+22*l)//451
    n=h+l-7*m+114
    return date(year,n//31,n%31+1)

def observances(year):
    fixed=[row(date(year,m,d),name,"observance") for m,d,name in OBSERVANCES]
    fixed.extend([row(easter(year),"Easter Sunday","observance"),
                  row(easter(year)-timedelta(days=21),"Mothering Sunday","observance"),
                  row(sunday(year,6,3),"Father’s Day","observance"),
                  row(sunday(year,11,2),"Remembrance Sunday","observance")])
    # Remembrance Sunday is the second Sunday in November.
    return fixed

def holiday_rows(data):
    events=data["england-and-wales"]["events"]
    return [row(date.fromisoformat(e["date"]),str(e["title"])[:200],"holiday") for e in events]

def f1_rows(data):
    result=[]
    for race in data["races"]:
        if race.get("cancelled") or race.get("canceled") or race.get("status") in ("cancelled","canceled"):
            continue
        name=str(race["name"])[:100]
        if not name.lower().endswith(("grand prix"," gp")):
            name+=" Grand Prix"
        location=str(race.get("location") or "")[:120]
        for key,stamp in race.get("sessions",{}).items():
            if key not in SESSIONS or not stamp:
                continue
            dt=datetime.fromisoformat(stamp.replace("Z","+00:00"))
            if dt.tzinfo is None:
                raise ValueError("Missing schedule timezone")
            dt=dt.astimezone(TZ)
            result.append(row(dt.date(),name+" · "+SESSIONS[key],"f1",dt.strftime("%H:%M"),location))
    return result

def get_json(url):
    # Fixed public endpoints only; never send Apple or other account credentials.
    with requests.Session() as session:
        session.trust_env=False
        with session.get(url,timeout=(5,12),allow_redirects=False,stream=True) as response:
            if response.status_code!=200:
                raise ValueError("Public calendar unavailable")
            data=bytearray()
            for chunk in response.iter_content(65536):
                data.extend(chunk)
                if len(data)>2*1024*1024:
                    raise ValueError("Public calendar response too large")
            import json
            return json.loads(data)

class PublicCalendar:
    def __init__(self):
        self.lock=threading.Lock()
        self.cache={}
        self.running=set()
        self.ttl=3600
        self.retry=300

    def source(self,key):
        now=time.monotonic()
        entry=self.cache.get(key)
        if (entry is None or now-entry["attempt"] >= (self.ttl if entry["ok"] else self.retry)) and key not in self.running and len(self.running)<3:
            self.running.add(key)
            threading.Thread(target=self.refresh,args=(key,),daemon=True).start()
        if entry is None:
            return [],"loading"
        if entry["ok"]:
            return entry["rows"],"fresh" if now-entry["attempt"]<self.ttl else "stale"
        return entry["rows"],"stale" if entry["rows"] else "error"

    def refresh(self,key):
        try:
            rows=holiday_rows(get_json(HOLIDAYS)) if key=="holidays" else f1_rows(get_json(F1.format(year=key)))
            ok=True
        except Exception:
            rows=None;ok=False
        with self.lock:
            prior=self.cache.get(key,{}).get("rows",[])
            self.cache[key]={"attempt":time.monotonic(),"ok":ok,"rows":rows if ok else prior}
            self.running.discard(key)
            while len(self.cache)>8:
                self.cache.pop(next(iter(self.cache)))

    def snapshot(self,month):
        start,end=month_bounds(month)
        years=range(start.year,(end-timedelta(days=1)).year+1)
        with self.lock:
            holidays,hs=self.source("holidays")
            f1=[];states=[]
            for year in years:
                items,state=self.source(year);f1.extend(items);states.append(state)
        fs="loading" if "loading" in states else "error" if "error" in states else "stale" if "stale" in states else "fresh"
        rows=[*holidays,*f1]
        for year in years:
            rows.extend(observances(year))
        unique={}
        for item in rows:
            day=item["date"]
            if start.isoformat()<=day<end.isoformat():
                unique.setdefault((day,item["title"],item["time"]),item)
        rows=sorted(unique.values(),key=lambda r:(r["date"],r["time"]!="All day",r["time"],r["title"]))
        return {"status":"fresh" if hs==fs=="fresh" else "partial","events":rows,
                "sources":{"holidays":hs,"f1":fs}}

service=PublicCalendar()

"""Fixed Bournemouth weather cache. Network refresh runs outside Spotify request thread."""
import threading
import time
import requests

URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
    "latitude": 50.72098, "longitude": -1.87669,
    "timezone": "Europe/London", "timeformat": "unixtime", "forecast_days": 8,
    "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,is_day",
    "hourly": "temperature_2m,precipitation_probability,weather_code,is_day",
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code,sunrise,sunset",
}
FRESH = 900
RETRY = 60
MAX_AGE = 21600
lock = threading.Lock()
data = None
updated = None
attempt = None
running = False
failed = False

def validate(value):
    if not isinstance(value,dict) or value.get("error"):
        raise ValueError("Invalid weather response")
    for section,fields in (("current",("time","temperature_2m","apparent_temperature","relative_humidity_2m","weather_code","is_day")),
                           ("hourly",("time","temperature_2m","precipitation_probability","weather_code","is_day")),
                           ("daily",("time","temperature_2m_max","temperature_2m_min","precipitation_probability_max","weather_code","sunrise","sunset"))):
        obj=value.get(section)
        if not isinstance(obj,dict) or not all(k in obj for k in fields):
            raise ValueError("Missing weather fields")
        if section!="current":
            n=len(obj["time"]) if isinstance(obj["time"],list) else 0
            if not n or not all(isinstance(obj[k],list) and len(obj[k])==n for k in fields):
                raise ValueError("Invalid weather arrays")
    if not isinstance(value.get("utc_offset_seconds"),(float,int)):
        raise ValueError("Missing weather offset")
    if not isinstance(value["current"]["time"],(int,float)) or not isinstance(value["current"]["temperature_2m"],(int,float)):
        raise ValueError("Missing current weather")
    return value

def refresh():
    global data,updated,running,failed
    try:
        response=requests.get(URL,params=PARAMS,timeout=(4,8),allow_redirects=False)
        if response.status_code!=200:
            raise ValueError("Weather service error")
        value=validate(response.json())
        with lock:
            data=value
            updated=time.time()
            failed=False
    except (requests.RequestException,ValueError,TypeError,KeyError):
        with lock:
            failed=True
    finally:
        with lock:
            running=False

def snapshot():
    global running,attempt
    with lock:
        now=time.time()
        age=max(0,now-updated) if updated is not None else None
        if not running and (age is None or age>=FRESH) and (attempt is None or now-attempt>=RETRY):
            attempt=now
            running=True
            threading.Thread(target=refresh,daemon=True,name="desk-weather-refresh").start()
        usable=data is not None and age is not None and age<MAX_AGE
        status=("stale" if failed or age>=FRESH else "fresh") if usable else ("loading" if running else "unavailable")
        return {"status":status,"updated":updated if usable else None,"data":data if usable else None}

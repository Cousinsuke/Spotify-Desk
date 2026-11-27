"""Local preview adapter for the original Gluroo reader."""
from pathlib import Path
import sys
import threading
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from glucose_live import LiveGlucose, STALE_SECONDS

class GlucoseService:
    def __init__(self, reader=None, clock=None, monotonic=None):
        self.reader = reader if reader is not None else LiveGlucose.from_environment()
        self.clock = clock or time.time
        self.monotonic = monotonic or time.monotonic
        self.lock = threading.Lock()
        self.cached = {"status":"loading","readings":[]}
        self.running = False
        self.next_check = 0.0
        if self.reader.config_error:
            self.cached = {"status":"configuration_error","readings":[]}
        elif not self.reader.url:
            self.cached = {"status":"not_configured","readings":[]}

    def refresh(self):
        try:
            result = self.reader.state()
        except Exception:
            # No private errors, URLs or credentials in logs.
            with self.lock:
                result = {**self.cached,"status":"stale" if self.cached.get("readings") else "unavailable"}
                result["retry_seconds"] = 150
        with self.lock:
            self.cached = result
            self.next_check = self.monotonic() + max(5,min(150,result.get("retry_seconds",150)))
            self.running = False

    def snapshot(self):
        with self.lock:
            status = self.cached["status"]
            if status not in ("configuration_error","not_configured") and not self.running and self.monotonic() >= self.next_check:
                self.running = True
                threading.Thread(target=self.refresh,daemon=True,name="desk-glucose-fetch").start()
            now = self.clock()
            result = dict(self.cached)
            rows = [p for p in result.get("readings",[]) if now*1000-86400000 <= p["timestamp"] <= now*1000+120000]
            result["readings"] = rows
            if rows:
                result["latest"] = rows[-1]
                age = max(0,int(now-rows[-1]["timestamp"]/1000))
                result["age_seconds"] = age
                if age >= STALE_SECONDS:
                    result["status"] = "stale"
            else:
                result.pop("latest",None)
                result.pop("age_seconds",None)
                if status in ("live","stale"):
                    result["status"] = "unavailable"
            return result

service = GlucoseService()

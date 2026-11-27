"""Read-only Linux server statistics; no privileged operations or identifiers."""
import os
import platform
import shutil
import time
from pathlib import Path

def read(path):
    try:return Path(path).read_text(errors="replace").strip()
    except OSError:return ""

def percent(used,total):
    return round(max(0,min(100,used*100/total)),1) if total>0 else None

def cpu_ticks(text):
    try:
        fields=text.splitlines()[0].split()
        if fields[0]!="cpu" or len(fields)<5:return None
        v=[int(x) for x in fields[1:9]]
        return sum(v),v[3]+(v[4] if len(v)>4 else 0)
    except (ValueError,IndexError):return None

def cpu_percent(before,after):
    if before is None or after is None:return None
    total=after[0]-before[0];idle=after[1]-before[1]
    if total<=0 or not 0<=idle<=total:return None
    return percent(total-idle,total)

def memory_stats(text):
    try:
        values={line.split(":")[0]:int(line.split(":")[1].split()[0])*1024 for line in text.splitlines() if ":" in line}
        total=values["MemTotal"];available=values["MemAvailable"]
        if not 0<=available<=total or total<=0:return None
        return {"used":total-available,"total":total,"percent":percent(total-available,total)}
    except (ValueError,KeyError,IndexError):return None

def temperature():
    readings=[]
    for sensor in Path("/sys/class/hwmon").glob("hwmon*"):
        kind=read(sensor/"name").lower()
        if kind not in ("coretemp","k10temp","zenpower","cpu_thermal"):continue
        for value in sensor.glob("temp*_input"):
            label=read(value.with_name(value.name.replace("_input","_label"))).lower()
            if kind=="coretemp" and not label.startswith("package"):continue
            if kind in ("k10temp","zenpower") and label not in ("tdie","tctl"):continue
            try:
                c=int(read(value))/1000
                if -10<=c<=150:readings.append(c)
            except ValueError:pass
    if not readings:
        for sensor in Path("/sys/class/thermal").glob("thermal_zone*"):
            if read(sensor/"type").lower() not in ("cpu-thermal","cpu_thermal","x86_pkg_temp","cpu","soc_thermal"):continue
            try:
                c=int(read(sensor/"temp"))/1000
                if -10<=c<=150:readings.append(c)
            except ValueError:pass
    return round(max(readings),1) if readings else None

class Hardware:
    def __init__(self):
        self.last_cpu=cpu_ticks(read("/proc/stat"));self.last_time=time.monotonic();self.cpu=None
    def snapshot(self,root):
        now=time.monotonic()
        if now-self.last_time>=0.25:
            current=cpu_ticks(read("/proc/stat"))
            self.cpu=cpu_percent(self.last_cpu,current);self.last_cpu=current;self.last_time=now
        try:
            disk=shutil.disk_usage(root)
            storage={"used":disk.used,"total":disk.total,"percent":percent(disk.used,disk.total)}
        except OSError:storage=None
        try:uptime=max(0,int(float(read("/proc/uptime").split()[0])))
        except (ValueError,IndexError,OverflowError):uptime=None
        try:os_name=platform.freedesktop_os_release().get("PRETTY_NAME",platform.system())
        except OSError:os_name=platform.system()
        model=read("/proc/device-tree/model").strip("\x00")
        links=[p for p in Path("/sys/class/net").glob("*") if p.name!="lo"]
        return {"os":os_name[:100],"architecture":platform.machine()[:32],"model":model[:100] if model.startswith("Raspberry Pi") else None,
                "cpu":self.cpu,"cores":os.cpu_count(),"memory":memory_stats(read("/proc/meminfo")),"storage":storage,
                "temperature":temperature(),"uptime":uptime,"network":"up" if any(read(p/"operstate")=="up" for p in links) else "unknown"}
hardware=Hardware()

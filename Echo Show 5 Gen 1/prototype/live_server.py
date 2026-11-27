"""Loopback-only, single-user Spotify test. No disk token cache or LAN exposure."""
import base64
import hashlib
import logging
import os
import re
import secrets
import time
from pathlib import Path
from urllib.parse import urlencode, urlparse
import requests
import weather_service
from flask import Flask, jsonify, redirect, request, send_from_directory

HOST = "127.0.0.1"
PORT = 8765
ORIGIN = f"http://{HOST}:{PORT}"
REDIRECT = ORIGIN + "/spotify/callback"
SCOPES = "user-read-playback-state user-read-currently-playing user-modify-playback-state user-library-read user-library-modify"
ROOT = Path(__file__).resolve().parent
CLIENT = os.environ.get("SPOTIPY_CLIENT_ID", "").strip()
app = Flask(__name__, static_folder=None)
token = None
pending = None
backoff = 0.0
saved_cache = {}
playback_cache = None
devices_cache = None
last_snapshot = None
last_seen = None
resume_grace = 300
resume_blocked = False
logging.getLogger("werkzeug").disabled = True
DIAGNOSTICS = os.environ.get("DESK_SPOTIFY_DIAGNOSTICS") == "1"

def diagnostic(label, **fields):
    if DIAGNOSTICS:
        print("[spotify-diag] "+time.strftime("%H:%M:%S")+" "+label+" "+
              " ".join(f"{k}={v}" for k,v in fields.items()), flush=True)

class ApiError(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message

@app.before_request
def protect():
    if request.host != f"{HOST}:{PORT}":
        return jsonify(error="Invalid local host"), 403
    if request.path.startswith("/api/"):
        if request.headers.get("X-Desk-Preview") != "1" or request.headers.get("Sec-Fetch-Site") not in (None, "same-origin"):
            return jsonify(error="Local preview request required"), 403
        if request.method != "GET" and request.headers.get("Origin") != ORIGIN:
            return jsonify(error="Invalid request origin"), 403

@app.after_request
def headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' https://i.scdn.co https://image-cdn-ak.spotifycdn.com https://image-cdn-fa.spotifycdn.com; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    return response

@app.errorhandler(ApiError)
def api_error(e):
    return jsonify(error=e.message), e.status

def exchange(data):
    global token
    try:
        r = requests.post("https://accounts.spotify.com/api/token", data={**data,"client_id":CLIENT}, timeout=12, allow_redirects=False)
        if r.status_code != 200:
            raise ApiError(401,"Spotify authorization failed. Check Client ID, redirect URI and account access.")
        new = r.json()
        if not new.get("access_token"):
            raise ApiError(401,"Spotify did not return an access token.")
        token = {**new, "refresh_token":new.get("refresh_token") or (token or {}).get("refresh_token"), "expires_at":time.monotonic()+int(new.get("expires_in",3600))}
    except requests.RequestException:
        raise ApiError(502,"Could not reach Spotify authorization server.")

def spotify(method,path,params=None,body=None):
    global token,backoff
    if not token:
        raise ApiError(401,"Connect Spotify first.")
    if time.monotonic()<backoff:
        raise ApiError(429,"Spotify rate limit; waiting before retry.")
    if token["expires_at"]<time.monotonic()+60:
        if not token.get("refresh_token"):
            token=None
            raise ApiError(401,"Reconnect Spotify.")
        exchange({"grant_type":"refresh_token","refresh_token":token["refresh_token"]})
    try:
        r=requests.request(method,"https://api.spotify.com/v1"+path,params=params,json=body,headers={"Authorization":"Bearer "+token["access_token"]},timeout=10,allow_redirects=False)
    except requests.RequestException:
        raise ApiError(502,"Could not reach Spotify.")
    if path.startswith("/me/player"):
        diagnostic("upstream", method=method, endpoint=path, status=r.status_code)
    if r.status_code==429:
        try: delay=max(1,int(r.headers.get("Retry-After","30")))
        except ValueError: delay=30
        backoff=time.monotonic()+delay
        raise ApiError(429,"Spotify rate limit; waiting before retry.")
    if r.status_code==401:
        token=None
        raise ApiError(401,"Spotify session expired; reconnect.")
    if r.status_code>=400 or 300<=r.status_code<400:
        raise ApiError(r.status_code if r.status_code<600 and r.status_code>=400 else 502,"Spotify rejected the request ("+str(r.status_code)+"). Check Premium, app access and device support.")
    # Playback/library writes acknowledge success; their response body is not data.
    # Spotify may return 204, an empty response, or a non-JSON success body.
    if method.upper() != "GET" or r.status_code == 204 or not r.content.strip():
        return None
    try:
        return r.json()
    except ValueError:
        raise ApiError(502,"Spotify returned an unreadable playback response.")

@app.get("/spotify/login")
def login():
    global pending
    if request.headers.get("Sec-Fetch-Site") not in (None,"same-origin","none"):
        raise ApiError(403,"Open Spotify login from the local dashboard.")
    if not CLIENT: raise ApiError(400,"Start the server with your Spotify Client ID.")
    verifier=secrets.token_urlsafe(64)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state=secrets.token_urlsafe(32)
    pending=(state,verifier,time.monotonic()+600)
    response = redirect("https://accounts.spotify.com/authorize?"+urlencode({"response_type":"code","client_id":CLIENT,"scope":SCOPES,"redirect_uri":REDIRECT,"state":state,"code_challenge_method":"S256","code_challenge":challenge}))
    response.set_cookie("desk_oauth_state",state,max_age=600,httponly=True,samesite="Lax",path="/spotify/callback")
    return response

@app.get("/spotify/callback")
def callback():
    global pending,playback_cache,devices_cache,last_snapshot,last_seen,resume_blocked
    item,pending=pending,None
    if not item or time.monotonic()>item[2] or not secrets.compare_digest(request.args.get("state",""),item[0]) or not secrets.compare_digest(request.cookies.get("desk_oauth_state",""),item[0]) or not request.args.get("code"):
        raise ApiError(400,"Authorization cancelled, expired or state mismatch. Open /spotify/login again.")
    exchange({"grant_type":"authorization_code","code":request.args["code"],"redirect_uri":REDIRECT,"code_verifier":item[1]})
    saved_cache.clear()
    playback_cache=devices_cache=last_snapshot=last_seen=None
    resume_blocked=False
    response=redirect("/?live=1")
    response.delete_cookie("desk_oauth_state",path="/spotify/callback")
    return response

def player(force=False):
    global playback_cache
    now=time.monotonic()
    if not force and playback_cache and now-playback_cache[0]<3:
        return playback_cache[1]
    p=spotify("GET","/me/player") or {}
    d=p.get("device") or {}
    diagnostic("player", present=bool(p), item=bool(p.get("item")),
               playing=bool(p.get("is_playing")), device=bool(d.get("id")),
               restricted=bool(d.get("is_restricted")),
               same_last=bool(d.get("id") and last_snapshot and d["id"]==last_snapshot.get("deviceId")))
    playback_cache=(time.monotonic(),p)
    return p

def safe_art(item):
    imgs=(item.get("album") or {}).get("images") or item.get("images") or []
    for img in sorted(imgs,key=lambda i:abs((i.get("width") or 320)-320)):
        url=img.get("url","")
        parsed=urlparse(url)
        if parsed.scheme=="https" and parsed.hostname in {"i.scdn.co","image-cdn-ak.spotifycdn.com","image-cdn-fa.spotifycdn.com"}:
            return url
    return ""

def saved_status(uri):
    if not uri: return None
    now=time.monotonic()
    entry=saved_cache.get(uri)
    if entry and now-entry[0]<60: return entry[1]
    try:
        result=spotify("GET","/me/library/contains",{"uris":uri})
        value=result[0] if isinstance(result,list) and result and isinstance(result[0],bool) else None
    except ApiError as e:
        if e.status in (401,429): raise
        value=None
    saved_cache.clear()
    saved_cache[uri]=(now,value)
    return value

def recovery_target(expected, rows):
    """Return verified, recent, or unavailable. Never guess another device."""
    if not isinstance(expected,str) or not expected:
        return None
    if any(row["active"] and row["id"]!=expected for row in rows):
        return None
    match=next((row for row in rows if row["id"]==expected),None)
    if match:
        return None if match["restricted"] else "verified"
    if (last_snapshot and last_snapshot.get("deviceId")==expected
        and last_snapshot.get("controllable") and last_seen is not None
        and time.monotonic()-last_seen<resume_grace and not resume_blocked):
        return "recent"
    return None

@app.get("/api/spotify/state")
def state():
    global last_snapshot,last_seen,resume_blocked
    if not token:
        last_snapshot=last_seen=None
        resume_blocked=False
        return jsonify(connected=False,saved=None)
    try:
        p=player(request.args.get("fresh")=="1")
        item=p.get("item") or {}
        d=p.get("device") or {}
        if not item and not d.get("id"):
            # A no-content playback response does not prove the account disconnected.
            # Keep one last track, marked historical, and verify its device independently.
            last=last_snapshot or {}
            expected=last.get("deviceId")
            rows=devices() if expected else []
            recovery=recovery_target(expected,rows)
            diagnostic("inactive", recovery=recovery or "none", blocked=resume_blocked,
                       remembered=bool(expected))
            if recovery=="verified":
                last_seen=time.monotonic()
                resume_blocked=False
            match=next((row for row in rows if row["id"]==expected),None) if recovery=="verified" else None
            return jsonify(**{**last,"connected":True,"playing":False,"inactive":True,
                "controllable":bool(recovery),"recovery":recovery,
                "device":(match["name"] if match else last.get("device")) if recovery else None,
                "deviceId":expected if recovery else None,"saved":None,"disallows":{"seeking":True,
                "pausing":True,"skipping_prev":recovery=="recent","skipping_next":recovery=="recent",
                "toggling_shuffle":True,"toggling_repeat_context":True}})
        uri=item.get("uri") if item.get("type")=="track" and not item.get("is_local") else None
        disallows=(p.get("actions") or {}).get("disallows") or p.get("actions") or {}
        snapshot=dict(connected=True,title=item.get("name"),artist=", ".join(a.get("name","") for a in item.get("artists",[])),art=safe_art(item),uri=uri,position=max(0,(p.get("progress_ms") or 0)//1000),positionMs=max(0,p.get("progress_ms") or 0),duration=max(0,(item.get("duration_ms") or 0)//1000),playing=bool(p.get("is_playing")),device=d.get("name"),deviceId=d.get("id"),controllable=bool(d.get("id") and not d.get("is_restricted")),shuffle=bool(p.get("shuffle_state")),repeat=p.get("repeat_state","off"),saved=saved_status(uri),disallows=disallows,inactive=False)
        if item and d.get("id"):
            last_snapshot=snapshot.copy()
            last_seen=time.monotonic() if snapshot["controllable"] else None
            resume_blocked=False
        elif d.get("id") and last_snapshot and d.get("id")!=last_snapshot.get("deviceId"):
            last_snapshot=last_seen=None
            resume_blocked=False
        return jsonify(**snapshot)
    except ApiError as e:
        if not token:last_snapshot=last_seen=None
        return jsonify(connected=bool(token),saved=None,error=e.message)


def devices(force=False):
    global devices_cache
    now=time.monotonic()
    if not force and devices_cache and now-devices_cache[0]<5:return devices_cache[1]
    result=spotify("GET","/me/player/devices") or {}
    rows=[{"id":d.get("id"),"name":d.get("name","Device"),"active":bool(d.get("is_active")),"restricted":bool(d.get("is_restricted"))} for d in result.get("devices",[])]
    expected=(last_snapshot or {}).get("deviceId")
    diagnostic("devices", count=len(rows), active=sum(bool(row["active"]) for row in rows),
               last_present=bool(expected and any(row["id"]==expected for row in rows)),
               other_active=any(row["active"] and row["id"]!=expected for row in rows))
    devices_cache=(now,rows)
    return rows

@app.get("/api/spotify/devices")
def list_devices():
    return jsonify(devices=devices())

@app.post("/api/spotify/command")
def command():
    global playback_cache,devices_cache,last_snapshot,last_seen,resume_blocked
    data=request.get_json(silent=True)
    if not isinstance(data,dict):raise ApiError(400,"Invalid command.")
    a,v=data.get("action"),data.get("value")
    if a not in ("device","save","toggle","next","previous","seek","shuffle","repeat"):
        raise ApiError(400,"Invalid command.")
    diagnostic("command", action=a, desired=v if a=="toggle" and type(v) is bool else "-")
    if a=="device":
        if not isinstance(v,str) or not any(d["id"]==v and not d["restricted"] for d in devices(True)):
            raise ApiError(400,"Device no longer available.")
        spotify("PUT","/me/player",body={"device_ids":[v],"play":False})
        devices_cache=None
        if last_snapshot and last_snapshot.get("deviceId")!=v:
            last_snapshot=last_seen=None
        resume_blocked=False
    else:
        p=player(True); playback_cache=None; d=p.get("device") or {};item=p.get("item") or {}
        if a=="save":
            uri=item.get("uri")
            if not isinstance(uri,str) or not re.fullmatch(r"spotify:track:[A-Za-z0-9]+",uri) or uri!=data.get("uri") or item.get("is_local"):
                raise ApiError(409,"Track changed or cannot be saved.")
            current=saved_status(uri)
            if current is None:raise ApiError(409,"Saved state unavailable.")
            spotify("DELETE" if current else "PUT","/me/library",{"uris":uri})
            saved_cache.pop(uri,None)
        else:
            expected=data.get("device")
            recovery=None
            if d.get("id"):
                if d.get("is_restricted") or d["id"]!=expected:
                    raise ApiError(409,"Active device changed. Select the intended playback device again.")
            else:
                # Never silently target a different device, or infer a track when absent.
                if p.get("is_playing") or not isinstance(expected,str) or not expected or a not in ("toggle","next","previous") or (a=="toggle" and v is not True):
                    raise ApiError(409,"No active playback. Open Spotify on your device or select it again.")
                rows=devices(True)
                recovery=recovery_target(expected,rows)
                if not recovery or (recovery=="recent" and not (a=="toggle" and v is True)):
                    raise ApiError(409,"Playback device is unavailable or changed. Open Spotify on it or select it again.")
            params={"device_id":expected}
            if a=="toggle":
                # Explicit requested state avoids an inverted toggle on a delayed read.
                desired=v if type(v) is bool else not bool(p.get("is_playing"))
                if not d.get("id") or desired!=bool(p.get("is_playing")):
                    try:
                        spotify("PUT","/me/player/"+("play" if desired else "pause"),params)
                    except ApiError as e:
                        if recovery=="recent" and e.status in (403,404):
                            resume_blocked=True
                            devices_cache=None
                            raise ApiError(e.status,"Spotify cannot reach the last device. Open Spotify on it, then select it again.")
                        raise
                if not desired and last_snapshot and last_snapshot.get("deviceId")==expected:
                    last_snapshot["playing"]=False
                    if item.get("uri")==last_snapshot.get("uri") and isinstance(p.get("progress_ms"),int):
                        last_snapshot["positionMs"]=max(0,p["progress_ms"])
                        last_snapshot["position"]=last_snapshot["positionMs"]//1000
                    if d.get("id"):
                        last_seen=time.monotonic()
            elif a in ("next","previous"):spotify("POST","/me/player/"+a,params)
            elif a=="seek":
                if type(v) not in (int,float) or not 0<=v<=((item.get("duration_ms") or 0)/1000) or item.get("uri")!=data.get("uri"):raise ApiError(400,"Invalid seek or track changed.")
                spotify("PUT","/me/player/seek",{**params,"position_ms":int(v*1000)})
            elif a=="shuffle":spotify("PUT","/me/player/shuffle",{**params,"state":str(not p.get("shuffle_state")).lower()})
            elif a=="repeat":spotify("PUT","/me/player/repeat",{**params,"state":{"off":"context","context":"track","track":"off"}.get(p.get("repeat_state"),"off")})
            else:raise ApiError(400,"Unknown command.")
    playback_cache=None
    diagnostic("command_ack", action=a)
    return jsonify(ok=True)

@app.get("/api/weather")
def weather_state():return jsonify(weather_service.snapshot())

@app.get("/")
def index():return send_from_directory(ROOT,"index.html")

@app.get("/<name>")
def asset(name):
    if name not in {"style.css","app.js","spotify-preview.js","spotify-live.js","playback-clock.js","album-palette.js","weather-preview.js","weather-live.js","favicon.svg","weather-sky.svg"}:return "",404
    return send_from_directory(ROOT,name)

if __name__=="__main__":
    if not re.fullmatch(r"[A-Za-z0-9]{16,128}",CLIENT):
        raise SystemExit("Set SPOTIPY_CLIENT_ID locally before starting.")
    print("Local Spotify test: "+ORIGIN+"/?live=1 (tokens held in memory only)",flush=True)
    app.run(host=HOST,port=PORT,debug=False,use_reloader=False,threaded=False)

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
logging.getLogger("werkzeug").disabled = True

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
    return r.json() if r.content else None

@app.get("/spotify/login")
def login():
    global pending
    if not CLIENT: raise ApiError(400,"Start the server with your Spotify Client ID.")
    verifier=secrets.token_urlsafe(64)
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state=secrets.token_urlsafe(32)
    pending=(state,verifier,time.monotonic()+600)
    return redirect("https://accounts.spotify.com/authorize?"+urlencode({"response_type":"code","client_id":CLIENT,"scope":SCOPES,"redirect_uri":REDIRECT,"state":state,"code_challenge_method":"S256","code_challenge":challenge}))

@app.get("/spotify/callback")
def callback():
    global pending,playback_cache,devices_cache
    item,pending=pending,None
    if not item or time.monotonic()>item[2] or not secrets.compare_digest(request.args.get("state",""),item[0]) or not request.args.get("code"):
        raise ApiError(400,"Authorization cancelled, expired or state mismatch. Open /spotify/login again.")
    exchange({"grant_type":"authorization_code","code":request.args["code"],"redirect_uri":REDIRECT,"code_verifier":item[1]})
    saved_cache.clear()
    playback_cache=devices_cache=None
    return redirect("/?live=1")

def player(force=False):
    global playback_cache
    now=time.monotonic()
    if not force and playback_cache and now-playback_cache[0]<3:
        return playback_cache[1]
    p=spotify("GET","/me/player") or {}
    playback_cache=(now,p)
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

@app.get("/api/spotify/state")
def state():
    if not token:return jsonify(connected=False,saved=None)
    try:
        p=player()
        item=p.get("item") or {}
        d=p.get("device") or {}
        uri=item.get("uri") if item.get("type")=="track" and not item.get("is_local") else None
        disallows=(p.get("actions") or {}).get("disallows") or p.get("actions") or {}
        return jsonify(connected=True,title=item.get("name"),artist=", ".join(a.get("name","") for a in item.get("artists",[])),art=safe_art(item),uri=uri,position=max(0,(p.get("progress_ms") or 0)//1000),duration=max(0,(item.get("duration_ms") or 0)//1000),playing=bool(p.get("is_playing")),device=d.get("name"),deviceId=d.get("id"),controllable=bool(d.get("id") and not d.get("is_restricted")),shuffle=bool(p.get("shuffle_state")),repeat=p.get("repeat_state","off"),saved=saved_status(uri),disallows=disallows)
    except ApiError as e:
        return jsonify(connected=bool(token),saved=None,error=e.message)

def devices(force=False):
    global devices_cache
    now=time.monotonic()
    if not force and devices_cache and now-devices_cache[0]<5:return devices_cache[1]
    result=spotify("GET","/me/player/devices") or {}
    rows=[{"id":d.get("id"),"name":d.get("name","Device"),"active":bool(d.get("is_active")),"restricted":bool(d.get("is_restricted"))} for d in result.get("devices",[])]
    devices_cache=(now,rows)
    return rows

@app.get("/api/spotify/devices")
def list_devices():
    return jsonify(devices=devices())

@app.post("/api/spotify/command")
def command():
    global playback_cache,devices_cache
    data=request.get_json(silent=True)
    if not isinstance(data,dict):raise ApiError(400,"Invalid command.")
    a,v=data.get("action"),data.get("value")
    if not isinstance(a,str):raise ApiError(400,"Invalid command.")
    if a=="device":
        if not isinstance(v,str) or not any(d["id"]==v and not d["restricted"] for d in devices(True)):
            raise ApiError(400,"Device no longer available.")
        spotify("PUT","/me/player",body={"device_ids":[v],"play":False})
        devices_cache=None
    else:
        p=player(True); d=p.get("device") or {};item=p.get("item") or {}
        if a=="save":
            uri=item.get("uri")
            if not isinstance(uri,str) or not re.fullmatch(r"spotify:track:[A-Za-z0-9]+",uri) or uri!=data.get("uri") or item.get("is_local"):
                raise ApiError(409,"Track changed or cannot be saved.")
            current=saved_status(uri)
            if current is None:raise ApiError(409,"Saved state unavailable.")
            spotify("DELETE" if current else "PUT","/me/library",{"uris":uri})
            saved_cache.pop(uri,None)
        else:
            if not d.get("id") or d.get("is_restricted") or d["id"]!=data.get("device"):
                raise ApiError(409,"Active playback device changed or is unavailable.")
            params={"device_id":d["id"]}
            if a=="toggle":spotify("PUT","/me/player/"+("pause" if p.get("is_playing") else "play"),params)
            elif a in ("next","previous"):spotify("POST","/me/player/"+a,params)
            elif a=="seek":
                if type(v) not in (int,float) or not 0<=v<=((item.get("duration_ms") or 0)/1000) or item.get("uri")!=data.get("uri"):raise ApiError(400,"Invalid seek or track changed.")
                spotify("PUT","/me/player/seek",{**params,"position_ms":int(v*1000)})
            elif a=="shuffle":spotify("PUT","/me/player/shuffle",{**params,"state":str(not p.get("shuffle_state")).lower()})
            elif a=="repeat":spotify("PUT","/me/player/repeat",{**params,"state":{"off":"context","context":"track","track":"off"}.get(p.get("repeat_state"),"off")})
            else:raise ApiError(400,"Unknown command.")
    playback_cache=None
    return jsonify(ok=True)

@app.get("/")
def index():return send_from_directory(ROOT,"index.html")

@app.get("/<name>")
def asset(name):
    if name not in {"style.css","app.js","spotify-preview.js","spotify-live.js","favicon.svg"}:return "",404
    return send_from_directory(ROOT,name)

if __name__=="__main__":
    if not re.fullmatch(r"[A-Za-z0-9]{16,128}",CLIENT):
        raise SystemExit("Set SPOTIPY_CLIENT_ID locally before starting.")
    print("Local Spotify test: "+ORIGIN+"/?live=1 (tokens held in memory only)",flush=True)
    app.run(host=HOST,port=PORT,debug=False,use_reloader=False,threaded=False)

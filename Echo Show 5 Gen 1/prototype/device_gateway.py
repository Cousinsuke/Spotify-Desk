"""Authenticated HTTPS device gateway; sample default, explicit opt-in scoped live API."""
import argparse
import hashlib
import ipaddress
import json
import math
import requests
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import subprocess
import tempfile
import time
from contextlib import contextmanager
from flask import Flask, request, redirect, send_from_directory, make_response, abort, jsonify

ROOT = Path(__file__).resolve().parent
STATE = Path.home() / ".local/share/spotify-desk-device"
PORT = 8443
COOKIE = "__Host-desk_device"
PAIR_SECONDS = 600
SESSION_SECONDS = 30 * 86400
ASSETS = frozenset(("style.css","app.js","spotify-preview.js","spotify-live.js","playback-clock.js",
    "album-palette.js","weather-preview.js","weather-live.js","glucose-chart.js","glucose-preview.js",
    "glucose-live.js","favicon.svg","weather-sky.svg","device-session.js"))
PRIVATE = tuple(ipaddress.ip_network(x) for x in ("10.0.0.0/8","172.16.0.0/12","192.168.0.0/16"))
SCHEMA = """CREATE TABLE IF NOT EXISTS pairing (id INTEGER PRIMARY KEY CHECK(id=1), digest TEXT, expires INTEGER, tries INTEGER);
CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, digest TEXT UNIQUE NOT NULL, expires INTEGER NOT NULL);"""

def validate_network(bind, network):
    ip=ipaddress.IPv4Address(bind)
    net=ipaddress.IPv4Network(network)
    if net.prefixlen<24 or not any(net.subnet_of(n) for n in PRIVATE) or ip not in net or ip in (net.network_address,net.broadcast_address):
        raise ValueError("Choose an RFC1918 LAN address and local /24 or smaller subnet.")
    return str(ip),str(net)

def private_dir(path):
    info=path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:
        raise ValueError("Device state directory must be private and owner-owned.")

def private_file(path):
    info=path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o077:
        raise ValueError("Unsafe device state file.")

def digest(value):
    return hashlib.sha256(value.encode("ascii")).hexdigest()

@contextmanager
def db(path):
    con=sqlite3.connect(path,timeout=5)
    try:
        with con:yield con
    finally:con.close()

def setup_db(path):
    with db(path) as con:con.executescript(SCHEMA)
    os.chmod(path,0o600)

def issue(path,now=None):
    now=int(time.time() if now is None else now)
    code=secrets.token_hex(8)
    with db(path) as con:
        con.execute("INSERT OR REPLACE INTO pairing VALUES (1,?,?,0)",(digest(code),now+PAIR_SECONDS))
    return code

def exchange(path,code,now=None):
    now=int(time.time() if now is None else now)
    with db(path) as con:
        con.execute("BEGIN IMMEDIATE")
        row=con.execute("SELECT digest,expires,tries FROM pairing WHERE id=1").fetchone()
        if not row or row[1]<=now or row[2]>=8:return None
        if not re.fullmatch(r"[a-f0-9]{16}",code) or not secrets.compare_digest(digest(code),row[0]):
            con.execute("UPDATE pairing SET tries=tries+1 WHERE id=1")
            return None
        con.execute("DELETE FROM pairing")
        con.execute("DELETE FROM sessions WHERE expires<=?",(now,))
        if con.execute("SELECT count(*) FROM sessions").fetchone()[0]>=8:return None
        token=secrets.token_urlsafe(32)
        con.execute("INSERT INTO sessions VALUES (?,?,?)",(secrets.token_hex(6),digest(token),now+SESSION_SECONDS))
        return token

def authorized(path,token,now=None):
    if not re.fullmatch(r"[A-Za-z0-9_-]{43}",token or ""):return False
    now=int(time.time() if now is None else now)
    with db(path) as con:
        return con.execute("SELECT 1 FROM sessions WHERE digest=? AND expires>?",(digest(token),now)).fetchone() is not None

def revoke(path,session_id=None):
    with db(path) as con:
        if session_id is None:
            con.execute("DELETE FROM sessions")
            con.execute("DELETE FROM pairing")
        else:con.execute("DELETE FROM sessions WHERE id=?",(session_id,))

def openssl(*args):
    subprocess.run(["openssl",*map(str,args)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def initialize(state,bind,network):
    bind,network=validate_network(bind,network)
    state.mkdir(mode=0o700,parents=True,exist_ok=False)
    private_dir(state)
    # CA signing key exists only in a private temporary directory; never export it.
    # Renewal requires a fresh CA and explicit client re-trust.
    with tempfile.TemporaryDirectory(dir=state) as tmp:
        tmp=Path(tmp)
        ca_key=tmp/"ca.key";csr=tmp/"server.csr";ext=tmp/"extensions"
        openssl("req","-x509","-newkey","rsa:3072","-nodes","-sha256","-days","400",
                "-subj","/CN=Spotify Desk Local Device CA","-keyout",ca_key,"-out",state/"ca.crt",
                "-addext","basicConstraints=critical,CA:TRUE,pathlen:0","-addext","keyUsage=critical,keyCertSign,cRLSign")
        openssl("req","-new","-newkey","rsa:2048","-nodes","-sha256","-subj","/CN="+bind,
                "-keyout",state/"server.key","-out",csr)
        ext.write_text("basicConstraints=critical,CA:FALSE\nkeyUsage=critical,digitalSignature,keyEncipherment\nextendedKeyUsage=serverAuth\nsubjectAltName=IP:"+bind+"\n")
        openssl("x509","-req","-in",csr,"-CA",state/"ca.crt","-CAkey",ca_key,"-CAserial",tmp/"serial",
                "-CAcreateserial","-out",state/"server.crt","-days","365","-sha256","-extfile",ext)
        openssl("verify","-CAfile",state/"ca.crt","-verify_ip",bind,state/"server.crt")
    for name in ("ca.crt","server.crt","server.key"):os.chmod(state/name,0o600)
    setup_db(state/"devices.sqlite")
    (state/"config.json").write_text(json.dumps({"bind":bind,"network":network}))
    os.chmod(state/"config.json",0o600)

def config(state):
    private_dir(state)
    for name in ("ca.crt","server.crt","server.key","devices.sqlite","config.json"):private_file(state/name)
    data=json.loads((state/"config.json").read_text())
    return validate_network(data["bind"],data["network"])


LIVE_GET=frozenset(("/api/spotify/state","/api/spotify/devices","/api/weather","/api/glucose","/api/calendar","/api/system"))
LIVE_POST="/api/spotify/command"
LOCAL="http://127.0.0.1:8765"
LIMIT=1024*1024

def live_enabled(state):
    marker=state/"live-enabled"
    try:private_file(marker)
    except FileNotFoundError:return False
    return marker.read_text()=="enabled\n"

def switch_live(state,enabled):
    marker=state/"live-enabled"
    if enabled:
        if marker.exists():private_file(marker)
        else:
            with os.fdopen(os.open(marker,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600),"w") as f:
                f.write("enabled\n")
    else:marker.unlink(missing_ok=True)
    revoke(state/"devices.sqlite")

def query_for(path,args):
    if not args:return {}
    if path=="/api/spotify/state" and list(args)==["fresh"] and args.getlist("fresh")==["1"]:
        return {"fresh":"1"}
    if path=="/api/calendar" and list(args)==["month"] and len(args.getlist("month"))==1 and re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])-01",args["month"]):
        return {"month":args["month"]}
    raise ValueError("Invalid query")

def command_body(data):
    if not isinstance(data,dict) or set(data)-{"action","value","uri","device"}:raise ValueError("Invalid command")
    action=data.get("action")
    if action not in ("toggle","next","previous","seek","shuffle","repeat","save","device"):raise ValueError("Invalid action")
    for key in ("uri","device"):
        value=data.get(key)
        if value is not None and (not isinstance(value,str) or len(value)>256):raise ValueError("Invalid target")
    value=data.get("value")
    if action=="toggle" and type(value) is not bool:raise ValueError("Explicit playback state required")
    if action=="seek" and (type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=86400):raise ValueError("Invalid seek")
    if action=="device" and (not isinstance(value,str) or not 0<len(value)<=256):raise ValueError("Invalid device")
    if action not in ("toggle","seek","device") and value is not None and type(value) is not bool:raise ValueError("Invalid value")
    return data

def local_api(method,path,params,body):
    # Fixed loopback destination; no redirects, environment proxies, browser cookies,
    # forwarding headers, arbitrary paths or request-header forwarding.
    if (method,path) not in {( "GET",p) for p in LIVE_GET}|{("POST",LIVE_POST)}:raise ValueError("Route denied")
    with requests.Session() as session:
        session.trust_env=False
        headers={"X-Desk-Preview":"1","Sec-Fetch-Site":"same-origin","Accept":"application/json"}
        if method=="POST":headers["Origin"]=LOCAL
        with session.request(method,LOCAL+path,params=params,json=body,headers=headers,
                             timeout=(2,12),allow_redirects=False,stream=True) as result:
            if result.status_code not in (200,400,401,403,404,409,429,500,502,503,504):
                raise ValueError("Unexpected backend response")
            if not result.headers.get("Content-Type","").lower().startswith("application/json"):
                raise ValueError("Unexpected backend type")
            raw=bytearray()
            for chunk in result.iter_content(16384):
                raw.extend(chunk)
                if len(raw)>LIMIT:raise ValueError("Response too large")
            data=json.loads(raw)
            if not isinstance(data,dict):raise ValueError("Unexpected backend data")
            # Do not forward upstream error bodies, headers, cookies or redirects.
            if result.status_code!=200:
                return {"error":"Backend request rejected or unavailable. Check the local dashboard."},result.status_code if result.status_code!=401 else 503
            return data,200


PAIR_PAGE="""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pair Spotify Desk</title>
<style>body{font:18px system-ui;background:#14181d;color:#eee;display:grid;place-items:center;min-height:90vh}main{max-width:420px;padding:24px}input,button{font:inherit;padding:12px;border-radius:8px;width:100%;box-sizing:border-box;margin:8px 0}button{background:#a6c9ed;border:0;color:#111}p{color:#b9c3ce}</style>
<main><h1>Pair this display</h1><p>Sample-data test only. Enter the one-time code generated on the Raspberry Pi.</p>
<form method="post" action="/pair" autocomplete="off"><label for="code">Pairing code</label><input id="code" name="code" type="password" maxlength="16" required autocomplete="off" autocapitalize="none"><button>Pair display</button></form></main></html>"""

def create_app(path,bind,network,clock=time.time,live=False,backend=local_api):
    bind,network=validate_network(bind,network)
    net=ipaddress.ip_network(network);host=f"{bind}:{PORT}";origin="https://"+host
    app=Flask(__name__,static_folder=None)
    app.config.update(MAX_CONTENT_LENGTH=1024,MAX_FORM_MEMORY_SIZE=1024,MAX_FORM_PARTS=2)
    @app.before_request
    def boundary():
        try:peer=ipaddress.ip_address(request.remote_addr or "")
        except ValueError:abort(403)
        if not request.is_secure or request.host!=host or peer not in net:abort(403)
        if request.headers.get("Sec-Fetch-Site") not in (None,"none","same-origin"):abort(403)
        if request.method not in ("GET","HEAD","POST"):abort(405)
        if request.method=="POST" and request.headers.get("Origin")!=origin:abort(403)
        api_route=live and request.path in LIVE_GET|{LIVE_POST,"/api/device/session"}
        if not api_route and request.path not in ("/","/pair") and request.path.lstrip("/") not in ASSETS:abort(404)
        if request.path!="/pair" and not authorized(path,request.cookies.get(COOKIE),clock()):
            if request.path=="/" and request.method in ("GET","HEAD"):return redirect("/pair",303)
            abort(401)
        if api_route:
            if request.headers.get("X-Desk-Preview")!="1":abort(403)
            if request.method!=("POST" if request.path==LIVE_POST else "GET"):abort(405)
        elif request.method=="POST" and request.path!="/pair":abort(405)

    @app.after_request
    def headers(response):
        response.headers["Cache-Control"]="no-store"
        # Native same-origin form POST needs its real Origin; no-referrer makes it null.
        # Limit the exception to the pairing page; never accept null or missing Origin.
        response.headers["Referrer-Policy"]="same-origin" if request.path=="/pair" else "no-referrer"
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["X-Frame-Options"]="DENY"
        images=" https://i.scdn.co https://image-cdn-ak.spotifycdn.com https://image-cdn-fa.spotifycdn.com" if live else ""
        connections="'self'" if live else "'none'"
        response.headers["Content-Security-Policy"]="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:"+images+"; connect-src "+connections+"; frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'"
        return response

    @app.route("/pair",methods=["GET","POST"])
    def pair():
        if request.method=="GET":
            if authorized(path,request.cookies.get(COOKIE),clock()):return redirect("/",303)
            return PAIR_PAGE.replace("Sample-data test only. ", "Live dashboard. " if live else "Sample-data test only. ")
        if request.mimetype!="application/x-www-form-urlencoded":abort(415)
        token=exchange(path,request.form.get("code","").strip().lower(),clock())
        if token is None:return "Pairing code invalid, expired, locked or device limit reached. Generate a new code on the Pi.",403
        response=redirect("/",303)
        response.set_cookie(COOKIE,token,max_age=SESSION_SECONDS,secure=True,httponly=True,samesite="Strict",path="/")
        return response

    @app.get("/")
    def index():
        if live:
            if request.query_string!=b"live=1":return redirect("/?live=1",303)
            html=(ROOT/"index.html").read_text(encoding="utf-8")
            return make_response(html.replace('<html lang="en">','<html lang="en" data-device-gateway="1">',1).replace('</head>','<script defer src="device-session.js"></script></head>',1))
        if request.query_string:return redirect("/",303)
        return send_from_directory(ROOT,"index.html")

    @app.route("/api/<path:name>",methods=["GET","POST"])
    def live_api(name):
        route="/api/"+name
        if not live:abort(404)
        if route=="/api/device/session":
            if request.args:abort(400)
            return jsonify(ok=True)
        try:
            params=query_for(route,request.args)
            body=None
            if request.method=="POST":
                if request.mimetype!="application/json":abort(415)
                body=command_body(request.get_json(silent=True))
        except (ValueError,OverflowError):return jsonify(error="Invalid device request"),400
        try:
            data,status=backend(request.method,route,params,body)
            return jsonify(data),status
        except (requests.RequestException,ValueError,OSError):
            return jsonify(error="Local backend unavailable"),503
    @app.get("/<name>")
    def asset(name):
        if name not in ASSETS:abort(404)
        return send_from_directory(ROOT,name)
    return app

def serve(state):
    bind,net=config(state)
    from gunicorn.app.base import BaseApplication
    class Server(BaseApplication):
        def load_config(self):
            options={"bind":f"{bind}:{PORT}","workers":1,"worker_class":"gthread","threads":2,
                "certfile":str(state/"server.crt"),"keyfile":str(state/"server.key"),
                "accesslog":None,"forwarded_allow_ips":"","secure_scheme_headers":{},
                "limit_request_line":2048,"limit_request_fields":32,"limit_request_field_size":4096,
                "timeout":30,"keepalive":2,"worker_connections":32,"backlog":32}
            for key,value in options.items():self.cfg.set(key,value)
        def load(self):return create_app(state/"devices.sqlite",bind,net,live=live_enabled(state))
    Server().run()

def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description="Authenticated LAN device gateway")
    sub=parser.add_subparsers(dest="action",required=True)
    init=sub.add_parser("init");init.add_argument("--bind",required=True);init.add_argument("--network",required=True)
    sub.add_parser("serve");sub.add_parser("pair");sub.add_parser("list")
    sub.add_parser("live-on");sub.add_parser("live-off")
    rev=sub.add_parser("revoke");rev.add_argument("id")
    args=parser.parse_args()
    if args.action=="init":
        initialize(STATE,args.bind,args.network);print("TLS setup complete. Public CA:",STATE/"ca.crt");return
    bind,net=config(STATE)
    path=STATE/"devices.sqlite"
    if args.action=="serve":serve(STATE)
    elif args.action in ("live-on","live-off"):
        switch_live(STATE,args.action=="live-on");print("Mode updated and sessions revoked. Restart device service and pair again.")
    elif args.action=="pair":print("One-time code (valid 10 minutes):",issue(path))
    elif args.action=="list":
        with db(path) as con:
            for sid,expiry in con.execute("SELECT id,expires FROM sessions WHERE expires>? ORDER BY expires",(int(time.time()),)):
                print(sid,time.strftime("%Y-%m-%d %H:%M UTC",time.gmtime(expiry)))
    elif args.action=="revoke":revoke(path,None if args.id=="all" else args.id);print("Revoked.")

if __name__=="__main__":
    try:main()
    except (ValueError,OSError,sqlite3.Error,subprocess.CalledProcessError):
        raise SystemExit("Device gateway setup or state error. Check local directory, certificate and bind configuration; no live service changes.")

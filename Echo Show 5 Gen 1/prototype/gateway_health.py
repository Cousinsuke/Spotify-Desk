"""Local, credential-free HTTPS health check; never starts a stopped gateway."""
import http.client
import ssl
import subprocess
import time
from device_gateway import STATE, PORT, config

UNIT = "spotify-desk-device.service"

def probe(state, bind):
    # The configured CA and IP SAN must validate. Never follow redirects.
    context = ssl.create_default_context(cafile=str(state / "ca.crt"))
    conn = http.client.HTTPSConnection(bind, PORT, timeout=5, context=context)
    try:
        conn.request("GET", "/", headers={"Connection": "close"})
        with conn.getresponse() as response:
            if response.status == 303 and response.getheader("Location") == "/pair":
                return "ok"
            return "unhealthy"
    except ssl.SSLCertVerificationError:
        return "certificate"
    except (OSError, http.client.HTTPException):
        return "unhealthy"
    finally:
        conn.close()

def active():
    return subprocess.run(["systemctl", "--user", "is-active", "--quiet", UNIT],
                          timeout=5, check=False).returncode == 0

def check(state=STATE):
    if not active():
        print("Gateway not active; no automatic start.")
        return 0
    bind, _ = config(state)
    for attempt in range(2):
        result = probe(state, bind)
        if result == "ok":
            return 0
        if result == "certificate":
            print("Gateway certificate validation failed; manual investigation required.")
            return 1
        if attempt == 0:
            time.sleep(5)
    if not active():
        return 0
    print("Gateway failed two trusted HTTPS probes; requesting gateway-only restart.")
    return subprocess.run(["systemctl", "--user", "--no-block", "try-restart", UNIT],
                          timeout=5, check=False).returncode

if __name__ == "__main__":
    try:
        raise SystemExit(check())
    except (OSError, ValueError, subprocess.SubprocessError):
        raise SystemExit("Gateway health check could not run; inspect local state and user service.")

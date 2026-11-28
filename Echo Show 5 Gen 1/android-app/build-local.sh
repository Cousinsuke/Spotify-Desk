#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ $# != 2 ]]; then
    echo "Usage: bash build-local.sh https://HOST:PORT/ /path/to/public-ca.crt" >&2
    exit 2
fi
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-17-openjdk}"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
export ANDROID_SDK_ROOT="$ANDROID_HOME"
export PATH="$JAVA_HOME/bin:$PATH"
GRADLE="${GRADLE_BIN:-$HOME/Android/Tools/gradle-8.9/bin/gradle}"
test -x "$GRADLE"
test -f "$ANDROID_HOME/platforms/android-35/android.jar"
test -x "$ANDROID_HOME/build-tools/34.0.0/aapt2"
python3 - "$1" "$2" <<'PY'
import ipaddress
import pathlib
import re
import subprocess
import sys
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

url, cert = sys.argv[1:]
u = urlsplit(url)
if u.scheme != 'https' or not u.hostname or u.username or u.password or u.path not in ('', '/') or u.query or u.fragment:
    sys.exit('Provide an HTTPS origin only, without credentials, path, query or fragment.')
host = u.hostname
try:
    ip = ipaddress.ip_address(host)
    if ip.version != 4:
        sys.exit('This prototype supports IPv4 or DNS names.')
except ValueError:
    if not re.fullmatch(r'[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?', host):
        sys.exit('Invalid hostname.')
port = u.port or 443
if not 1 <= port <= 65535:
    sys.exit('Invalid port.')
source = pathlib.Path(cert).expanduser()
data = source.read_bytes()
if b'PRIVATE KEY' in data or data.count(b'-----BEGIN CERTIFICATE-----') != 1:
    sys.exit('Expected exactly one PEM public CA certificate, not a key or bundle.')
info = subprocess.check_output(['openssl', 'x509', '-in', str(source), '-noout', '-ext', 'basicConstraints'], text=True)
if 'CA:TRUE' not in info:
    sys.exit('Certificate is not a CA.')
subprocess.run(['openssl','x509','-in',str(source),'-checkend','0','-noout'],check=True)
base = pathlib.Path('app/build/generated/local-res')
for sub in ('raw','xml','values'):
    (base / sub).mkdir(parents=True, exist_ok=True)
(base/'raw/desk_ca.pem').write_bytes(data)
origin = f'https://{host}:{port}/'
(base/'values/local_config.xml').write_text(f'<resources><string name="dashboard_origin">{escape(origin)}</string></resources>\n')
(base/'xml/network_security_config.xml').write_text(f'''<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors><certificates src="system"/></trust-anchors>
    </base-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="false">{escape(host)}</domain>
        <trust-anchors><certificates src="@raw/desk_ca"/></trust-anchors>
    </domain-config>
</network-security-config>
''')
print('Local HTTPS origin and CA resources generated (ignored by Git).')
PY
"$GRADLE" --no-daemon :app:assembleDebug
echo "APK: app/build/outputs/apk/debug/app-debug.apk"

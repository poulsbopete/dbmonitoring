#!/bin/bash
# Verify the track is using config.yml for VMs + secrets (do NOT attach a
# secrets-only sandboxConfig — that wiped virtualmachines and skipped track setup).
#
# Usage: ./apply-secrets.sh

set -euo pipefail

TOKEN=$(python3 -c "import json; d=json.load(open('$HOME/.config/instruqt/credentials')); print(d['access_token'])")

python3 - <<'PY'
import json, urllib.request, os, sys
token = os.environ.get('TOKEN') or open(os.path.expanduser('~/.config/instruqt/credentials')).read()
import pathlib
token = json.loads(pathlib.Path.home().joinpath('.config/instruqt/credentials').read_text())['access_token']

def gql(query):
    req = urllib.request.Request(
        'https://play.instruqt.com/graphql',
        data=json.dumps({'query': query}).encode(),
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

res = gql('''
query {
  track(trackSlug: "serverless-db-monitoring", organizationSlug: "elastic") {
    sandboxConfig { id }
    config {
      virtualmachines { name image }
      secrets { name }
    }
    scripts { action host }
  }
}
''')
t = res['data']['track']
vms = [v['name'] for v in (t['config']['virtualmachines'] or [])]
secrets = [s['name'] for s in (t['config']['secrets'] or [])]
scripts = [f"{s['action']}:{s['host']}" for s in (t['scripts'] or [])]
print('sandboxConfig:', t['sandboxConfig'])
print('vms:', vms)
print('secrets:', secrets)
print('scripts:', scripts)

ok = True
if t['sandboxConfig'] is not None:
    print('ERROR: custom sandboxConfig is linked; unlink it (it can wipe VMs / skip track setup).')
    print('  GraphQL: setTrackSandboxConfigVersion(trackID:"kz0navpyrwlk", configVersionID:null)')
    print('  then: instruqt track push --force')
    ok = False
if 'es3-api' not in vms:
    print('ERROR: missing es3-api VM in track config — run: instruqt track push --force')
    ok = False
for need in ('ESS_CLOUD_API_KEY', 'LLM_PROXY_PROD'):
    if need not in secrets:
        print(f'ERROR: missing secret {need} in track config — check config.yml secrets: then push')
        ok = False
if 'setup:es3-api' not in scripts:
    print('ERROR: missing track setup script')
    ok = False
if not ok:
    sys.exit(1)
print('✅ Track config OK: es3-api VM + secrets + setup script (no custom sandboxConfig).')
PY

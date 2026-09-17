#!/bin/bash
# Re-applies the Instruqt sandbox secrets after a track push.
# Instruqt track push does not preserve the sandbox config — run this after every push.
#
# Usage: ./apply-secrets.sh
#
# Sandbox config ID: cxf0faaupiu4 (DB Monitoring Serverless secrets)
# Track ID: kz0navpyrwlk

set -euo pipefail

TOKEN=$(python3 -c "import json; d=json.load(open('$HOME/.config/instruqt/credentials')); print(d['access_token'])")
PARENT_CONFIG_ID="cxf0faaupiu4"
TRACK_ID="kz0navpyrwlk"

echo "Updating sandbox config with ESS_CLOUD_API_KEY + LLM_PROXY_PROD..."

UPDATE=$(curl -sf -X POST https://play.instruqt.com/graphql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation UpdateSandboxConfig($configID: String!, $config: SandboxConfigInput!) { updateSandboxConfig(configID: $configID, config: $config) { id version status } }",
    "variables": {
      "configID": "'"$PARENT_CONFIG_ID"'",
      "config": {
        "description": "ESS_CLOUD_API_KEY + LLM_PROXY_PROD for serverless-db-monitoring",
        "resources": {
          "secrets": [
            { "name": "ESS_CLOUD_API_KEY" },
            { "name": "LLM_PROXY_PROD" }
          ]
        }
      }
    }
  }')
echo "$UPDATE" | python3 -m json.tool 2>/dev/null

NEW_VERSION_ID=$(echo "$UPDATE" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['updateSandboxConfig']['id'])" 2>/dev/null)
echo "New version ID: $NEW_VERSION_ID"

echo "Publishing..."
PUB=$(curl -sf -X POST https://play.instruqt.com/graphql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { publishSandboxConfig(configID: \\\"$PARENT_CONFIG_ID\\\", changeLogEntry: \\\"Re-apply secrets after track push\\\") { id version status } }\"}")
echo "$PUB" | python3 -m json.tool 2>/dev/null

PUB_VERSION_ID=$(echo "$PUB" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['data']['publishSandboxConfig']['id'])" 2>/dev/null)
echo "Published version ID: $PUB_VERSION_ID"

echo "Linking to track..."
curl -sf -X POST https://play.instruqt.com/graphql \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"mutation { setTrackSandboxConfigVersion(trackID: \\\"$TRACK_ID\\\", configVersionID: \\\"$PUB_VERSION_ID\\\") }\"}" \
  | python3 -m json.tool 2>/dev/null

echo "✅ Secrets applied and sandbox config linked to track."

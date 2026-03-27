#!/bin/bash
# link-secrets.sh
# Re-links org-level secrets (ESS_CLOUD_API_KEY, LLM_PROXY_PROD) to the
# serverless-db-monitoring track via the Instruqt GraphQL API.
# Run this after every `instruqt track push` to prevent secrets being wiped.

set -euo pipefail

TRACK_ID="kz0navpyrwlk"
CREDS_FILE="${HOME}/.config/instruqt/credentials"

if [ ! -f "$CREDS_FILE" ]; then
  echo "ERROR: Instruqt credentials not found at ${CREDS_FILE}. Run: instruqt auth login" >&2
  exit 1
fi

REFRESH_TOKEN=$(python3 -c "import json; d=json.load(open('${CREDS_FILE}')); print(d['refresh_token'])")
API_KEY=$(python3 -c "import json; d=json.load(open('${CREDS_FILE}')); print(d['api_key'])")

echo "Refreshing Instruqt auth token…"
ACCESS_TOKEN=$(curl -s -X POST \
  "https://securetoken.googleapis.com/v1/token?key=${API_KEY}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=${REFRESH_TOKEN}" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['access_token'])")

echo "Linking ESS_CLOUD_API_KEY + LLM_PROXY_PROD to track ${TRACK_ID}…"
RESULT=$(curl -s -X POST https://play.instruqt.com/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -d "{
    \"query\": \"mutation UpdateTrack(\$track: TrackInput!) { updateCompleteTrack(track: \$track) { id title } }\",
    \"variables\": {
      \"track\": {
        \"id\": \"${TRACK_ID}\",
        \"slug\": \"serverless-db-monitoring\",
        \"owner\": \"elastic\",
        \"title\": \"Elastic Database Monitoring \u2014 MySQL \u00b7 PostgreSQL \u00b7 SQL Server \u00b7 MongoDB\",
        \"config\": {
          \"secrets\": [
            {\"name\": \"ESS_CLOUD_API_KEY\"},
            {\"name\": \"LLM_PROXY_PROD\"}
          ]
        }
      }
    }
  }")

if echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); exit(0 if d.get('data',{}).get('updateCompleteTrack') else 1)" 2>/dev/null; then
  echo "✓ Secrets linked successfully."
else
  echo "ERROR: Failed to link secrets." >&2
  echo "$RESULT" | python3 -m json.tool >&2
  exit 1
fi

#!/bin/bash
# push.sh — Push the Instruqt track.
# The $ESS_CLOUD_API_KEY and $LLM_PROXY_PROD entries in config.yml are
# sufficient for Instruqt to link the org secrets automatically on push.
# Do NOT call updateCompleteTrack after this — it overwrites the full track.
#
# Usage: ./scripts/push.sh

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Pushing Instruqt track ==="
cd "$REPO_ROOT/serverless-db-monitoring"
instruqt track push --force

echo ""
echo "Done. Track: https://play.instruqt.com/manage/elastic/tracks/serverless-db-monitoring"

#!/bin/bash
# push.sh — Push the Instruqt track.
# NOTE: No --force flag. Using --force resets the sandbox config and wipes
# secrets, hosts, and other UI settings configured in the Instruqt dashboard.
#
# Usage: ./scripts/push.sh

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Pushing Instruqt track ==="
cd "$REPO_ROOT/serverless-db-monitoring"
instruqt track push

echo ""
echo "Done. Track: https://play.instruqt.com/manage/elastic/tracks/serverless-db-monitoring"

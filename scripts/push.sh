#!/bin/bash
# push.sh — Push the Instruqt track and re-link secrets in one step.
# Usage: ./scripts/push.sh

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Pushing Instruqt track ==="
cd "$REPO_ROOT/serverless-db-monitoring"
instruqt track push --force

echo ""
echo "=== Re-linking org secrets (prevents push from wiping them) ==="
"$REPO_ROOT/scripts/link-secrets.sh"

echo ""
echo "Done. Track: https://play.instruqt.com/manage/elastic/tracks/serverless-db-monitoring"

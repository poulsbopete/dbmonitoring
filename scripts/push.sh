#!/bin/bash
# push.sh — Sync and push the Instruqt track.
# Pulls remote state first to avoid conflicts, then pushes local changes.
# Does NOT use --force so sandbox config (secrets, hosts) is preserved.
#
# Usage: ./scripts/push.sh

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TRACK_DIR="$REPO_ROOT/serverless-db-monitoring"

echo "=== Pulling remote track state ==="
cd "$TRACK_DIR"
instruqt track pull --force

echo ""
echo "=== Restoring local changes from git ==="
git -C "$REPO_ROOT" checkout -- "$TRACK_DIR"

echo ""
echo "=== Pushing Instruqt track ==="
instruqt track push

echo ""
echo "Done. Track: https://play.instruqt.com/manage/elastic/tracks/serverless-db-monitoring"

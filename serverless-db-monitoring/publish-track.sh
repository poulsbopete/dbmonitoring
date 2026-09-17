#!/usr/bin/env bash
# Push current Git branch to origin, then upload track metadata to Instruqt.
# Run from anywhere; commit your changes first.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "==> git push origin $BRANCH"
git push origin "$BRANCH"
echo "==> instruqt track push"
cd serverless-db-monitoring
instruqt track push
echo "==> re-apply sandbox secrets (track push drops sandboxConfig)"
./apply-secrets.sh
echo "OK: Git + Instruqt + secrets updated."

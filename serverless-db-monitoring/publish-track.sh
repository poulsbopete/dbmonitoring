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
echo "OK: Git + Instruqt updated."

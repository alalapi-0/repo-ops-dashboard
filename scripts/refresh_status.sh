#!/usr/bin/env bash
# Refresh repo status, dashboard, reports, and optional UI check.
# Usage: ./scripts/refresh_status.sh [--example] [--ui-check]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

USE_EXAMPLE=false
UI_CHECK=false
for arg in "$@"; do
  case "$arg" in
    --example) USE_EXAMPLE=true ;;
    --ui-check) UI_CHECK=true ;;
  esac
done

PYTHON="${PYTHON:-python3}"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
fi

echo "[refresh] agent_gate"
"$PYTHON" scripts/agent_gate.py

if $USE_EXAMPLE; then
  CONFIG="config/repos.example.yaml"
  SNAPSHOTS="data/repo_snapshots.example.json"
  STATUS="data/repo_status.example.json"
  echo "[refresh] scan (example dry-run)"
  "$PYTHON" scripts/scan_repos.py --config "$CONFIG" --dry-run
else
  CONFIG="config/repos.yaml"
  SNAPSHOTS="data/repo_snapshots.json"
  STATUS="data/repo_status.json"
  echo "[refresh] scan (live)"
  "$PYTHON" scripts/scan_repos.py --config "$CONFIG" --no-dry-run
fi

echo "[refresh] analyze"
"$PYTHON" scripts/analyze_repos.py --input "$SNAPSHOTS" --output "$STATUS"

echo "[refresh] priority review"
if $USE_EXAMPLE; then
  "$PYTHON" scripts/priority_review.py \
    --input "$STATUS" \
    --repos-config config/repos.example.yaml \
    --output-board data/priority_board.example.run.json \
    --output-report reports/priority_review.example.md
  PRIORITY_BOARD="data/priority_board.example.run.json"
else
  "$PYTHON" scripts/priority_review.py --input "$STATUS"
  PRIORITY_BOARD="data/priority_board.json"
fi

echo "[refresh] dashboard"
"$PYTHON" scripts/generate_dashboard.py --input "$STATUS" --output dashboard/index.html --priority-board "$PRIORITY_BOARD"

echo "[refresh] reports"
"$PYTHON" scripts/generate_report.py --input "$STATUS"

echo "[refresh] feishu preview"
"$PYTHON" scripts/prepare_feishu_payload.py

echo "[refresh] protocol sync suggestions"
"$PYTHON" scripts/protocol_sync_report.py --input "$SNAPSHOTS" --no-dry-run

echo "[refresh] openclaw brief"
"$PYTHON" scripts/generate_openclaw_brief.py --input "$STATUS"

if $UI_CHECK; then
  echo "[refresh] ui_check"
  "$PYTHON" scripts/ui_check.py \
    --file dashboard/index.html \
    --screenshot reports/ui_screenshots/dashboard.png \
    --headless true
fi

echo "[refresh] done -> $STATUS"

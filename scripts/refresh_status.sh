#!/usr/bin/env bash
# Refresh repo status, dashboard, reports, and optional UI check.
# Usage: ./scripts/refresh_status.sh [--example] [--ui-check] [--feishu-send] [--bitable-sync] [--llm-summary] [--generation-pipeline] [--call]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

USE_EXAMPLE=false
UI_CHECK=false
FEISHU_SEND=false
BITABLE_SYNC=false
LLM_SUMMARY=false
GEN_PIPELINE=false
LLM_CALL=false
for arg in "$@"; do
  case "$arg" in
    --example) USE_EXAMPLE=true ;;
    --ui-check) UI_CHECK=true ;;
    --feishu-send) FEISHU_SEND=true ;;
    --bitable-sync) BITABLE_SYNC=true ;;
    --llm-summary) LLM_SUMMARY=true ;;
    --generation-pipeline) GEN_PIPELINE=true ;;
    --call) LLM_CALL=true ;;
  esac
done

if [[ -f "$ROOT/.env" ]] && { $FEISHU_SEND || $BITABLE_SYNC || $LLM_CALL || $GEN_PIPELINE; }; then
  _PRESERVE_LLM="${LLM_ENABLED:-}"
  set -a
  # shellcheck disable=SC1091
  source "$ROOT/.env"
  set +a
  if [[ "$_PRESERVE_LLM" == "true" ]]; then
    export LLM_ENABLED=true
  fi
fi

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
  PRIORITY_REPORT="reports/priority_review.example.md"
  WEEKLY_REVIEW="reports/weekly_review.example.md"
  HUMAN_NOTES="data/human_notes.example.json"
else
  "$PYTHON" scripts/priority_review.py --input "$STATUS"
  PRIORITY_BOARD="data/priority_board.json"
  PRIORITY_REPORT="reports/priority_review.md"
  WEEKLY_REVIEW="reports/weekly_review.md"
  HUMAN_NOTES="data/human_notes.json"
fi

echo "[refresh] reports"
"$PYTHON" scripts/generate_report.py --input "$STATUS"

echo "[refresh] protocol sync suggestions"
"$PYTHON" scripts/protocol_sync_report.py --input "$SNAPSHOTS" --no-dry-run

echo "[refresh] sync portfolio state"
"$PYTHON" scripts/sync_portfolio_state.py --status "$STATUS"

echo "[refresh] portfolio checkpoint snapshot (dry-run)"
"$PYTHON" scripts/snapshot_portfolio_checkpoint.py

echo "[refresh] sync governance task queue"
"$PYTHON" scripts/sync_governance_task_queue.py

echo "[refresh] daily brief"
"$PYTHON" scripts/generate_daily_brief.py --input "$STATUS"

echo "[refresh] daily briefing (governance digest)"
"$PYTHON" scripts/generate_daily_briefing.py --input "$STATUS"

echo "[refresh] openclaw orchestration bridge"
"$PYTHON" scripts/openclaw_orchestration_bridge.py

echo "[refresh] eval registry (dry-run)"
"$PYTHON" scripts/run_eval_registry.py --required-only

echo "[refresh] handoff packet (dry-run)"
"$PYTHON" scripts/generate_handoff_packet.py --task-spec governance/task_specs/example_task_spec.yaml

echo "[refresh] failure recovery plan (dry-run)"
"$PYTHON" scripts/failure_recovery.py --task-id task_example --failure-class validation_failed --retry-count 1

if $LLM_SUMMARY; then
  echo "[refresh] llm summary"
  if $LLM_CALL; then
    if [[ "${LLM_ENABLED:-false}" != "true" ]]; then
      echo "[warn] LLM_ENABLED is not true; skipping --call"
    else
      "$PYTHON" scripts/generate_llm_summary.py --input "$STATUS" --call
    fi
  else
    "$PYTHON" scripts/generate_llm_summary.py --input "$STATUS"
  fi
fi

if $GEN_PIPELINE; then
  echo "[refresh] generation pipeline"
  PIPE_ARGS=(--input "$STATUS" --round "refresh_$(date +%Y%m%d)")
  if $LLM_CALL; then
    if [[ "${LLM_ENABLED:-false}" != "true" ]]; then
      echo "[warn] LLM_ENABLED is not true; skipping pipeline --call"
    else
      PIPE_ARGS+=(--call --auto-approve --review-mode auto --skip-human-review)
      "$PYTHON" scripts/run_generation_pipeline.py "${PIPE_ARGS[@]}"
      "$PYTHON" scripts/generate_generations_page.py
    fi
  else
    "$PYTHON" scripts/run_generation_pipeline.py --dry-run "${PIPE_ARGS[@]}"
  fi
fi

echo "[refresh] weekly review merge"
"$PYTHON" scripts/generate_weekly_review.py \
  --priority-report "$PRIORITY_REPORT" \
  --human-notes "$HUMAN_NOTES" \
  --output "$WEEKLY_REVIEW"

echo "[refresh] weekly digest"
"$PYTHON" scripts/generate_weekly_digest.py --input "$STATUS" --human-notes "$HUMAN_NOTES"

echo "[refresh] cursor task_spec prompt"
"$PYTHON" scripts/generate_cursor_prompt_from_task_spec.py \
  --task-spec governance/task_specs/example_task_spec.yaml \
  --dry-run

echo "[refresh] codex task_spec prompt"
"$PYTHON" scripts/generate_codex_prompt_from_task_spec.py \
  --task-spec governance/task_specs/example_codex_task_spec.yaml \
  --dry-run

echo "[refresh] dashboard"
"$PYTHON" scripts/generate_dashboard.py \
  --input "$STATUS" \
  --output dashboard/index.html \
  --priority-board "$PRIORITY_BOARD" \
  --human-notes "$HUMAN_NOTES"

echo "[refresh] feishu preview"
if $FEISHU_SEND; then
  "$PYTHON" scripts/prepare_feishu_payload.py --status "$STATUS" --send
else
  "$PYTHON" scripts/prepare_feishu_payload.py --status "$STATUS"
fi

if $BITABLE_SYNC; then
  echo "[refresh] feishu bitable sync"
  "$PYTHON" scripts/sync_feishu_bitable.py --input "$STATUS" --sync
fi

if $UI_CHECK; then
  echo "[refresh] ui_check"
  "$PYTHON" scripts/ui_check.py \
    --file dashboard/index.html \
    --screenshot reports/ui_screenshots/dashboard.png \
    --headless true
fi

echo "[refresh] done -> $STATUS"

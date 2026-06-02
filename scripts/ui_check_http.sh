#!/usr/bin/env bash
# Start local HTTP server, run ui_check against http://127.0.0.1:8765/dashboard/, then stop server.
# Usage: ./scripts/ui_check_http.sh [--port 8765]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PORT=8765
for arg in "$@"; do
  case "$arg" in
    --port=*) PORT="${arg#*=}" ;;
    --port) shift; PORT="${1:-8765}" ;;
  esac
done

PYTHON="${PYTHON:-python3}"
if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
fi

if [[ ! -f "$ROOT/dashboard/index.html" ]]; then
  echo "[error] dashboard/index.html not found; run generate_dashboard first" >&2
  exit 1
fi

echo "[ui_check_http] starting http.server on 127.0.0.1:${PORT}"
"$PYTHON" -m http.server "$PORT" --bind 127.0.0.1 &
SERVER_PID=$!

cleanup() {
  if kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

sleep 1
PAGE_URL="http://127.0.0.1:${PORT}/dashboard/"
echo "[ui_check_http] checking ${PAGE_URL}"

"$PYTHON" scripts/ui_check.py \
  --url "$PAGE_URL" \
  --file dashboard/index.html \
  --screenshot reports/ui_screenshots/dashboard_http.png \
  --headless true \
  --report reports/ui_check_http_report.md

echo "[ui_check_http] done"

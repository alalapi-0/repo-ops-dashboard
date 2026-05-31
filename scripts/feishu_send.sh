#!/usr/bin/env bash
# Load gitignored .env then run prepare_feishu_payload (preview or --send).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if [[ -f "${ROOT}/.env" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${ROOT}/.env"
  set +a
fi
cd "${ROOT}"
exec python3 scripts/prepare_feishu_payload.py "$@"

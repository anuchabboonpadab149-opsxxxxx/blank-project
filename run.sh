#!/usr/bin/env bash
set -euo pipefail

# Load env if present
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs -d '\\n' -0 echo 2>/dev/null || true)
  set +a
fi

# Default to daemon + interval for 24/7
MODE="${RUN_MODE:-daemon}"
INTERVAL="${INTERVAL_SECONDS:-1800}"
TZONE="${TIMEZONE:-Asia/Bangkok}"

if [ "$MODE" = "daemon" ]; then
  echo "Starting daemon: every ${INTERVAL}s timezone ${TZONE}"
  exec python3 cli.py --mode daemon --interval "${INTERVAL}" --tz "${TZONE}"
else
  echo "Starting once"
  exec python3 cli.py --mode once
fi
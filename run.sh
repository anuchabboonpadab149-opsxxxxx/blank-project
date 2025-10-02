#!/usr/bin/env bash
set -euo pipefail

# Load env if present
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs -d '\n' -0 echo 2>/dev/null || true)
  set +a
fi

MODE="${RUN_MODE:-daemon}"
INTERVAL="${INTERVAL_SECONDS:-}"
CRON="${CRON_SPEC:-}"
TZONE="${TIMEZONE:-Asia/Bangkok}"

if [ "$MODE" = "daemon" ]; then
  echo "Starting daemon. Interval='${INTERVAL:-none}' Cron='${CRON:-none}' TZ='${TZONE}'"
  ARGS=(cli.py --mode daemon --tz "${TZONE}")
  if [ -n "${INTERVAL}" ]; then
    ARGS+=("--interval" "${INTERVAL}")
  fi
  if [ -n "${CRON}" ]; then
    ARGS+=("--cron" "${CRON}")
  fi
  exec python3 "${ARGS[@]}"
else
  echo "Starting once"
  exec python3 cli.py --mode once
fi
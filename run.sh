#!/usr/bin/env bash
set -euo pipefail

# python-dotenv will load .env inside the Python apps; no need to parse here.

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
#!/usr/bin/env bash
set -euo pipefail

# python-dotenv will load .env inside the Python apps; no need to parse here.

MODE="${RUN_MODE:-daemon}"
TZONE="${TIMEZONE:-Asia/Bangkok}"

if [ "$MODE" = "daemon" ]; then
  echo "Starting daemon (env-driven). TZ='${TZONE}'"
  exec python3 cli.py --mode daemon --tz "${TZONE}"
else
  echo "Starting once"
  exec python3 cli.py --mode once
fi
  if [ -n "${POST_CRON_SPEC}" ]; then
    ARGS+=("--post-cron" "${POST_CRON_SPEC}")
  fi
  if [ -n "${COLLECT_INTERVAL_MIN}" ]; then
    ARGS+=("--collect-interval-min" "${COLLECT_INTERVAL_MIN}")
  fi
  if [ -n "${COLLECT_CRON_SPEC}" ]; then
    ARGS+=("--collect-cron" "${COLLECT_CRON_SPEC}")
  fi
  exec python3 "${ARGS[@]}"
else
  echo "Starting once"
  exec python3 cli.py --mode once
fi
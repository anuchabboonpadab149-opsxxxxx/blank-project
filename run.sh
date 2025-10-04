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
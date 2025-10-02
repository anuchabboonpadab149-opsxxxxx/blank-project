import os
import sys
import argparse
import logging
import threading

from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

from promote_ayutthaya import Config, run_once

log = logging.getLogger("promote_cli")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Promote a Tweet to Ayutthaya via X Ads API")
    parser.add_argument("--mode", choices=["once", "daemon"], help="Run once or daemon (scheduled). Overrides RUN_MODE env.", default=None)
    parser.add_argument("--cron", help="Cron spec for daemon mode. Supports 5 fields 'm h dom mon dow' or 6 fields 's m h dom mon dow'. Overrides CRON_SPEC env.", default=None)
    parser.add_argument("--interval", type=int, help="Interval seconds for daemon mode, e.g. 1 for every second. Overrides INTERVAL_SECONDS env.", default=None)
    parser.add_argument("--tz", help="Timezone ID, e.g. 'Asia/Bangkok'. Overrides TIMEZONE env.", default=None)
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    mode = args.mode or os.getenv("RUN_MODE", "once").strip()
    cron_spec = (args.cron or os.getenv("CRON_SPEC", "")).strip()
    interval_seconds_env = os.getenv("INTERVAL_SECONDS", "").strip()
    interval_seconds = args.interval if args.interval is not None else (int(interval_seconds_env) if interval_seconds_env.isdigit() else None)
    tz = args.tz or os.getenv("TIMEZONE", "Asia/Bangkok")

    if mode == "once":
        cfg = Config()
        res = run_once(cfg)
        log.info(f"Completed one-shot promotion: {res}")
        return

    # daemon mode
    scheduler = BlockingScheduler(timezone=pytz.timezone(tz))
    run_lock = threading.Lock()

    def job():
        if not run_lock.acquire(blocking=False):
            log.info("Previous job still running; skipping this tick.")
            return
        try:
            cfg = Config()
            res = run_once(cfg)
            log.info(f"Promotion job result: {res}")
        except Exception as e:
            log.error(f"Promotion job failed: {e}", exc_info=True)
        finally:
            run_lock.release()

    added = 0

    # Interval trigger (supports per-second)
    if interval_seconds and interval_seconds > 0:
        log.info(f"Adding interval trigger: every {interval_seconds}s tz='{tz}'")
        scheduler.add_job(job, IntervalTrigger(seconds=interval_seconds, timezone=pytz.timezone(tz)),
                          id="promote_interval", replace_existing=True, max_instances=1, coalesce=True)
        added += 1

    # Cron trigger (supports 5 or 6 fields incl. seconds)
    if cron_spec:
        fields = cron_spec.split()
        tzinfo = pytz.timezone(tz)
        if len(fields) == 6:
            second, minute, hour, day, month, dow = fields
            trigger = CronTrigger(second=second, minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tzinfo)
        elif len(fields) == 5:
            minute, hour, day, month, dow = fields
            trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tzinfo)
        else:
            log.error("CRON_SPEC must have 5 fields ('m h dom mon dow') or 6 fields ('s m h dom mon dow').")
            sys.exit(1)

        log.info(f"Adding cron trigger: cron='{cron_spec}' tz='{tz}'")
        scheduler.add_job(job, trigger, id="promote_cron", replace_existing=True, max_instances=1, coalesce=True)
        added += 1

    # Default if neither specified: run every 1 second
    if added == 0:
        log.info("No interval or cron provided; defaulting to every 1 second.")
        scheduler.add_job(job, IntervalTrigger(seconds=1, timezone=pytz.timezone(tz)),
                          id="promote_default", replace_existing=True, max_instances=1, coalesce=True)

    log.info("Scheduler started; press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
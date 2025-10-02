import os
import sys
import argparse
import logging

from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from promote_ayutthaya import Config, run_once

log = logging.getLogger("promote_cli")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Promote a Tweet to Ayutthaya via X Ads API")
    parser.add_argument("--mode", choices=["once", "daemon"], help="Run once or daemon (scheduled). Overrides RUN_MODE env.", default=None)
    parser.add_argument("--cron", help="Cron spec for daemon mode, e.g. '0 9 * * *'. Overrides CRON_SPEC env.", default=None)
    parser.add_argument("--tz", help="Timezone ID, e.g. 'Asia/Bangkok'. Overrides TIMEZONE env.", default=None)
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    mode = args.mode or os.getenv("RUN_MODE", "once").strip()
    cron_spec = args.cron or os.getenv("CRON_SPEC", "0 9 * * *")
    tz = args.tz or os.getenv("TIMEZONE", "Asia/Bangkok")

    if mode == "once":
        cfg = Config()
        res = run_once(cfg)
        log.info(f"Completed one-shot promotion: {res}")
        return

    # daemon mode
    log.info(f"Starting daemon scheduler: cron='{cron_spec}' tz='{tz}'")
    scheduler = BlockingScheduler(timezone=pytz.timezone(tz))

    def job():
        try:
            cfg = Config()
            res = run_once(cfg)
            log.info(f"Promotion job result: {res}")
        except Exception as e:
            log.error(f"Promotion job failed: {e}", exc_info=True)

    # Parse 5-field cron spec
    fields = cron_spec.split()
    if len(fields) != 5:
        log.error("CRON_SPEC must have 5 fields like '0 9 * * *'")
        sys.exit(1)

    minute, hour, day, month, dow = fields
    trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=pytz.timezone(tz))
    scheduler.add_job(job, trigger, id="promote_ayutthaya_job", replace_existing=True)
    log.info("Scheduler started; press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
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

from promote_ayutthaya import Config, post_one_from_file, collect_metrics, collect_ads_analytics

log = logging.getLogger("promote_cli")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Promote a Tweet to Ayutthaya via X Ads API")
    parser.add_argument("--mode", choices=["once", "daemon"], help="Run once or daemon (scheduled). Overrides RUN_MODE env.", default=None)
    # Posting triggers
    parser.add_argument("--post-cron", help="Cron for posting (5 or 6 fields). Overrides POST_CRON env.", default=None)
    parser.add_argument("--post-interval", type=int, help="Interval seconds for posting. Overrides POST_INTERVAL_SECONDS env.", default=None)
    # Collecting triggers
    parser.add_argument("--collect-cron", help="Cron for collecting metrics (5 or 6 fields). Overrides COLLECT_CRON env.", default=None)
    parser.add_argument("--collect-interval-min", type=int, help="Interval minutes for collecting metrics. Overrides COLLECT_INTERVAL_MINUTES env.", default=None)
    parser.add_argument("--tz", help="Timezone ID, e.g. 'Asia/Bangkok'. Overrides TIMEZONE env.", default=None)
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    mode = args.mode or os.getenv("RUN_MODE", "once").strip()
    tz = args.tz or os.getenv("TIMEZONE", "Asia/Bangkok")

    # Posting trigger env
    post_cron = (args.post_cron or os.getenv("POST_CRON", "")).strip()
    post_interval_env = os.getenv("POST_INTERVAL_SECONDS", "").strip()
    post_interval = args.post_interval if args.post_interval is not None else (int(post_interval_env) if post_interval_env.isdigit() else None)

    # Collecting trigger env
    collect_cron = (args.collect_cron or os.getenv("COLLECT_CRON", "")).strip()
    collect_interval_min_env = os.getenv("COLLECT_INTERVAL_MINUTES", "").strip()
    collect_interval_min = args.collect_interval_min if args.collect_interval_min is not None else (int(collect_interval_min_env) if collect_interval_min_env.isdigit() else None)

    if mode == "once":
        cfg = Config()
        res = post_one_from_file(cfg)
        log.info(f"Posted and promoted: {res}")
        met = collect_metrics(cfg)
        log.info(f"Collected organic metrics: {met}")
        ads = collect_ads_analytics(cfg)
        log.info(f"Collected ads analytics: {ads}")
        return

    scheduler = BlockingScheduler(timezone=pytz.timezone(tz))

    post_lock = threading.Lock()
    collect_lock = threading.Lock()

    def post_job():
        if not post_lock.acquire(blocking=False):
            log.info("Post job already running; skipping.")
            return
        try:
            cfg = Config()
            res = post_one_from_file(cfg)
            log.info(f"Post job result: {res}")
        except Exception as e:
            log.error(f"Post job failed: {e}", exc_info=True)
        finally:
            post_lock.release()

    def collect_job():
        if not collect_lock.acquire(blocking=False):
            log.info("Collect job already running; skipping.")
            return
        try:
            cfg = Config()
            met = collect_metrics(cfg)
            log.info(f"Collect organic metrics result: {met}")
            ads = collect_ads_analytics(cfg)
            log.info(f"Collect ads analytics result: {ads}")
        except Exception as e:
            log.error(f"Collect job failed: {e}", exc_info=True)
        finally:
            collect_lock.release()

    tzinfo = pytz.timezone(tz)

    added = 0

    # Posting triggers
    if post_interval and post_interval > 0:
        log.info(f"Adding posting interval every {post_interval}s")
        scheduler.add_job(post_job, IntervalTrigger(seconds=post_interval, timezone=tzinfo),
                          id="post_interval", replace_existing=True, max_instances=1, coalesce=True)
        added += 1
    if post_cron:
        fields = post_cron.split()
        if len(fields) == 6:
            second, minute, hour, day, month, dow = fields
            trigger = CronTrigger(second=second, minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tzinfo)
        elif len(fields) == 5:
            minute, hour, day, month, dow = fields
            trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tzinfo)
        else:
            log.error("POST_CRON must have 5 or 6 fields.")
            sys.exit(1)
        log.info(f"Adding posting cron: '{post_cron}'")
        scheduler.add_job(post_job, trigger, id="post_cron", replace_existing=True, max_instances=1, coalesce=True)
        added += 1

    # Collecting triggers
    if collect_interval_min and collect_interval_min > 0:
        log.info(f"Adding collect interval every {collect_interval_min} minutes")
        scheduler.add_job(collect_job, IntervalTrigger(minutes=collect_interval_min, timezone=tzinfo),
                          id="collect_interval", replace_existing=True, max_instances=1, coalesce=True)
    if collect_cron:
        fields = collect_cron.split()
        if len(fields) == 6:
            second, minute, hour, day, month, dow = fields
            trigger = CronTrigger(second=second, minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tzinfo)
        elif len(fields) == 5:
            minute, hour, day, month, dow = fields
            trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=tzinfo)
        else:
            log.error("COLLECT_CRON must have 5 or 6 fields.")
            sys.exit(1)
        log.info(f"Adding collect cron: '{collect_cron}'")
        scheduler.add_job(collect_job, trigger, id="collect_cron", replace_existing=True, max_instances=1, coalesce=True)

    if added == 0:
        # sensible defaults: post every 1 second; collect every 1 minute
        log.info("No posting trigger specified; defaulting to every 1 second.")
        scheduler.add_job(post_job, IntervalTrigger(seconds=1, timezone=tzinfo),
                          id="post_default", replace_existing=True, max_instances=1, coalesce=True)
        log.info("No collect trigger specified; defaulting to every 1 minute.")
        scheduler.add_job(collect_job, IntervalTrigger(minutes=1, timezone=tzinfo),
                          id="collect_default", replace_existing=True, max_instances=1, coalesce=True)

    log.info("Scheduler started; press Ctrl+C to stop.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
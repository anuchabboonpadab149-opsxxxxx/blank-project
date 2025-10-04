import os
import sys
import argparse
import logging
import threading

from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

from promote_ayutthaya import Config, post_one_from_file, collect_metrics, collect_ads_analytics
from social_dispatcher import distribute_once

log = logging.getLogger("promote_cli")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Distribute posts to multiple social platforms and collect metrics")
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
    distribute_all = os.getenv("DISTRIBUTE_ALL", "true").lower() in {"1", "true", "yes"}
    web_enabled = os.getenv("WEB_DASHBOARD", "true").lower() in {"1", "true", "yes"}

    # Posting trigger env
    post_cron = (args.post_cron or os.getenv("POST_CRON", "")).strip()
    post_interval_env = os.getenv("POST_INTERVAL_SECONDS", "").strip()
    post_interval = args.post_interval if args.post_interval is not None else (int(post_interval_env) if post_interval_env.isdigit() else None)

    # Collecting trigger env
    collect_cron = (args.collect_cron or os.getenv("COLLECT_CRON", "")).strip()
    collect_interval_min_env = os.getenv("COLLECT_INTERVAL_MINUTES", "").strip()
    collect_interval_min = args.collect_interval_min if args.collect_interval_min is not None else (int(collect_interval_min_env) if collect_interval_min_env.isdigit() else None)

    # Runtime overrides via config_store
    try:
        import config_store
        post_int_override = config_store.get("post_interval_seconds")
        if isinstance(post_int_override, int) and post_int_override > 0:
            post_interval = post_int_override
            post_cron = ""
        collect_int_override = config_store.get("collect_interval_minutes")
        if isinstance(collect_int_override, int) and collect_int_override > 0:
            collect_interval_min = collect_int_override
            collect_cron = ""
    except Exception:
        pass

    if mode == "once":
        text_for_event = None
        post_result = None
        try:
            if distribute_all:
                post_result = distribute_once()
                text_for_event = post_result.get("text")
                log.info(f"Distributed to providers: {post_result}")
            else:
                cfg = Config()
                post_result = post_one_from_file(cfg)
                text_for_event = post_result.get("text")
                log.info(f"Posted and promoted on Twitter: {post_result}")
        except Exception as e:
            log.error(f"Post once failed: {e}", exc_info=True)
        try:
            from content_generator import generate_caption
            from media_generator import generate_all
            import realtime_bus as bus
            # Prefer runtime sender/tts config
            sender_name = None
            tts_lang = "th"
            try:
                import config_store
                sender_name = config_store.get("sender_name")
                tts_lang = config_store.get("tts_lang", "th")
            except Exception:
                pass
            if not text_for_event:
                cfg2 = Config()
                text_for_event = generate_caption(sender_name=sender_name or cfg2.SENDER_NAME)
            media = generate_all(text_for_event, sender=(sender_name or ""), tts_lang=tts_lang)
            bus.publish({"type": "post", "text": text_for_event, "providers": (post_result or {}).get("providers"), "twitter_detail": (post_result or {}).get("twitter_detail"), "media": media})
        except Exception as e:
            log.error(f"Media generation/event publish failed: {e}", exc_info=True)

        cfg = Config()
        met = collect_metrics(cfg)
        log.info(f"Collected organic metrics: {met}")
        ads = collect_ads_analytics(cfg)
        log.info(f"Collected ads analytics: {ads}")
        try:
            import realtime_bus as bus
            bus.publish({"type": "collect", "organic_count": met.get("count", 0), "ads_status": ads.get("status", str(ads))})
        except Exception:
            pass
        return

    SchedulerCls = BackgroundScheduler if web_enabled else BlockingScheduler
    scheduler = SchedulerCls(timezone=pytz.timezone(tz))

    post_lock = threading.Lock()
    collect_lock = threading.Lock()

    def post_job():
        if not post_lock.acquire(blocking=False):
            log.info("Post job already running; skipping.")
            return
        try:
            text_for_event = None
            result = None
            if distribute_all:
                try:
                    result = distribute_once()
                    text_for_event = (result or {}).get("text")
                    log.info(f"Post job distributed: {result}")
                except Exception as e:
                    log.error(f"Post job distribute failed: {e}", exc_info=True)
            else:
                try:
                    cfg_local = Config()
                    result = post_one_from_file(cfg_local)
                    text_for_event = (result or {}).get("text")
                    log.info(f"Post job (Twitter only) result: {result}")
                except Exception as e:
                    log.error(f"Post job (Twitter) failed: {e}", exc_info=True)

            if not text_for_event:
                try:
                    from content_generator import generate_caption
                    sender_name = None
                    try:
                        import config_store
                        sender_name = config_store.get("sender_name")
                    except Exception:
                        pass
                    cfg_local2 = Config()
                    text_for_event = generate_caption(sender_name=sender_name or cfg_local2.SENDER_NAME)
                except Exception as e:
                    log.error(f"Fallback content generation failed: {e}", exc_info=True)
                    text_for_event = ""

            try:
                from media_generator import generate_all
                import realtime_bus as bus
                sender_name = ""
                tts_lang = "th"
                try:
                    import config_store
                    sender_name = config_store.get("sender_name") or ""
                    tts_lang = config_store.get("tts_lang", "th")
                except Exception:
                    pass
                media = generate_all(text_for_event, sender=sender_name, tts_lang=tts_lang)
                bus.publish({"type": "post", "text": text_for_event, "providers": (result or {}).get("providers"), "twitter_detail": (result or {}).get("twitter_detail"), "media": media})
            except Exception as e:
                log.error(f"Media generation or event publish failed: {e}", exc_info=True)

        except Exception as e:
            log.error(f"Post job failed: {e}", exc_info=True)
        finally:
            post_lock.release()

    def collect_job():
        if not collect_lock.acquire(blocking=False):
            log.info("Collect job already running; skipping.")
            return
        try:
            cfg_local = Config()
            met = collect_metrics(cfg_local)
            log.info(f"Collect organic metrics result: {met}")
            ads = collect_ads_analytics(cfg_local)
            log.info(f"Collect ads analytics result: {ads}")
            try:
                import realtime_bus as bus
                bus.publish({"type": "collect", "organic_count": met.get("count", 0), "ads_status": ads.get("status", str(ads))})
            except Exception:
                pass
        except Exception as e:
            log.error(f"Collect job failed: {e}", exc_info=True)
        finally:
            collect_lock.release()

    tzinfo = pytz.timezone(tz)

    # Register scheduler and jobs for web control
    try:
        import scheduler_control
        scheduler_control.register_scheduler(scheduler, tzinfo, post_job_fn=post_job, collect_job_fn=collect_job)
    except Exception:
        pass

    added = 0

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
        log.info("No posting trigger specified; defaulting to every 1 second.")
        scheduler.add_job(post_job, IntervalTrigger(seconds=1, timezone=tzinfo),
                          id="post_default", replace_existing=True, max_instances=1, coalesce=True)
        log.info("No collect trigger specified; defaulting to every 1 minute.")
        scheduler.add_job(collect_job, IntervalTrigger(minutes=1, timezone=tzinfo),
                          id="collect_default", replace_existing=True, max_instances=1, coalesce=True)

    if web_enabled:
        log.info("Starting BackgroundScheduler + web dashboard")
        scheduler.start()
        try:
            from web_dashboard import start_web
            start_web()
        except (KeyboardInterrupt, SystemExit):
            log.info("Web server stopped.")
        finally:
            scheduler.shutdown(wait=False)
    else:
        log.info("Scheduler started; press Ctrl+C to stop.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            log.info("Scheduler stopped.")


if __name__ == "__main__":
    main()
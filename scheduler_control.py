import logging
from typing import Optional

from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

log = logging.getLogger("scheduler_control")

_scheduler = None
_tzinfo = None
_post_job_fn = None
_collect_job_fn = None


def register_scheduler(scheduler, tzinfo, post_job_fn=None, collect_job_fn=None):
    global _scheduler, _tzinfo, _post_job_fn, _collect_job_fn
    _scheduler = scheduler
    _tzinfo = tzinfo
    _post_job_fn = post_job_fn
    _collect_job_fn = collect_job_fn


def trigger_post_now() -> bool:
    if _post_job_fn:
        try:
            _post_job_fn()
            return True
        except Exception as e:
            log.error(f"trigger_post_now failed: {e}", exc_info=True)
    return False


def trigger_collect_now() -> bool:
    if _collect_job_fn:
        try:
            _collect_job_fn()
            return True
        except Exception as e:
            log.error(f"trigger_collect_now failed: {e}", exc_info=True)
    return False


def reschedule(post_interval_seconds: Optional[int] = None,
               collect_interval_minutes: Optional[int] = None,
               post_cron: Optional[str] = None,
               collect_cron: Optional[str] = None) -> bool:
    if not _scheduler or not _tzinfo:
        return False
    # Remove existing known jobs
    for jid in ["post_interval", "post_cron", "post_default", "collect_interval", "collect_cron", "collect_default"]:
        try:
            _scheduler.remove_job(jid)
        except Exception:
            pass

    added = 0
    if post_interval_seconds and post_interval_seconds > 0 and _post_job_fn:
        _scheduler.add_job(_post_job_fn, IntervalTrigger(seconds=post_interval_seconds, timezone=_tzinfo),
                           id="post_interval", replace_existing=True, max_instances=1, coalesce=True)
        added += 1
    if post_cron and _post_job_fn:
        fields = post_cron.split()
        if len(fields) == 6:
            second, minute, hour, day, month, dow = fields
            trigger = CronTrigger(second=second, minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=_tzinfo)
        elif len(fields) == 5:
            minute, hour, day, month, dow = fields
            trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=_tzinfo)
        else:
            raise ValueError("POST_CRON must have 5 or 6 fields.")
        _scheduler.add_job(_post_job_fn, trigger, id="post_cron", replace_existing=True, max_instances=1, coalesce=True)
        added += 1

    if collect_interval_minutes and collect_interval_minutes > 0 and _collect_job_fn:
        _scheduler.add_job(_collect_job_fn, IntervalTrigger(minutes=collect_interval_minutes, timezone=_tzinfo),
                           id="collect_interval", replace_existing=True, max_instances=1, coalesce=True)
    if collect_cron and _collect_job_fn:
        fields = collect_cron.split()
        if len(fields) == 6:
            second, minute, hour, day, month, dow = fields
            trigger = CronTrigger(second=second, minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=_tzinfo)
        elif len(fields) == 5:
            minute, hour, day, month, dow = fields
            trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow, timezone=_tzinfo)
        else:
            raise ValueError("COLLECT_CRON must have 5 or 6 fields.")
        _scheduler.add_job(_collect_job_fn, trigger, id="collect_cron", replace_existing=True, max_instances=1, coalesce=True)

    if added == 0 and _post_job_fn:
        _scheduler.add_job(_post_job_fn, IntervalTrigger(seconds=1, timezone=_tzinfo),
                           id="post_default", replace_existing=True, max_instances=1, coalesce=True)
    if _collect_job_fn:
        _scheduler.add_job(_collect_job_fn, IntervalTrigger(minutes=1, timezone=_tzinfo),
                           id="collect_default", replace_existing=True, max_instances=1, coalesce=True)
    return True
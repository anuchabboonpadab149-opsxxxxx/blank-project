import json
import os
import threading
import time
from typing import Any, Callable, Dict, Optional

_STATE_PATH = os.getenv("CB_STATE_PATH", "cb_state.json")
_LOCK = threading.Lock()

# Defaults (tuned for stronger resilience by default; can be overridden by env)
FAILURE_THRESHOLD = int(os.getenv("CB_FAILURE_THRESHOLD", "3"))          # failures to open the circuit
OPEN_TIMEOUT_SEC = int(os.getenv("CB_OPEN_TIMEOUT_SEC", "60"))           # how long to keep open before half-open
MAX_RETRIES = int(os.getenv("CB_MAX_RETRIES", "3"))                      # retries per call when circuit is closed
BACKOFF_BASE = float(os.getenv("CB_BACKOFF_BASE", "1.0"))                # starting delay (seconds)
BACKOFF_FACTOR = float(os.getenv("CB_BACKOFF_FACTOR", "2.0"))            # multiplier
MAX_BACKOFF = float(os.getenv("CB_MAX_BACKOFF", "8.0"))                  # cap delay per attempt


def _load() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(_STATE_PATH):
        return {}
    try:
        with open(_STATE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _save(data: Dict[str, Dict[str, Any]]) -> None:
    tmp = f"{_STATE_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _STATE_PATH)


def _now() -> float:
    return time.time()


def _get_entry(data: Dict[str, Dict[str, Any]], key: str) -> Dict[str, Any]:
    entry = data.get(key)
    if not entry:
        entry = {"state": "closed", "fail_count": 0, "opened_at": None, "last_error": None}
        data[key] = entry
    return entry


def _publish_event(evt: Dict[str, Any]) -> None:
    try:
        import realtime_bus as bus
        bus.publish(evt)
    except Exception:
        pass


def call_with_circuit(name: str, func: Callable[[], Any],
                      max_retries: Optional[int] = None,
                      failure_threshold: Optional[int] = None,
                      open_timeout_sec: Optional[int] = None,
                      backoff_base: Optional[float] = None,
                      backoff_factor: Optional[float] = None,
                      max_backoff: Optional[float] = None) -> Any:
    """
    Execute func() under circuit breaker + retry with exponential backoff.
    Returns func()'s return value. When circuit open, returns a skipped-like dict.
    """
    max_retries = MAX_RETRIES if max_retries is None else max_retries
    failure_threshold = FAILURE_THRESHOLD if failure_threshold is None else failure_threshold
    open_timeout_sec = OPEN_TIMEOUT_SEC if open_timeout_sec is None else open_timeout_sec
    backoff_base = BACKOFF_BASE if backoff_base is None else backoff_base
    backoff_factor = BACKOFF_FACTOR if backoff_factor is None else backoff_factor
    max_backoff = MAX_BACKOFF if max_backoff is None else max_backoff

    with _LOCK:
        data = _load()
        entry = _get_entry(data, name)
        state = entry.get("state", "closed")
        opened_at = entry.get("opened_at")

        if state == "open":
            # Is timeout elapsed?
            if opened_at and (_now() - float(opened_at)) >= open_timeout_sec:
                # half-open: allow one trial
                entry["state"] = "half_open"
                _save(data)
                _publish_event({"type": "circuit", "action": "half_open", "provider": name, "ts": _now()})
            else:
                # still open -> skip
                retry_after = None
                if opened_at:
                    retry_after = max(0.0, open_timeout_sec - (_now() - float(opened_at)))
                return {"provider": name, "status": "skipped", "detail": {"reason": "circuit_open", "retry_after_sec": retry_after}}

    # Decide attempts
    attempts = 1 if entry.get("state") == "half_open" else max(1, int(max_retries))
    delay = backoff_base

    last_error = None
    for i in range(attempts):
        try:
            result = func()
            # On success, close circuit and reset counters
            with _LOCK:
                data = _load()
                entry = _get_entry(data, name)
                if entry.get("state") in {"open", "half_open"}:
                    _publish_event({"type": "circuit", "action": "close", "provider": name, "ts": _now()})
                entry["state"] = "closed"
                entry["fail_count"] = 0
                entry["opened_at"] = None
                entry["last_error"] = None
                _save(data)
            return result
        except Exception as e:
            last_error = str(e)
            # brief backoff, but don't block too long
            time.sleep(min(delay, max_backoff))
            delay *= backoff_factor

    # All attempts failed -> update state
    with _LOCK:
        data = _load()
        entry = _get_entry(data, name)
        entry["fail_count"] = int(entry.get("fail_count", 0)) + 1
        entry["last_error"] = last_error
        if entry["state"] == "half_open":
            # immediate re-open
            entry["state"] = "open"
            entry["opened_at"] = _now()
            _save(data)
            _publish_event({"type": "circuit", "action": "open", "provider": name, "ts": _now(), "reason": "half_open_failed"})
        else:
            if entry["fail_count"] >= failure_threshold:
                entry["state"] = "open"
                entry["opened_at"] = _now()
                _save(data)
                _publish_event({"type": "circuit", "action": "open", "provider": name, "ts": _now(), "reason": "threshold_reached"})
            else:
                _save(data)

    # Return a unified error dict (so callers don't crash)
    return {"provider": name, "status": "error", "detail": {"error": last_error, "circuit_state": _load().get(name, {}).get("state", "unknown")}}


def states() -> Dict[str, Dict[str, Any]]:
    with _LOCK:
        return _load()
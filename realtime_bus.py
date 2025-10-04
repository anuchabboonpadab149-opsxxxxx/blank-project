import json
import os
import time
from threading import Condition
from collections import deque
from typing import Deque, Dict, Generator, List, Optional

# In-memory event buffer with condition for SSE-style streaming
_MAX_EVENTS = 2000
_events: Deque[Dict] = deque(maxlen=_MAX_EVENTS)
_cv: Condition = Condition()

LOG_DIR = "outputs"
EVENTS_LOG = os.path.join(LOG_DIR, "events.jsonl")


def _ensure_dirs() -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(os.path.join(LOG_DIR, "audio"), exist_ok=True)
    os.makedirs(os.path.join(LOG_DIR, "images"), exist_ok=True)
    os.makedirs(os.path.join(LOG_DIR, "video"), exist_ok=True)


_ensure_dirs()


def publish(event: Dict) -> Dict:
    """
    Publish an event to the in-memory queue and append to events.jsonl.
    Adds id and ts fields.
    """
    event = dict(event)  # copy
    event.setdefault("ts", time.time())
    # Persist
    try:
        with open(EVENTS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        # do not block pipeline due to logging errors
        pass
    with _cv:
        # Attach incremental id
        next_id = (_events[-1]["id"] + 1) if _events else 0
        event["id"] = next_id
        _events.append(event)
        _cv.notify_all()
    return event


def recent(n: int = 100) -> List[Dict]:
    with _cv:
        return list(_events)[-n:]


def stream(last_id: Optional[int] = None, keepalive_sec: float = 1.0) -> Generator[Dict, None, None]:
    """
    Generator that yields events as they arrive. Includes keepalive events.
    """
    if last_id is None:
        with _cv:
            last_id = _events[-1]["id"] + 1 if _events else 0
    last_keep = time.time()
    while True:
        with _cv:
            while True:
                if _events and _events[-1]["id"] >= last_id:
                    # find next item
                    for ev in _events:
                        if ev["id"] == last_id:
                            last_id += 1
                            yield ev
                            break
                    else:
                        # Not found (maybe evicted by maxlen); jump to end.
                        last_id = _events[-1]["id"] + 1
                else:
                    break
            # Wait for new events or keepalive timeout
            now = time.time()
            remaining = max(0.0, keepalive_sec - (now - last_keep))
            _cv.wait(timeout=remaining)
        # keepalive outside lock
        now2 = time.time()
        if now2 - last_keep >= keepalive_sec:
            last_keep = now2
            yield {"type": "keepalive", "ts": now2}
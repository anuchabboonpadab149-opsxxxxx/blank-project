import json
import os
import threading
import time
from typing import Dict

_PATH = os.getenv("METRICS_STORE_PATH", "metrics.json")
_LOCK = threading.Lock()


def _load() -> Dict:
    if not os.path.exists(_PATH):
        return {"pageviews": {}, "total_pageviews": 0, "last_visit_ts": None}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"pageviews": {}, "total_pageviews": 0, "last_visit_ts": None}


def _save(data: Dict) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def pageview(route: str) -> None:
    with _LOCK:
        data = _load()
        pv = data.setdefault("pageviews", {})
        pv[route] = int(pv.get(route, 0)) + 1
        data["total_pageviews"] = int(data.get("total_pageviews", 0)) + 1
        data["last_visit_ts"] = time.time()
        _save(data)
    try:
        import realtime_bus as bus
        bus.publish({"type": "visit", "route": route, "ts": time.time()})
    except Exception:
        pass


def get_metrics() -> Dict:
    with _LOCK:
        return _load()
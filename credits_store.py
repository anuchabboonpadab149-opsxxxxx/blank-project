import json
import os
import threading
import time
from typing import Dict, Optional

_PATH = os.getenv("CREDITS_STORE_PATH", "credits.json")
_LOCK = threading.Lock()


def _load() -> Dict:
    if not os.path.exists(_PATH):
        return {"users": {}}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"users": {}}


def _save(data: Dict) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def get(user_id: str) -> int:
    with _LOCK:
        data = _load()
        u = data.setdefault("users", {}).setdefault(user_id, {"credits": 0, "updated_ts": None})
        return int(u.get("credits", 0))


def set(user_id: str, credits: int) -> int:
    with _LOCK:
        data = _load()
        u = data.setdefault("users", {}).setdefault(user_id, {"credits": 0, "updated_ts": None})
        u["credits"] = int(max(0, credits))
        u["updated_ts"] = time.time()
        _save(data)
        return u["credits"]


def add(user_id: str, delta: int) -> int:
    with _LOCK:
        data = _load()
        u = data.setdefault("users", {}).setdefault(user_id, {"credits": 0, "updated_ts": None})
        u["credits"] = int(max(0, int(u.get("credits", 0)) + int(delta)))
        u["updated_ts"] = time.time()
        _save(data)
        return u["credits"]


def use(user_id: str) -> Optional[int]:
    with _LOCK:
        data = _load()
        u = data.setdefault("users", {}).setdefault(user_id, {"credits": 0, "updated_ts": None})
        cur = int(u.get("credits", 0))
        if cur <= 0:
            return None
        u["credits"] = cur - 1
        u["updated_ts"] = time.time()
        _save(data)
        return u["credits"]
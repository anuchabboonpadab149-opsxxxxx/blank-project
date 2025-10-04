import json
import os
import threading
import time
from typing import Dict, List

_PATH = os.getenv("DIVINATION_STORE_PATH", "divinations.json")
_LOCK = threading.Lock()


def _load() -> Dict:
    if not os.path.exists(_PATH):
        return {"history": []}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {"history": []}


def _save(data: Dict) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def append(user_id: str, div_type: str, input_text: str, result_text: str) -> Dict:
    item = {
        "id": int(time.time() * 1000),
        "ts": time.time(),
        "user_id": user_id,
        "type": div_type,
        "input": input_text,
        "result": result_text,
    }
    with _LOCK:
        data = _load()
        hist: List[Dict] = data.setdefault("history", [])
        hist.append(item)
        # limit size to last 1000 for safety
        if len(hist) > 1000:
            hist[:] = hist[-1000:]
        _save(data)
    return item


def recent(limit: int = 50) -> List[Dict]:
    with _LOCK:
        data = _load()
        hist: List[Dict] = data.get("history", [])
        return list(hist[-limit:])
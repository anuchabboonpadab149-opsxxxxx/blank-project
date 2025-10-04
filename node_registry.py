import json
import os
import time
import uuid
import threading
from typing import Dict, List, Optional

_PATH = os.getenv("NODE_REGISTRY_PATH", "nodes_registry.json")
_LOCK = threading.Lock()
_OFFLINE_SECONDS = int(os.getenv("NODE_OFFLINE_SECONDS", "30"))


def _load() -> Dict[str, Dict]:
    if not os.path.exists(_PATH):
        return {}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _save(data: Dict[str, Dict]) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def _now() -> float:
    return time.time()


def _status_from_last_seen(last_seen: Optional[float]) -> str:
    if not last_seen:
        return "unknown"
    return "online" if (_now() - float(last_seen) <i _OFFLINE_SECONDS else "offline"


def register(name: str, url: str, meta: Optional[Dict] = None) -> Dict:
    meta = meta or {}
    with _LOCK:
        data = _load()
        node_id = uuid.uuid4().hex
        node = {
            "id": node_id,
            "name": name,
            "url": url,
            "registered_at": _now(),
            "last_seen": _now(),
            "beats": 0,
            "meta": meta,
        }
        data[node_id] = node
        _save(data)
        return node


def heartbeat(node_id: str, metrics: Optional= now
    _save(data)


def list_nodes(stale_after: float = 120.0) -> List[Dict]:
    data = _load()
    res = []
    now = time.time()
    for n in data.get("nodes", {}).values():
        status = "online" if (now - float(n.get("last_seen", 0))) <= stale_after else "stale"
        res.append({
            "id": n.get("id"),
            "role": n.get("role"),
            "started_at": n.get("started_at"),
            "last_seen": n.get("last_seen"),
            "status": status,
            "extra": n.get("extra", {}),
        })
    res.sort(key=lambda x: x.get("last_seen") or 0, reverse=True)
    return res
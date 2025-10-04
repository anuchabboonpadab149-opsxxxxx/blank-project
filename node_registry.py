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
    return "online" if (_now() - float(last_seen)) < _OFFLINE_SECONDS else "offline"


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


def heartbeat(node_id: str, metrics: Optional[Dict] = None) -> Dict:
    metrics = metrics or {}
    with _LOCK:
        data = _load()
        node = data.get(node_id)
        if not node:
            raise KeyError("node not found")
        node["last_seen"] = _now()
        node["beats"] = int(node.get("beats", 0)) + 1
        node.setdefault("meta", {})
        node["meta"]["metrics"] = metrics
        data[node_id] = node
        _save(data)
        return node


def list_nodes() -> List[Dict]:
    with _LOCK:
        data = _load()
        out: List[Dict] = []
        for node in data.values():
            n = dict(node)
            n["status"] = _status_from_last_seen(n.get("last_seen"))
            out.append(n)
        # sort by status then last_seen desc
        out.sort(key=lambda n: (0 if n["status"] == "online" else 1, -(n.get("last_seen") or 0)))
        return out


def summary() -> Dict:
    nodes = list_nodes()
    online = sum(1 for n in nodes if n.get("status") == "online")
    offline = sum(1 for n in nodes if n.get("status") == "offline")
    return {"total": len(nodes), "online": online, "offline": offline, "threshold_sec": _OFFLINE_SECONDS}
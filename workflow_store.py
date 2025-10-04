import json
import os
import threading
import time
import uuid
from typing import Any, Dict, List, Optional

_PATH = os.getenv("WORKFLOWS_PATH", "workflows.json")
_LOCK = threading.Lock()


def _now() -> float:
    return time.time()


def _load() -> Dict[str, Any]:
    if not os.path.exists(_PATH):
        return {"running": {}, "runs": []}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "running" in data and "runs" in data:
                data["running"] = data.get("running", {})
                data["runs"] = data.get("runs", [])
                return data
    except Exception:
        pass
    return {"running": {}, "runs": []}


def _save(data: Dict[str, Any]) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def _publish(event: Dict[str, Any]) -> None:
    try:
        import realtime_bus as bus
        bus.publish(event)
    except Exception:
        pass


def start(name: str, meta: Optional[Dict[str, Any]] = None) -> str:
    """
    Start a workflow instance. Returns workflow id.
    """
    wid = str(uuid.uuid4())
    with _LOCK:
        data = _load()
        data["running"][wid] = {
            "id": wid,
            "name": str(name),
            "start_ts": _now(),
            "meta": meta or {},
        }
        _save(data)
    _publish({"type": "workflow", "action": "start", "id": wid, "name": name, "ts": _now(), "meta": meta or {}})
    return wid


def end(wid: str, result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Complete a workflow instance successfully.
    """
    with _LOCK:
        data = _load()
        run = data["running"].pop(wid, None)
        if not run:
            # unknown id, record anyway
            run = {"id": wid, "name": "unknown", "start_ts": _now(), "meta": {}}
        run["end_ts"] = _now()
        run["duration_sec"] = float(run["end_ts"]) - float(run.get("start_ts", run["end_ts"]))
        run["status"] = "ok"
        run["result"] = result or {}
        data["runs"].append(run)
        _save(data)
    _publish({"type": "workflow", "action": "end", "id": wid, "name": run.get("name"), "ts": _now(),
              "status": "ok", "duration_sec": run.get("duration_sec"), "result": result or {}})
    return run


def fail(wid: str, error: str) -> Dict[str, Any]:
    """
    Mark a workflow instance as failed.
    """
    with _LOCK:
        data = _load()
        run = data["running"].pop(wid, None)
        if not run:
            run = {"id": wid, "name": "unknown", "start_ts": _now(), "meta": {}}
        run["end_ts"] = _now()
        run["duration_sec"] = float(run["end_ts"]) - float(run.get("start_ts", run["end_ts"]))
        run["status"] = "error"
        run["error"] = error
        data["runs"].append(run)
        _save(data)
    _publish({"type": "workflow", "action": "fail", "id": wid, "name": run.get("name"), "ts": _now(),
              "status": "error", "error": error, "duration_sec": run.get("duration_sec")})
    return run


def reset() -> None:
    with _LOCK:
        data = _load()
        data["runs"] = []
        _save(data)
    _publish({"type": "workflow", "action": "reset", "ts": _now()})


def summary(limit: int = 50) -> Dict[str, Any]:
    with _LOCK:
        data = _load()
        runs = data.get("runs", [])
        running = data.get("running", {})
        agg: Dict[str, Dict[str, Any]] = {}
        for r in runs:
            name = r.get("name", "unknown")
            a = agg.setdefault(name, {"name": name, "ok": 0, "error": 0, "last_duration_sec": None})
            if r.get("status") == "ok":
                a["ok"] += 1
            else:
                a["error"] += 1
            a["last_duration_sec"] = r.get("duration_sec")
        return {
            "total_runs": len(runs),
            "running_count": len(running),
            "running": list(running.values()),
            "last_runs": runs[-limit:],
            "aggregate": list(agg.values()),
        }
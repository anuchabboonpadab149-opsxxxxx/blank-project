import json
import os
import time
from typing import Dict, Any, Optional

AUDIT_LOG = os.getenv("AUDIT_LOG", os.path.join("outputs", "audit.jsonl"))
os.makedirs(os.path.dirname(AUDIT_LOG) or ".", exist_ok=True)

def record(actor: str, action: str, target: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> None:
    obj = {
        "ts": time.time(),
        "actor": actor,
        "action": action,
        "target": target,
        "meta": meta or {},
    }
    try:
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    except Exception:
        pass
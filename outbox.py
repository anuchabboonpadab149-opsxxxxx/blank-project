import json
import os
import time
import uuid
from typing import Dict, List, Optional

BASE_DIR = os.getenv("OUTBOX_DIR", os.path.join("outputs", "outbox"))
LOG_FILE = os.path.join(BASE_DIR, "outbox.jsonl")


def _ensure_dir() -> None:
    os.makedirs(BASE_DIR, exist_ok=True)


def record(provider: str, text: str, detail: Optional[Dict] = None, media: Optional[Dict] = None) -> Dict:
    """
    Persist a simulated 'post' to the outbox. Returns the saved record.
    """
    _ensure_dir()
    rec = {
        "id": uuid.uuid4().hex,
        "ts": time.time(),
        "provider": provider,
        "text": text,
        "detail": detail or {},
        "media": media or {},
    }
    # append log
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass
    # write item file
    try:
        name = f"{int(rec['ts'])}_{provider}_{rec['id']}.json"
        with open(os.path.join(BASE_DIR, name), "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
    return rec


def list_recent(n: int = 50) -> List[Dict]:
    """
    Return last n records from outbox.jsonl (if present).
    """
    _ensure_dir()
    items: List[Dict] = []
    if not os.path.exists(LOG_FILE):
        return items
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()[-n:]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except Exception:
                continue
    except Exception:
        pass
    return items
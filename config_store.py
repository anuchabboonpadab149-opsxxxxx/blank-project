import json
import os
import threading
from typing import Any, Dict, Optional

_PATH = os.getenv("RUNTIME_CONFIG_PATH", "runtime_config.json")
_LOCK = threading.Lock()

_DEFAULTS: Dict[str, Any] = {
    "post_interval_seconds": None,    # None -> use env/cli/default
    "collect_interval_minutes": None, # None -> use env/cli/default
    "providers": None,                # list[str] or None to use env
    "sender_name": None,              # override SENDER_NAME
    "tts_lang": "th",
    "content_mode": None,             # "generate" | "file" | "import" | None -> fallback
    "tweets_file": None,              # override tweets file path
    "import_source_url": None,
    "import_format": "lines",
    # Optional content overrides
    "hashtags_base": None,
    "openers": None,
    "core_love": None,
    "playful_addons": None,
    "light_spicy": None,
}


def _load() -> Dict[str, Any]:
    if not os.path.exists(_PATH):
        return {}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data: Dict[str, Any]) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def get_config() -> Dict[str, Any]:
    with _LOCK:
        cfg = _DEFAULTS.copy()
        cfg.update(_load())
        return cfg


def get(key: str, default: Any = None) -> Any:
    return get_config().get(key, default)


def update_config(patch: Dict[str, Any]) -> Dict[str, Any]:
    with _LOCK:
        cur = _load()
        # Only update keys we know
        for k in list(patch.keys()):
            if k not in _DEFAULTS:
                patch.pop(k, None)
        cur.update(patch)
        _save(cur)
        return get_config()
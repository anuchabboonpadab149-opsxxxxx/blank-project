import json
import os
import threading
from typing import Dict, Optional

_PATH = os.getenv("CREDENTIALS_PATH", "credentials.json")
_LOCK = threading.Lock()

# Allowlist of credential keys we manage via the dashboard
ALLOWED_KEYS = [
    # Twitter (X)
    "TW_CONSUMER_KEY", "TW_CONSUMER_SECRET", "TW_ACCESS_TOKEN", "TW_ACCESS_TOKEN_SECRET", "TW_BEARER_TOKEN",
    # Facebook / Instagram (Graph)
    "FB_PAGE_ID", "FB_ACCESS_TOKEN", "IG_USER_ID", "IG_IMAGE_URL",
    # LinkedIn
    "LI_ACCESS_TOKEN", "LI_ORG_URN",
    # LINE
    "LINE_CHANNEL_ACCESS_TOKEN",
    # Telegram
    "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
    # Discord
    "DISCORD_WEBHOOK_URL",
    # Reddit
    "REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "REDDIT_SUBREDDIT",
    # Mastodon
    "MASTODON_BASE_URL", "MASTODON_ACCESS_TOKEN",
    # TikTok (Ads placeholder)
    "TIKTOK_APP_ID", "TIKTOK_SECRET", "TIKTOK_ADVERTISER_ID",
    # Twitter Ads
    "ADS_ACCOUNT_ID", "FUNDING_INSTRUMENT_ID", "CAMPAIGN_ID", "LINE_ITEM_ID",
    # Optional Ads analytics
    "ADS_ENTITY_IDS",
    # LLM providers
    "LLM_PROVIDER",           # openai|gemini
    "OPENAI_API_KEY", "OPENAI_MODEL",
    "GEMINI_API_KEY", "GEMINI_MODEL",
]


def _load() -> Dict[str, str]:
    if not os.path.exists(_PATH):
        return {}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def _save(data: Dict[str, str]) -> None:
    tmp = f"{_PATH}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def _apply_env(data: Dict[str, str]) -> None:
    # Update current process environment so subsequent provider builds pick these values.
    for k, v in data.items():
        os.environ[str(k)] = str(v)


def mask_value(v: Optional[str]) -> str:
    if not v:
        return ""
    if len(v) <= 6:
        return "*" * len(v)
    return v[:2] + "*" * (len(v) - 4) + v[-2:]


def get() -> Dict[str, str]:
    with _LOCK:
        return _load()


def get_masked() -> Dict[str, str]:
    with _LOCK:
        raw = _load()
        return {k: mask_value(v) for k, v in raw.items()}


def update(patch: Dict[str, Optional[str]]) -> Dict[str, str]:
    """
    Update credentials store with the provided patch.
    - Only keys in ALLOWED_KEYS are accepted.
    - Empty string means 'clear' (remove from store and unset env).
    - Non-empty string sets the value and exports to os.environ.
    Returns the full masked dictionary after update.
    """
    if not isinstance(patch, dict):
        patch = {}
    with _LOCK:
        cur = _load()
        changed: Dict[str, str] = {}
        for k, v in patch.items():
            if k not in ALLOWED_KEYS:
                continue
            s = "" if v is None else str(v)
            if s == "":
                # clear
                if k in cur:
                    del cur[k]
                if k in os.environ:
                    del os.environ[k]
            else:
                cur[k] = s
                changed[k] = s
        _save(cur)
        if changed:
            _apply_env(changed)
        return {k: mask_value(v) for k, v in cur.items()}
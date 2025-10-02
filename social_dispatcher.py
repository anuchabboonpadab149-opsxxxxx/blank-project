import os
import json
import logging
from typing import List, Dict, Any

from promote_ayutthaya import Config, post_one_from_file
from providers.twitter import TwitterProvider
from providers.facebook import FacebookProvider
from providers.linkedin import LinkedInProvider

log = logging.getLogger("social_dispatcher")


def _build_providers(cfg: Config) -> List:
    names = os.getenv("PROVIDERS", "twitter").lower().split(",")
    names = [n.strip() for n in names if n.strip()]
    providers = []
    for n in names:
        if n == "twitter":
            providers.append(TwitterProvider(cfg))
        elif n == "facebook":
            providers.append(FacebookProvider())
        elif n == "linkedin":
            providers.append(LinkedInProvider())
        else:
            log.warning(f"Unknown provider '{n}' — skipping")
    return providers


def distribute_once() -> Dict[str, Any]:
    """
    Pull next text (via tweets.txt rotation) and distribute to all configured providers.
    For Twitter, we also run the promotion flow (Ayutthaya targeting).
    """
    cfg = Config()
    res = post_one_from_file(cfg)  # posts + promotes on Twitter
    text = res.get("text")
    providers = _build_providers(cfg)
    statuses = []
    for p in providers:
        if getattr(p, "name", "") == "twitter":
            # Already posted/promoted by post_one_from_file
            statuses.append({"provider": "twitter", "status": "ok", "detail": {"tweet_id": res.get("tweet_id")}})
        else:
            statuses.append(p.post(text))
    return {"text": text, "providers": statuses, "twitter_detail": res}
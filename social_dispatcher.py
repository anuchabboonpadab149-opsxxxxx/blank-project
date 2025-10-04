import os
import json
import logging
from typing import List, Dict, Any

from promote_ayutthaya import Config, post_one_auto
from providers.twitter import TwitterProvider
from providers.facebook import FacebookProvider
from providers.linkedin import LinkedInProvider
from providers.line import LineProvider
from providers.telegram import TelegramProvider
from providers.discord import DiscordProvider
from providers.instagram import InstagramProvider
from providers.reddit import RedditProvider
from providers.tiktok_ads import TikTokAdsProvider
from providers.mastodon import MastodonProvider

log = logging.getLogger("social_dispatcher")


def _provider_names() -> List[str]:
    try:
        import config_store
        names_cfg = config_store.get("providers")
        if isinstance(names_cfg, list) and names_cfg:
            return [str(x).strip().lower() for x in names_cfg if str(x).strip()]
    except Exception:
        pass
    names_env = os.getenv("PROVIDERS", "twitter")
    return [n.strip().lower() for n in names_env.split(",") if n.strip()]


def _build_providers(cfg: Config) -> List:
    names = _provider_names()
    providers = []
    for n in names:
        if n == "twitter":
            providers.append(TwitterProvider(cfg))
        elif n == "facebook":
            providers.append(FacebookProvider())
        elif n == "linkedin":
            providers.append(LinkedInProvider())
        elif n == "line":
            providers.append(LineProvider())
        elif n == "telegram":
            providers.append(TelegramProvider())
        elif n == "discord":
            providers.append(DiscordProvider())
        elif n == "instagram":
            providers.append(InstagramProvider())
        elif n == "reddit":
            providers.append(RedditProvider())
        elif n == "tiktok":
            providers.append(TikTokAdsProvider())
        elif n == "mastodon":
            providers.append(MastodonProvider())
        else:
            log.warning(f"Unknown provider '{n}' — skipping")
    return providers


def distribute_once() -> Dict[str, Any]:
    """
    Pull next text (tweets.txt/import/generator) and distribute to providers.
    Twitter is posted/promoted; others receive the same text.
    """
    cfg = Config()
    res = post_one_auto(cfg)  # posts + promotes on Twitter
    text = res.get("text")
    providers = _build_providers(cfg)
    statuses = []
    for p in providers:
        if getattr(p, "name", "") == "twitter":
            statuses.append({"provider": "twitter", "status": "ok", "detail": {"tweet_id": res.get("tweet_id")}})
        else:
            statuses.append(p.post(text))
    return {"text": text, "providers": statuses, "twitter_detail": res}
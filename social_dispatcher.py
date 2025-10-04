import os
import json
import logging
from typing import List, Dict, Any, Callable

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

from circuit_breaker import call_with_circuit

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


def _post_with_cb(p, text: str) -> Dict[str, Any]:
    name = getattr(p, "name", "unknown") or "unknown"
    def fn():
        result = p.post(text)
        # If provider itself signals non-exception error, raise to be handled by CB backoff when appropriate
        if isinstance(result, dict) and result.get("status") in {"error"}:
            # Surface the error to allow retry/backoff; include summary in exception
            raise RuntimeError(str(result.get("detail", {}).get("error", "provider_error")))
        return result
    try:
        ret = call_with_circuit(name, fn)
        # call_with_circuit returns either provider dict or a fallback 'skipped/error' dict
        if isinstance(ret, dict):
            return ret
        # if provider returned non-dict, normalize
        return {"provider": name, "status": "ok", "detail": {"result": ret}}
    except Exception as e:
        log.error(f"Provider {name} failed after circuit handling: {e}", exc_info=True)
        return {"provider": name, "status": "error", "detail": {"error": str(e)}}


def distribute_once() -> Dict[str, Any]:
    """
    Pull next text (tweets.txt/import/generator) and distribute to providers.
    Twitter is posted/promoted; others receive the same text.
    """
    cfg = Config()

    # Wrap Twitter posting/promote with circuit breaker too
    def _tw_call():
        return post_one_auto(cfg)

    tw_result = call_with_circuit("twitter", _tw_call)
    providers = _build_providers(cfg)
    statuses: List[Dict[str, Any]] = []

    text = None
    twitter_detail: Dict[str, Any] = {}

    if isinstance(tw_result, dict) and "provider" in tw_result and "status" in tw_result:
        # Circuit breaker skipped/error shape
        twitter_detail = tw_result
        text = tw_result.get("text")
        statuses.append(tw_result)
    else:
        twitter_detail = tw_result if isinstance(tw_result, dict) else {}
        text = (twitter_detail or {}).get("text")
        statuses.append({"provider": "twitter", "status": "ok", "detail": {"tweet_id": twitter_detail.get("tweet_id")}})

    # Fallback: ensure text exists even if twitter was skipped/error
    if not text:
        try:
            from content_generator import generate_caption
            # Attempt to read sender_name override from config_store if available
            try:
                import config_store
                sender = config_store.get("sender_name")
            except Exception:
                sender = None
            text = generate_caption(sender_name=sender)
        except Exception:
            text = "สวัสดีจากระบบอัตโนมัติ"

    for p in providers:
        if getattr(p, "name", "") == "twitter":
            # Already handled above via circuit breaker
            continue
        statuses.append(_post_with_cb(p, text))

    return {"text": text, "providers": statuses, "twitter_detail": twitter_detail}
import os
import json
import logging
import uuid
from typing import List, Dict, Any, Optional

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


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}


# Defaults: real API mode (no simulation) unless explicitly enabled
SIMULATE_ALL_PROVIDERS = _bool_env("SIMULATE_ALL_PROVIDERS", False)
SIMULATE_ON_ERROR = _bool_env("SIMULATE_ON_ERROR", False)


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


def _has_credentials(name: str) -> bool:
    """
    Minimal credential presence check per provider.
    Used to auto-enable simulation when nothing is configured.
    """
    env = lambda k: (os.getenv(k) or "").strip()
    name = (name or "").lower()
    if name == "twitter":
        return all(env(k) for k in ["TW_CONSUMER_KEY", "TW_CONSUMER_SECRET", "TW_ACCESS_TOKEN", "TW_ACCESS_TOKEN_SECRET"])
    if name == "facebook":
        return all(env(k) for k in ["FB_PAGE_ID", "FB_ACCESS_TOKEN"])
    if name == "linkedin":
        return all(env(k) for k in ["LI_ACCESS_TOKEN", "LI_ORG_URN"])
    if name == "line":
        return bool(env("LINE_CHANNEL_ACCESS_TOKEN"))
    if name == "telegram":
        return all(env(k) for k in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"])
    if name == "discord":
        return bool(env("DISCORD_WEBHOOK_URL"))
    if name == "instagram":
        return all(env(k) for k in ["IG_USER_ID", "FB_ACCESS_TOKEN", "IG_IMAGE_URL"])
    if name == "reddit":
        return all(env(k) for k in ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD", "REDDIT_SUBREDDIT"])
    if name == "mastodon":
        return all(env(k) for k in ["MASTODON_BASE_URL", "MASTODON_ACCESS_TOKEN"])
    if name == "tiktok":
        return all(env(k) for k in ["TIKTOK_APP_ID", "TIKTOK_SECRET", "TIKTOK_ADVERTISER_ID"])
    return False


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


def _simulate_post(provider_name: str, text: str) -> Dict[str, Any]:
    try:
        import outbox
        rec = outbox.record(provider_name, text, detail={"simulated": True})
        sim_id = rec.get("id")
    except Exception:
        sim_id = uuid.uuid4().hex
    # Emit simulation event
    try:
        import realtime_bus as bus
        bus.publish({"type": "simulate", "provider": provider_name, "text": text})
    except Exception:
        pass
    return {"provider": provider_name, "status": "ok", "detail": {"simulated": True, "id": sim_id}}


def _maybe_simulate(ret: Dict[str, Any], provider: str, text: str) -> Dict[str, Any]:
    status = (ret or {}).get("status")
    if status == "skipped" and SIMULATE_ALL_PROVIDERS:
        return _simulate_post(provider, text)
    if status == "error" and SIMULATE_ON_ERROR:
        return _simulate_post(provider, text)
    return ret


def _generate_text() -> str:
    try:
        from content_generator import generate_caption
        try:
            import config_store
            sender = config_store.get("sender_name")
        except Exception:
            sender = None
        return generate_caption(sender_name=sender)
    except Exception:
        return "สวัสดีจากระบบอัตโนมัติ"


def _post_with_cb(p, text: str) -> Dict[str, Any]:
    name = getattr(p, "name", "unknown") or "unknown"

    def fn():
        result = p.post(text)
        if isinstance(result, dict) and result.get("status") in {"error"}:
            raise RuntimeError(str(result.get("detail", {}).get("error", "provider_error")))
        return result

    try:
        ret = call_with_circuit(name, fn)
        if isinstance(ret, dict):
            return _maybe_simulate(ret, name, text)
        return {"provider": name, "status": "ok", "detail": {"result": ret}}
    except Exception as e:
        log.error(f"Provider {name} failed after circuit handling: {e}", exc_info=True)
        if SIMULATE_ON_ERROR:
            return _simulate_post(name, text)
        return {"provider": name, "status": "error", "detail": {"error": str(e)}}


def distribute_once() -> Dict[str, Any]:
    """
    Pull next text (tweets.txt/import/generator) and distribute to providers.
    Real API mode by default; simulation can be enabled by env flags.
    """
    cfg = Config()
    providers = _build_providers(cfg)

    # Auto-enable simulation if no provider has credentials configured
    try:
        names = _provider_names()
        if names and not any(_has_credentials(n) for n in names):
            global SIMULATE_ALL_PROVIDERS
            SIMULATE_ALL_PROVIDERS = True
            log.info("No provider credentials detected; enabling SIMULATE_ALL_PROVIDERS=True automatically.")
    except Exception:
        pass

    statuses: List[Dict[str, Any]] = []
    text: Optional[str] = None
    twitter_detail: Dict[str, Any] = {}

    if SIMULATE_ALL_PROVIDERS:
        text = _generate_text()
        included = set()
        for p in providers:
            nm = getattr(p, "name", "unknown") or "unknown"
            statuses.append(_simulate_post(nm, text))
            included.add(nm)
        if "twitter" not in included:
            statuses.append(_simulate_post("twitter", text))
        twitter_detail = {"provider": "twitter", "status": "ok", "detail": {"simulated": True}}
        return {"text": text, "providers": statuses, "twitter_detail": twitter_detail}

    # Real mode: post on Twitter with CB
    def _tw_call():
        return post_one_auto(cfg)

    tw_result = call_with_circuit("twitter", _tw_call)

    if isinstance(tw_result, dict) and "provider" in tw_result and "status" in tw_result:
        twitter_detail = _maybe_simulate(tw_result, "twitter", tw_result.get("text") or "")
        text = twitter_detail.get("text")
        statuses.append(twitter_detail)
    else:
        twitter_detail = tw_result if isinstance(tw_result, dict) else {}
        text = (twitter_detail or {}).get("text")
        statuses.append({"provider": "twitter", "status": "ok", "detail": {"tweet_id": twitter_detail.get("tweet_id")}})

    if not text:
        text = _generate_text()

    for p in providers:
        if getattr(p, "name", "") == "twitter":
            continue
        statuses.append(_post_with_cb(p, text))

    return {"text": text, "providers": statuses, "twitter_detail": twitter_detail}

    # Real mode attempt: post on Twitter with CB (if credentials missing, will error -> simulate on error)
    def _tw_call():
        return post_one_auto(cfg)

    try:
        tw_result = call_with_circuit("twitter", _tw_call)
    except Exception as e:
        log.error(f"Twitter call failed: {e}", exc_info=True)
        tw_result = {"provider": "twitter", "status": "error", "detail": {"error": str(e)}}

    if isinstance(tw_result, dict) and "provider" in tw_result and "status" in tw_result:
        twitter_detail = _maybe_simulate(tw_result, "twitter", (tw_result.get("text") or ""))  # type: ignore[arg-type]
        text = twitter_detail.get("text")
        statuses.append(twitter_detail)
    else:
        twitter_detail = tw_result if isinstance(tw_result, dict) else {}
        text = (twitter_detail or {}).get("text")
        statuses.append({"provider": "twitter", "status": "ok", "detail": {"tweet_id": twitter_detail.get("tweet_id")}})

    if not text:
        text = _generate_text()

    for p in providers:
        if getattr(p, "name", "") == "twitter":
            continue
        statuses.append(_post_with_cb(p, text))

    return {"text": text, "providers": statuses, "twitter_detail": twitter_detail}
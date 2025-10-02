import os
import logging
import requests

log = logging.getLogger("dispatcher")


def _bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


# ========== Mastodon ==========
def post_mastodon(text: str) -> dict:
    if not _bool_env("MASTODON_ENABLED"):
        return {"skipped": "MASTODON_ENABLED false"}
    base = os.getenv("MASTODON_BASE_URL")
    token = os.getenv("MASTODON_ACCESS_TOKEN")
    if not base or not token:
        return {"error": "MASTODON_BASE_URL or MASTODON_ACCESS_TOKEN missing"}
    url = f"{base.rstrip('/')}/api/v1/statuses"
    resp = requests.post(url, data={"status": text}, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ========== Reddit ==========
def post_reddit(text: str) -> dict:
    if not _bool_env("REDDIT_ENABLED"):
        return {"skipped": "REDDIT_ENABLED false"}
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    subreddit = os.getenv("REDDIT_SUBREDDIT")
    if not all([client_id, client_secret, username, password, subreddit]):
        return {"error": "Reddit credentials or subreddit missing"}
    # OAuth2 script app
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    data = {"grant_type": "password", "username": username, "password": password}
    headers = {"User-Agent": "ayutthaya-poster/0.1"}
    tok = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers, timeout=15)
    tok.raise_for_status()
    access_token = tok.json()["access_token"]
    headers["Authorization"] = f"Bearer {access_token}"
    # Submit text post
    submit = requests.post("https://oauth.reddit.com/api/submit", headers=headers, timeout=15, data={
        "sr": subreddit,
        "kind": "self",
        "title": (text[:250] or "Post"),
        "text": text
    })
    submit.raise_for_status()
    return submit.json()


# ========== Facebook Page ==========
def post_facebook_page(text: str) -> dict:
    if not _bool_env("FACEBOOK_ENABLED"):
        return {"skipped": "FACEBOOK_ENABLED false"}
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
    if not page_id or not token:
        return {"error": "FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN missing"}
    url = f"https://graph.facebook.com/v21.0/{page_id}/feed"
    resp = requests.post(url, data={"message": text}, params={"access_token": token}, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ========== LinkedIn ==========
def post_linkedin(text: str) -> dict:
    if not _bool_env("LINKEDIN_ENABLED"):
        return {"skipped": "LINKEDIN_ENABLED false"}
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    urn = os.getenv("LINKEDIN_ORGANIZATION_URN") or os.getenv("LINKEDIN_PERSON_URN")
    if not token or not urn:
        return {"error": "LINKEDIN_ACCESS_TOKEN or URN missing"}
    # UGC Post (text only)
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    payload = {
        "author": urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ========== Telegram ==========
def post_telegram(text: str) -> dict:
    if not _bool_env("TELEGRAM_ENABLED"):
        return {"skipped": "TELEGRAM_ENABLED false"}
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not bot_token or not chat_id:
        return {"error": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing"}
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ========== Discord Webhook ==========
def post_discord(text: str) -> dict:
    if not _bool_env("DISCORD_ENABLED"):
        return {"skipped": "DISCORD_ENABLED false"}
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook:
        return {"error": "DISCORD_WEBHOOK_URL missing"}
    resp = requests.post(webhook, json={"content": text}, timeout=15)
    resp.raise_for_status()
    return {"status": "ok"}


def cross_post(text: str) -> dict:
    """
    Cross-post to all enabled platforms. Returns a dict with per-platform results.
    """
    results = {}
    for name, func in {
        "mastodon": post_mastodon,
        "reddit": post_reddit,
        "facebook": post_facebook_page,
        "linkedin": post_linkedin,
        "telegram": post_telegram,
        "discord": post_discord,
    }.items():
        try:
            res = func(text)
            results[name] = res
        except Exception as e:
            log.error(f"{name} post failed: {e}", exc_info=True)
            results[name] = {"error": str(e)}
    return results
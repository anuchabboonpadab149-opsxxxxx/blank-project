

import os
import sys
import json
import logging
from typing import Tuple, Dict, Any, List

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

BASE_ADS = "https://ads-api.twitter.com/11"
BASE_TW = "https://api.twitter.com/1.1"

log = logging.getLogger("promote_ayutthaya")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


class Config:
    def __init__(self) -> None:
        load_dotenv()
        # Credentials
        self.CONSUMER_KEY = os.getenv("TW_CONSUMER_KEY")
        self.CONSUMER_SECRET = os.getenv("TW_CONSUMER_SECRET")
        self.ACCESS_TOKEN = os.getenv("TW_ACCESS_TOKEN")
        self.ACCESS_TOKEN_SECRET = os.getenv("TW_ACCESS_TOKEN_SECRET")
        self.BEARER = os.getenv("TW_BEARER_TOKEN", "")
        # Ads account
        self.ADS_ACCOUNT_ID = os.getenv("ADS_ACCOUNT_ID")
        self.FUNDING_INSTRUMENT_ID = os.getenv("FUNDING_INSTRUMENT_ID")
        self.CAMPAIGN_ID = os.getenv("CAMPAIGN_ID") or None
        # Tweet content or file-based rotation
        self.TWEET_TEXT = os.getenv("TWEET_TEXT")
        self.TWEETS_FILE = os.getenv("TWEETS_FILE", "tweets.txt")
        # Budget/bid
        self.DAILY_BUDGET_MICRO = int(os.getenv("DAILY_BUDGET_MICRO", "5000000"))
        self.TOTAL_BUDGET_MICRO = int(os.getenv("TOTAL_BUDGET_MICRO", str(self.DAILY_BUDGET_MICRO * 7)))
        self.BID_AMOUNT_MICRO = int(os.getenv("BID_AMOUNT_MICRO", "500000"))
        self.OBJECTIVE = os.getenv("OBJECTIVE", "TWEET_ENGAGEMENTS")
        self.PLACEMENT = os.getenv("PLACEMENT", "ALL_ON_TWITTER")

    def validate(self) -> None:
        required = {
            "TW_CONSUMER_KEY": self.CONSUMER_KEY,
            "TW_CONSUMER_SECRET": self.CONSUMER_SECRET,
            "TW_ACCESS_TOKEN": self.ACCESS_TOKEN,
            "TW_ACCESS_TOKEN_SECRET": self.ACCESS_TOKEN_SECRET,
            "ADS_ACCOUNT_ID": self.ADS_ACCOUNT_ID,
            "FUNDING_INSTRUMENT_ID": self.FUNDING_INSTRUMENT_ID,
        }
        missing = [k for k, v in required.items() if not v or str(v).strip() == ""]
        if missing:
            raise SystemExit(f"Missing required env vars: {', '.join(missing)}")


def oauth(config: Config) -> OAuth1:
    return OAuth1(config.CONSUMER_KEY, config.CONSUMER_SECRET, config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)


def post_tweet(auth: OAuth1, text: str) -> str:
    url = f"{BASE_TW}/statuses/update.json"
    resp = requests.post(url, auth=auth, data={"status": text})
    resp.raise_for_status()
    data = resp.json()
    return data["id_str"]


def create_campaign(auth: OAuth1, account_id: str, funding_instrument_id: str, name: str, daily_budget_micro: int, total_budget_micro: int) -> str:
    url = f"{BASE_ADS}/accounts/{account_id}/campaigns"
    payload = {
        "funding_instrument_id": funding_instrument_id,
        "name": name,
        "daily_budget_amount_local_micro": str(daily_budget_micro),
        "total_budget_amount_local_micro": str(total_budget_micro),
        "paused": False,
    }
    resp = requests.post(url, auth=auth, data=payload)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def create_line_item(auth: OAuth1, account_id: str, campaign_id: str, name: str, placement: str, objective: str, bid_micro: int) -> str:
    url = f"{BASE_ADS}/accounts/{account_id}/line_items"
    payload = {
        "campaign_id": campaign_id,
        "name": name,
        "product_type": "PROMOTED_TWEETS",
        "placements": [placement],
        "objective": objective,
        "bid_amount_local_micro": bid_micro,
        "paused": False,
    }
    resp = requests.post(url, auth=auth, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def find_ayutthaya_location_id(auth: OAuth1, account_id: str) -> Tuple[str, Dict[str, Any]]:
    url = f"{BASE_ADS}/accounts/{account_id}/targeting_criteria/locations"
    params = {"location_type": "REGION", "country_code": "TH", "q": "Ayutthaya"}
    resp = requests.get(url, auth=auth, params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data:
        params["q"] = "Phra Nakhon Si Ayutthaya"
        resp = requests.get(url, auth=auth, params=params)
        resp.raise_for_status()
        data = resp.json().get("data", [])
    if not data:
        raise RuntimeError("Ayutthaya region not found in Ads API locations.")
    loc = data[0]
    return loc["targeting_value"], loc


def add_geo_targeting(auth: OAuth1, account_id: str, line_item_id: str, location_id: str) -> str:
    url = f"{BASE_ADS}/accounts/{account_id}/targeting_criteria"
    payload = {
        "line_item_id": line_item_id,
        "targeting_type": "LOCATION",
        "targeting_value": location_id,
    }
    resp = requests.post(url, auth=auth, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def promote_tweet(auth: OAuth1, account_id: str, line_item_id: str, tweet_id: str) -> str:
    url = f"{BASE_ADS}/accounts/{account_id}/promoted_tweets"
    payload = {"line_item_id": line_item_id, "tweet_id": tweet_id}
    resp = requests.post(url, auth=auth, json=payload)
    resp.raise_for_status()
    return resp.json()["data"]["id"]


def run_once(cfg: Config) -> Dict[str, Any]:
    # Legacy: post cfg.TWEET_TEXT and promote
    cfg.validate()
    _auth = oauth(cfg)
    text = cfg.TWEET_TEXT
    if not text:
        raise SystemExit("TWEET_TEXT is empty; use file-based posting via post_one_from_file.")
    tweet_id = post_tweet(_auth, text)
    if cfg.CAMPAIGN_ID:
        campaign_id = cfg.CAMPAIGN_ID
    else:
        campaign_id = create_campaign(_auth, cfg.ADS_ACCOUNT_ID, cfg.FUNDING_INSTRUMENT_ID, "Ayutthaya Reach Campaign", cfg.DAILY_BUDGET_MICRO, cfg.TOTAL_BUDGET_MICRO)
    line_item_id = create_line_item(_auth, cfg.ADS_ACCOUNT_ID, campaign_id, "Ayutthaya LI", cfg.PLACEMENT, cfg.OBJECTIVE, cfg.BID_AMOUNT_MICRO)
    location_id, loc_meta = find_ayutthaya_location_id(_auth, cfg.ADS_ACCOUNT_ID)
    tc_id = add_geo_targeting(_auth, cfg.ADS_ACCOUNT_ID, line_item_id, location_id)
    promoted_id = promote_tweet(_auth, cfg.ADS_ACCOUNT_ID, line_item_id, tweet_id)
    return {"tweet_id": tweet_id, "campaign_id": campaign_id, "line_item_id": line_item_id, "targeting_criteria_id": tc_id, "promoted_tweet_id": promoted_id, "location": loc_meta, "text": text}


# ===== File rotation and metrics =====

STATE_FILE = "posted_state.json"
METRICS_FILE = "metrics.json"
ADS_METRICS_FILE = "ads_metrics.json"


def _load_json(path: str) -> Dict[str, Any]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_tweets(path: str) -> List[str]:
    tweets: List[str] = []
    if not os.path.exists(path):
        return tweets
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            t = line.strip()
            if t:
                tweets.append(t)
    return tweets


def get_next_tweet(tweets: List[str]) -> str:
    state = _load_json(STATE_FILE)
    used = set(state.get("used_texts", []))
    for t in tweets:
        if t not in used:
            return t
    # Reset when all used
    if tweets:
        _save_json(STATE_FILE, {"used_texts": [], "posted": state.get("posted", [])})
        return tweets[0]
    raise SystemExit("No tweets available in tweets file")


def mark_used(text: str, tweet_id: str) -> None:
    state = _load_json(STATE_FILE)
    used = set(state.get("used_texts", []))
    used.add(text)
    posted = state.get("posted", [])
    posted.append({"text": text, "tweet_id": tweet_id})
    state["used_texts"] = list(used)
    state["posted"] = posted
    _save_json(STATE_FILE, state)


def post_one_from_file(cfg: Config) -> Dict[str, Any]:
    cfg.validate()
    _auth = oauth(cfg)
    tweets = load_tweets(cfg.TWEETS_FILE)
    text = get_next_tweet(tweets)
    log.info(f"Posting tweet from file: {text}")
    tweet_id = post_tweet(_auth, text)
    mark_used(text, tweet_id)
    # Promote on X Ads
    if cfg.CAMPAIGN_ID:
        campaign_id = cfg.CAMPAIGN_ID
    else:
        campaign_id = create_campaign(_auth, cfg.ADS_ACCOUNT_ID, cfg.FUNDING_INSTRUMENT_ID, "Ayutthaya Reach Campaign", cfg.DAILY_BUDGET_MICRO, cfg.TOTAL_BUDGET_MICRO)
    line_item_id = create_line_item(_auth, cfg.ADS_ACCOUNT_ID, campaign_id, "Ayutthaya LI", cfg.PLACEMENT, cfg.OBJECTIVE, cfg.BID_AMOUNT_MICRO)
    location_id, loc_meta = find_ayutthaya_location_id(_auth, cfg.ADS_ACCOUNT_ID)
    tc_id = add_geo_targeting(_auth, cfg.ADS_ACCOUNT_ID, line_item_id, location_id)
    promoted_id = promote_tweet(_auth, cfg.ADS_ACCOUNT_ID, line_item_id, tweet_id)

    # Cross-post to other platforms
    try:
        from dispatcher import cross_post
        cross = cross_post(text)
    except Exception as e:
        log.error(f"Cross-post failed: {e}", exc_info=True)
        cross = {"error": str(e)}

    return {
        "tweet_id": tweet_id,
        "campaign_id": campaign_id,
        "line_item_id": line_item_id,
        "targeting_criteria_id": tc_id,
        "promoted_tweet_id": promoted_id,
        "location": loc_meta,
        "text": text,
        "cross_post": cross
    }


def collect_metrics(cfg: Config, max_items: int = 50) -> Dict[str, Any]:
    state = _load_json(STATE_FILE)
    posted = state.get("posted", [])
    ids = [p["tweet_id"] for p in posted[-max_items:] if "tweet_id" in p]
    res = {"count": 0, "items": []}
    if not ids or not cfg.BEARER:
        return res
    url = "https://api.twitter.com/2/tweets"
    params = {"ids": ",".join(ids), "tweet.fields": "created_at,public_metrics"}
    headers = {"Authorization": f"Bearer {cfg.BEARER}"}
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("data", [])
    res["count"] = len(items)
    res["items"] = items
    existing = _load_json(METRICS_FILE)
    existing.setdefault("runs", [])
    existing["runs"].append({"items": items})
    _save_json(METRICS_FILE, existing)
    return res


def _load_entity_ids() -> List[str]:
    ids_env = os.getenv("ADS_ENTITY_IDS", "")
    ids: List[str] = []
    if ids_env.strip():
        ids = [x.strip() for x in ids_env.split(",") if x.strip()]
    else:
        path = os.getenv("ADS_ENTITY_FILE", "ads_entities.txt")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    t = line.strip()
                    if t:
                        ids.append(t)
    return ids


def collect_ads_analytics(cfg: Config) -> Dict[str, Any]:
    """
    Collect Ads analytics via Ads API v11 synchronous stats endpoint.
    Returns impressions, engagements, etc. depending on metric_groups.
    """
    entity = os.getenv("ADS_ENTITY_TYPE", "LINE_ITEM")  # LINE_ITEM, PROMOTED_TWEET, CAMPAIGN
    granularity = os.getenv("ADS_GRANULARITY", "HOUR")  # HOUR or DAY
    start_time = os.getenv("ADS_START_TIME")            # ISO8601 e.g. 2025-10-01T00:00:00Z
    end_time = os.getenv("ADS_END_TIME")                # ISO8601
    metric_groups = os.getenv("ADS_METRIC_GROUPS", "ENGAGEMENT")  # e.g., ENGAGEMENT,BILLING,MEDIA

    ids = _load_entity_ids()
    if not ids:
        return {"error": "No Ads entity IDs provided."}

    auth = oauth(cfg)
    url = f"{BASE_ADS}/stats/accounts/{cfg.ADS_ACCOUNT_ID}"
    params = {
        "entity": entity,
        "entity_ids": ",".join(ids),
        "granularity": granularity,
        "metric_groups": metric_groups,
    }
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time

    resp = requests.get(url, auth=auth, params=params)
    resp.raise_for_status()
    data = resp.json()

    # Persist
    existing = _load_json(ADS_METRICS_FILE)
    existing.setdefault("runs", [])
    existing["runs"].append(data)
    _save_json(ADS_METRICS_FILE, existing)

    return {"status": "ok", "count": len(data.get("data", []))}


if __name__ == "__main__":
    cfg = Config()
    # Default: post from file then collect metrics (organic + ads)
    posted = post_one_from_file(cfg)
    print(json.dumps(posted, ensure_ascii=False))
    metrics = collect_metrics(cfg)
    print(json.dumps(metrics, ensure_ascii=False))
    ads = collect_ads_analytics(cfg)
    print(json.dumps(ads, ensure_ascii=False))
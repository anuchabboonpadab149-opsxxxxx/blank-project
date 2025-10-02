import os
import sys
import json
import logging
from typing import Tuple, Dict, Any, Optional

import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

# Optional scheduler imports are done in cli.py to avoid forcing daemon mode here.

BASE_ADS = "https://ads-api.twitter.com/11"
BASE_TW = "https://api.twitter.com/1.1"

log = logging.getLogger("promote_ayutthaya")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)


class Config:
    def __init__(self) -> None:
        load_dotenv()
        # Credentials
        self.CONSUMER_KEY = os.getenv("TW_CONSUMER_KEY")
        self.CONSUMER_SECRET = os.getenv("TW_CONSUMER_SECRET")
        self.ACCESS_TOKEN = os.getenv("TW_ACCESS_TOKEN")
        self.ACCESS_TOKEN_SECRET = os.getenv("TW_ACCESS_TOKEN_SECRET")
        # Ads account
        self.ADS_ACCOUNT_ID = os.getenv("ADS_ACCOUNT_ID")
        self.FUNDING_INSTRUMENT_ID = os.getenv("FUNDING_INSTRUMENT_ID")
        self.CAMPAIGN_ID = os.getenv("CAMPAIGN_ID") or None
        # Tweet content
        self.TWEET_TEXT = os.getenv("TWEET_TEXT")
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
            "TWEET_TEXT": self.TWEET_TEXT,
        }
        missing = [k for k, v in required.items() if not v or str(v).strip() == ""]
        if missing:
            raise SystemExit(f"Missing required env vars: {', '.join(missing)}")


def oauth(config: Config) -> OAuth1:
    return OAuth1(
        config.CONSUMER_KEY,
        config.CONSUMER_SECRET,
        config.ACCESS_TOKEN,
        config.ACCESS_TOKEN_SECRET,
    )


def post_tweet(auth: OAuth1, text: str) -> str:
    url = f"{BASE_TW}/statuses/update.json"
    resp = requests.post(url, auth=auth, data={"status": text})
    resp.raise_for_status()
    data = resp.json()
    return data["id_str"]


def create_campaign(auth: OAuth1, account_id: str, funding_instrument_id: str, name: str) -> str:
    url = f"{BASE_ADS}/accounts/{account_id}/campaigns"
    payload = {
        "funding_instrument_id": funding_instrument_id,
        "name": name,
        "daily_budget_amount_local_micro": str(cfg.DAILY_BUDGET_MICRO),
        "total_budget_amount_local_micro": str(cfg.TOTAL_BUDGET_MICRO),
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
    cfg.validate()
    _auth = oauth(cfg)

    log.info("Posting tweet")
    tweet_id = post_tweet(_auth, cfg.TWEET_TEXT)
    log.info(f"Tweet ID: {tweet_id}")

    if cfg.CAMPAIGN_ID:
        campaign_id = cfg.CAMPAIGN_ID
        log.info(f"Using existing campaign: {campaign_id}")
    else:
        log.info("Creating campaign")
        campaign_id = create_campaign(_auth, cfg.ADS_ACCOUNT_ID, cfg.FUNDING_INSTRUMENT_ID, "Ayutthaya Reach Campaign")
        log.info(f"Campaign ID: {campaign_id}")

    log.info("Creating line item")
    line_item_id = create_line_item(_auth, cfg.ADS_ACCOUNT_ID, campaign_id, "Ayutthaya LI", cfg.PLACEMENT, cfg.OBJECTIVE, cfg.BID_AMOUNT_MICRO)
    log.info(f"Line Item ID: {line_item_id}")

    log.info("Finding Ayutthaya location")
    location_id, loc_meta = find_ayutthaya_location_id(_auth, cfg.ADS_ACCOUNT_ID)
    log.info(f"Targeting Ayutthaya: {loc_meta.get('name')} ({location_id})")

    log.info("Adding geo targeting")
    tc_id = add_geo_targeting(_auth, cfg.ADS_ACCOUNT_ID, line_item_id, location_id)
    log.info(f"Targeting criteria ID: {tc_id}")

    log.info("Promoting tweet")
    promoted_id = promote_tweet(_auth, cfg.ADS_ACCOUNT_ID, line_item_id, tweet_id)
    log.info(f"Promoted Tweet ID: {promoted_id}")

    return {
        "tweet_id": tweet_id,
        "campaign_id": campaign_id,
        "line_item_id": line_item_id,
        "targeting_criteria_id": tc_id,
        "promoted_tweet_id": promoted_id,
        "location": loc_meta,
    }


if __name__ == "__main__":
    # Direct run does a one-shot promotion
    cfg = Config()
    result = run_once(cfg)
    print(json.dumps(result, ensure_ascii=False))
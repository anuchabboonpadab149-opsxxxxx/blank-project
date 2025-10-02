import logging
from typing import Optional

from requests_oauthlib import OAuth1
import requests

from promote_ayutthaya import Config, oauth, post_tweet

log = logging.getLogger("providers.twitter")


class TwitterProvider:
    name = "twitter"

    def __init__(self, cfg: Config):
        self.cfg = cfg

    def post(self, text: str):
        try:
            self.cfg.validate()
            _auth = oauth(self.cfg)
            tweet_id = post_tweet(_auth, text)
            return {"provider": self.name, "status": "ok", "detail": {"tweet_id": tweet_id}}
        except Exception as e:
            log.error(f"Twitter post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
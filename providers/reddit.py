import logging
import os
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger("providers.reddit")


class RedditProvider:
    name = "reddit"

    def __init__(self):
        self.client_id = os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
        self.username = os.getenv("REDDIT_USERNAME", "")
        self.password = os.getenv("REDDIT_PASSWORD", "")
        self.subreddit = os.getenv("REDDIT_SUBREDDIT", "")

    def _get_token(self):
        auth = HTTPBasicAuth(self.client_id, self.client_secret)
        data = {"grant_type": "password", "username": self.username, "password": self.password}
        headers = {"User-Agent": "BeeBellBot/1.0"}
        resp = requests.post("https://www.reddit.com/api/v1/access_token", auth=auth, data=data, headers=headers, timeout=20)
        resp.raise_for_status()
        return resp.json().get("access_token")

    def post(self, text: str):
        if not all([self.client_id, self.client_secret, self.username, self.password, self.subreddit]):
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "REDDIT_* envs missing"}}
        try:
            token = self._get_token()
            headers = {"Authorization": f"Bearer {token}", "User-Agent": "BeeBellBot/1.0"}
            payload = {"sr": self.subreddit, "title": text[:280], "kind": "self", "text": text}
            resp = requests.post("https://oauth.reddit.com/api/submit", headers=headers, data=payload, timeout=20)
            resp.raise_for_status()
            data = resp.json() if resp.headers.get("Content-Type", "").startswith("application/json") else {"status_code": resp.status_code}
            return {"provider": self.name, "status": "ok", "detail": data}
        except Exception as e:
            log.error(f"Reddit post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
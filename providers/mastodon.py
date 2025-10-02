import os
import logging
import requests

log = logging.getLogger("providers.mastodon")


class MastodonProvider:
    name = "mastodon"

    def __init__(self):
        self.base_url = os.getenv("MASTODON_BASE_URL", "")
        self.access_token = os.getenv("MASTODON_ACCESS_TOKEN", "")

    def post(self, text: str):
        if not self.base_url or not self.access_token:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "MASTODON_BASE_URL or MASTODON_ACCESS_TOKEN missing"}}
        try:
            url = f"{self.base_url.rstrip('/')}/api/v1/statuses"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            resp = requests.post(url, headers=headers, data={"status": text}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {"provider": self.name, "status": "ok", "detail": data}
        except Exception as e:
            log.error(f"Mastodon post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
import logging
import os
import requests

log = logging.getLogger("providers.facebook")


class FacebookProvider:
    name = "facebook"

    def __init__(self):
        self.page_id = os.getenv("FB_PAGE_ID", "")
        self.access_token = os.getenv("FB_ACCESS_TOKEN", "")

    def post(self, text: str):
        if not self.page_id or not self.access_token:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "FB_PAGE_ID or FB_ACCESS_TOKEN missing"}}
        try:
            url = f"https://graph.facebook.com/v19.0/{self.page_id}/feed"
            resp = requests.post(url, data={"message": text, "access_token": self.access_token}, timeout=20)
            resp.raise_for_status()
            data = resp.json()
            return {"provider": self.name, "status": "ok", "detail": data}
        except Exception as e:
            log.error(f"Facebook post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
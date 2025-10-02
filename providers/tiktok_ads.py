import logging
import os

log = logging.getLogger("providers.tiktok_ads")


class TikTokAdsProvider:
    name = "tiktok"

    def __init__(self):
        self.app_id = os.getenv("TIKTOK_APP_ID", "")
        self.secret = os.getenv("TIKTOK_SECRET", "")
        self.advertiser_id = os.getenv("TIKTOK_ADVERTISER_ID", "")

    def post(self, text: str):
        # TikTok organic posting is not supported via public API.
        # This provider is a placeholder for Ads integration.
        if not all([self.app_id, self.secret, self.advertiser_id]):
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "TIKTOK_* envs missing (ads integration placeholder)"}}
        return {"provider": self.name, "status": "skipped", "detail": {"reason": "TikTok Ads integration needs creative assets and campaign settings"}}
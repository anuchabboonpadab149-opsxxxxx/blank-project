import logging
import os
import requests

log = logging.getLogger("providers.instagram")


class InstagramProvider:
    name = "instagram"

    def __init__(self):
        self.user_id = os.getenv("IG_USER_ID", "")
        self.access_token = os.getenv("FB_ACCESS_TOKEN", "")
        # For simple posting we require an image URL (IG doesn't allow text-only)
        self.image_url = os.getenv("IG_IMAGE_URL", "")

    def post(self, text: str):
        if not self.user_id or not self.access_token:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "IG_USER_ID or FB_ACCESS_TOKEN missing"}}
        if not self.image_url:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "IG_IMAGE_URL missing (Instagram requires media)"}}
        try:
            # Step 1: Create media container
            create_url = f"https://graph.facebook.com/v19.0/{self.user_id}/media"
            create_params = {"image_url": self.image_url, "caption": text, "access_token": self.access_token}
            create_resp = requests.post(create_url, data=create_params, timeout=30)
            create_resp.raise_for_status()
            creation_id = create_resp.json().get("id")

            # Step 2: Publish the media
            publish_url = f"https://graph.facebook.com/v19.0/{self.user_id}/media_publish"
            publish_params = {"creation_id": creation_id, "access_token": self.access_token}
            publish_resp = requests.post(publish_url, data=publish_params, timeout=30)
            publish_resp.raise_for_status()

            return {"provider": self.name, "status": "ok", "detail": {"creation_id": creation_id}}
        except Exception as e:
            log.error(f"Instagram post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
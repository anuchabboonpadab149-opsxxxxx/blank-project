import logging
import os
import requests

log = logging.getLogger("providers.discord")


class DiscordProvider:
    name = "discord"

    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")

    def post(self, text: str):
        if not self.webhook_url:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "DISCORD_WEBHOOK_URL missing"}}
        try:
            payload = {"content": text}
            resp = requests.post(self.webhook_url, json=payload, timeout=20)
            if 200 <= resp.status_code < 300:
                return {"provider": self.name, "status": "ok", "detail": {"status_code": resp.status_code}}
            else:
                return {"provider": self.name, "status": "error", "detail": {"status_code": resp.status_code, "text": resp.text}}
        except Exception as e:
            log.error(f"Discord post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
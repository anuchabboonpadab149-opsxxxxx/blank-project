import os
import logging
import requests

log = logging.getLogger("providers.line")


class LineProvider:
    name = "line"

    def __init__(self):
        self.channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

    def post(self, text: str):
        if not self.channel_token:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "LINE_CHANNEL_ACCESS_TOKEN missing"}}
        try:
            # Broadcast message to all friends of the bot
            url = "https://api.line.me/v2/bot/message/broadcast"
            headers = {
                "Authorization": f"Bearer {self.channel_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": [
                    {"type": "text", "text": text}
                ]
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            resp.raise_for_status()
            return {"provider": self.name, "status": "ok", "detail": resp.json() if resp.text else {}}
        except Exception as e:
            log.error(f"LINE post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
import logging
import os
import requests

log = logging.getLogger("providers.line")


class LineProvider:
    name = "line"

    def __init__(self):
        self.token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")

    def post(self, text: str):
        if not self.token:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "LINE_CHANNEL_ACCESS_TOKEN missing"}}
        try:
            url = "https://api.line.me/v2/bot/message/broadcast"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
            payload = {
                "messages": [{"type": "text", "text": text}],
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            # LINE returns 200 with empty body on success
            if resp.status_code == 200:
                return {"provider": self.name, "status": "ok", "detail": {"status_code": 200}}
            else:
                return {"provider": self.name, "status": "error", "detail": {"status_code": resp.status_code, "text": resp.text}}
        except Exception as e:
            log.error(f"LINE post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
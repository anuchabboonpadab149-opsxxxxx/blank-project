import logging
import os
import requests

log = logging.getLogger("providers.telegram")


class TelegramProvider:
    name = "telegram"

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID", "")  # e.g., @channelusername or numeric ID

    def post(self, text: str):
        if not self.bot_token or not self.chat_id:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID missing"}}
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": text}
            resp = requests.post(url, json=payload, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {"provider": self.name, "status": "ok", "detail": data}
        except Exception as e:
            log.error(f"Telegram post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
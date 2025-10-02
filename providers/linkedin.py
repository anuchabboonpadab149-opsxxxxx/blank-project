import logging
import os
import requests

log = logging.getLogger("providers.linkedin")


class LinkedInProvider:
    name = "linkedin"

    def __init__(self):
        self.access_token = os.getenv("LI_ACCESS_TOKEN", "")
        self.organization_urn = os.getenv("LI_ORG_URN", "")  # e.g., "urn:li:organization:123456"

    def post(self, text: str):
        if not self.access_token or not self.organization_urn:
            return {"provider": self.name, "status": "skipped", "detail": {"reason": "LI_ACCESS_TOKEN or LI_ORG_URN missing"}}
        try:
            url = "https://api.linkedin.com/v2/ugcPosts"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
            }
            payload = {
                "author": self.organization_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return {"provider": self.name, "status": "ok", "detail": data}
        except Exception as e:
            log.error(f"LinkedIn post failed: {e}", exc_info=True)
            return {"provider": self.name, "status": "error", "detail": {"error": str(e)}}
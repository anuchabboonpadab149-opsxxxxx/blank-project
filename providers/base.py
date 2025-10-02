import logging
from typing import Optional

log = logging.getLogger("providers.base")


class ProviderResult:
    def __init__(self, name: str, status: str, detail: Optional[dict] = None):
        self.name = name
        self.status = status  # "ok" or "error" or "skipped"
        self.detail = detail or {}

    def to_dict(self):
        return {"provider": self.name, "status": self.status, "detail": self.detail}


class BaseProvider:
    name = "base"

    def post(self, text: str) -> ProviderResult:
        raise NotImplementedError
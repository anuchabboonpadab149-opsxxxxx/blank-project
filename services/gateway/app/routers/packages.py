import os
import httpx
from fastapi import APIRouter

router = APIRouter()
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment:8002")


@router.get("/packages")
def list_packages():
    with httpx.Client(timeout=10) as client:
        r = client.get(f"{PAYMENT_SERVICE_URL}/internal/packages", headers={"X-Internal-Token": os.getenv("INTERNAL_TOKEN", "internal-secret")})
        r.raise_for_status()
        return r.json()
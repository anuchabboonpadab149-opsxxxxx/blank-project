import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import require_admin

router = APIRouter()
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment:8002")
FORTUNE_SERVICE_URL = os.getenv("FORTUNE_SERVICE_URL", "http://fortune:8003")
CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://credit:8001")


@router.post("/payment/confirm")
def confirm_payment(transaction_id: str, user_id: str, credits_to_add: int, _=Depends(require_admin)):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{PAYMENT_SERVICE_URL}/internal/payment/confirm",
            json={"transaction_id": transaction_id, "user_id": user_id, "credits_to_add": credits_to_add},
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=r.text)
        return r.json()


# Content management
@router.post("/content/source")
def upsert_source(name: str, type: str, upright_prob: float | None = None, allowed_deck: str | None = None, _=Depends(require_admin)):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/admin/source",
            json={"name": name, "type": type, "upright_prob": upright_prob, "allowed_deck": allowed_deck},
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.post("/content/sen-si")
def add_sensi_content(source_id: int, slip_number: int, verse_content: str, fate_summary: str, _=Depends(require_admin)):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/admin/sen-si",
            json={"source_id": source_id, "slip_number": slip_number, "verse_content": verse_content, "fate_summary": fate_summary},
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.post("/content/tarot")
def add_tarot_content(card_name: str, meaning_upright: str, meaning_reversed: str, _=Depends(require_admin)):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/admin/tarot",
            json={"card_name": card_name, "meaning_upright": meaning_upright, "meaning_reversed": meaning_reversed},
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        return r.json()


@router.get("/dashboard")
def dashboard(_=Depends(require_admin)):
    headers = {"X-Internal-Token": INTERNAL_TOKEN}
    with httpx.Client(timeout=10) as client:
        pay = client.get(f"{PAYMENT_SERVICE_URL}/internal/admin/stats", headers=headers).json()
        cred = client.get(f"{CREDIT_SERVICE_URL}/internal/admin/stats", headers=headers).json()
        fort = client.get(f"{FORTUNE_SERVICE_URL}/internal/admin/stats", headers=headers).json()
        return {"payment": pay, "credit": cred, "fortune": fort}
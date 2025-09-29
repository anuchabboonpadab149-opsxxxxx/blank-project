import os
import httpx
from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..schemas import CreditBalanceResponse, HistoryResponse

router = APIRouter()

CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://credit:8001")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment:8002")
FORTUNE_SERVICE_URL = os.getenv("FORTUNE_SERVICE_URL", "http://fortune:8003")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")


@router.get("/credits", response_model=CreditBalanceResponse)
def get_credits(user=Depends(get_current_user)):
    with httpx.Client(timeout=10) as client:
        r = client.get(
            f"{CREDIT_SERVICE_URL}/internal/credits/{user.id}",
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        data = r.json()
        return CreditBalanceResponse(credit_balance=data.get("balance", 0))


@router.get("/history/all", response_model=HistoryResponse)
def get_history(user=Depends(get_current_user)):
    headers = {"X-Internal-Token": INTERNAL_TOKEN}
    with httpx.Client(timeout=15) as client:
        txs = client.get(f"{PAYMENT_SERVICE_URL}/internal/payment/user-history/{user.id}", headers=headers).json()
        fortunes = client.get(f"{FORTUNE_SERVICE_URL}/internal/fortune/user-history/{user.id}", headers=headers).json()
        return HistoryResponse(buy_history=txs, fortune_history=fortunes)
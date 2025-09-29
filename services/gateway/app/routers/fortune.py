import os
import httpx
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import get_current_user
from ..schemas import (
    FortuneSourceOut,
    FortuneDrawRequest,
    FortuneDrawSuccess,
    FortuneDrawError,
    TarotMultiDrawRequest,
    TarotMultiDrawResponse,
    TarotCardOut,
)

router = APIRouter()

CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://credit:8001")
FORTUNE_SERVICE_URL = os.getenv("FORTUNE_SERVICE_URL", "http://fortune:8003")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")


@router.get("/sources", response_model=list[FortuneSourceOut])
def list_sources():
    with httpx.Client(timeout=10) as client:
        r = client.get(f"{FORTUNE_SERVICE_URL}/internal/fortune/sources", headers={"X-Internal-Token": INTERNAL_TOKEN})
        r.raise_for_status()
        return r.json()


@router.post("/draw", responses={200: {"model": FortuneDrawSuccess}, 402: {"model": FortuneDrawError}})
def draw(payload: FortuneDrawRequest, user=Depends(get_current_user)):
    headers = {"X-Internal-Token": INTERNAL_TOKEN}
    with httpx.Client(timeout=15) as client:
        # deduct one credit
        deduct = client.post(
            f"{CREDIT_SERVICE_URL}/internal/credits/deduct",
            json={"user_id": user.id, "amount": 1, "reason": "Draw Fortune"},
            headers=headers,
        )
        if deduct.status_code != 200 or not deduct.json().get("success"):
            return {"error": "Insufficient credits"}
        new_balance = deduct.json().get("new_balance", 0)

        # execute fortune
        res = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/fortune/execute",
            json={"user_id": user.id, "source_id": payload.source_id},
            headers=headers,
        )
        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Fortune service unavailable")
        data = res.json()
        # record
        record = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/fortune/record",
            json={
                "user_id": user.id,
                "source_id": payload.source_id,
                "result_key": data["result_key"],
                "reading_date": datetime.utcnow().isoformat(),
                "verse": data.get("verse"),
                "summary": data.get("summary"),
            },
            headers=headers,
        )
        history_id = record.json().get("fortune_history_id")
        return FortuneDrawSuccess(
            fortune_id=history_id,
            result_key=data["result_key"],
            verse_content=data.get("verse"),
            fate_summary=data.get("summary"),
            new_credit_balance=new_balance,
        )


@router.post("/tarot/draw-multi", response_model=TarotMultiDrawResponse)
def tarot_draw_multi(payload: TarotMultiDrawRequest, user=Depends(get_current_user)):
    headers = {"X-Internal-Token": INTERNAL_TOKEN}
    count = payload.count
    if count not in (5, 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="count must be 5 or 10")
    cost = 1 if count == 5 else 2
    with httpx.Client(timeout=20) as client:
        # deduct credits
        deduct = client.post(
            f"{CREDIT_SERVICE_URL}/internal/credits/deduct",
            json={"user_id": user.id, "amount": cost, "reason": f"Tarot x{count}"},
            headers=headers,
        )
        if deduct.status_code != 200 or not deduct.json().get("success"):
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail="Insufficient credits")
        new_balance = deduct.json().get("new_balance", 0)

        # execute multi
        res = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/fortune/tarot-multi",
            json={"source_id": payload.source_id, "count": count},
            headers=headers,
        )
        if res.status_code != 200:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Fortune service unavailable")
        data = res.json()

        # record one combined entry
        record = client.post(
            f"{FORTUNE_SERVICE_URL}/internal/fortune/record",
            json={
                "user_id": user.id,
                "source_id": payload.source_id,
                "result_key": data.get("result_key"),
                "reading_date": datetime.utcnow().isoformat(),
                "verse": data.get("verse"),
                "summary": None,
            },
            headers=headers,
        )
        history_id = record.json().get("fortune_history_id")
        cards = [TarotCardOut(**c) for c in data.get("cards", [])]
        return TarotMultiDrawResponse(
            fortune_id=history_id,
            result_key=data.get("result_key"),
            cards=cards,
            new_credit_balance=new_balance,
        )
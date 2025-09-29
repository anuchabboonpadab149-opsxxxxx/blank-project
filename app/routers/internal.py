from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, Depends, status
from sqlalchemy.orm import Session

from ..db import (
    get_db,
    UserCredit,
    Transaction,
    TransactionStatusEnum,
    Package,
    FortuneSource,
    FortuneContent,
    TarotContent,
    FortuneHistory,
)
from ..schemas import (
    InternalCreditAdjustRequest,
    InternalCreditAdjustResponse,
    InternalCreditGetResponse,
    InternalPaymentProcessSuccessRequest,
    InternalPaymentProcessSuccessResponse,
    InternalPaymentLookupResponse,
    InternalFortuneExecuteRequest,
    InternalFortuneExecuteResponse,
    InternalFortuneRecordRequest,
    InternalFortuneRecordResponse,
)
from ..utils import is_internal_authorized

router = APIRouter()


def require_internal(auth_header: str | None):
    if not is_internal_authorized(auth_header):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized internal call")


@router.post("/credits/deduct", response_model=InternalCreditAdjustResponse)
def internal_deduct(
    payload: InternalCreditAdjustRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    if payload.amount <= 0:
        return InternalCreditAdjustResponse(success=False, error="Invalid amount")
    credit = db.query(UserCredit).filter(UserCredit.user_id == payload.user_id).with_for_update().first()
    if not credit or credit.balance < payload.amount:
        return InternalCreditAdjustResponse(success=False, error="Insufficient credits")
    credit.balance -= payload.amount
    db.commit()
    return InternalCreditAdjustResponse(success=True, new_balance=credit.balance)


@router.post("/credits/add", response_model=InternalCreditAdjustResponse)
def internal_add(
    payload: InternalCreditAdjustRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    if payload.amount <= 0:
        return InternalCreditAdjustResponse(success=False, error="Invalid amount")
    credit = db.query(UserCredit).filter(UserCredit.user_id == payload.user_id).with_for_update().first()
    if not credit:
        credit = UserCredit(user_id=payload.user_id, balance=0)
        db.add(credit)
    credit.balance += payload.amount
    db.commit()
    return InternalCreditAdjustResponse(success=True, new_balance=credit.balance)


@router.get("/credits/{user_id}", response_model=InternalCreditGetResponse)
def internal_get_credits(
    user_id: str,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
    return InternalCreditGetResponse(balance=credit.balance if credit else 0)


@router.post("/payment/process-success", response_model=InternalPaymentProcessSuccessResponse)
def internal_payment_success(
    payload: InternalPaymentProcessSuccessRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    tx = db.query(Transaction).filter(Transaction.id == payload.transaction_id, Transaction.user_id == payload.user_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    tx.status = TransactionStatusEnum.CONFIRMED
    # Add credits
    credit = db.query(UserCredit).filter(UserCredit.user_id == payload.user_id).with_for_update().first()
    if not credit:
        credit = UserCredit(user_id=payload.user_id, balance=0)
        db.add(credit)
    credit.balance += payload.credits_to_add
    db.commit()
    return InternalPaymentProcessSuccessResponse(status="CONFIRMED", credits_added=payload.credits_to_add)


@router.get("/payment/lookup/{tx_id}", response_model=InternalPaymentLookupResponse)
def internal_payment_lookup(
    tx_id: str,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return InternalPaymentLookupResponse(transaction_id=tx.id, status=tx.status, user_id=tx.user_id)


@router.post("/fortune/execute", response_model=InternalFortuneExecuteResponse)
def internal_fortune_execute(
    payload: InternalFortuneExecuteRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    src = db.query(FortuneSource).filter(FortuneSource.id == payload.source_id).first()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    if src.type == "Sen_Si":
        options = db.query(FortuneContent).filter(FortuneContent.source_id == src.id).all()
        import random

        if not options:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No content")
        choice = random.choice(options)
        return InternalFortuneExecuteResponse(
            result_key=f"ใบที่ {choice.slip_number}",
            verse=choice.verse_content,
            summary=choice.fate_summary,
        )
    else:
        cards = db.query(TarotContent).all()
        import random

        if not cards:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No tarot content")
        card = random.choice(cards)
        upright = random.choice([True, False])
        return InternalFortuneExecuteResponse(
            result_key=card.card_name + (" (Upright)" if upright else " (Reversed)"),
            verse=card.meaning_upright if upright else card.meaning_reversed,
            summary=None,
        )


@router.post("/fortune/record", response_model=InternalFortuneRecordResponse)
def internal_fortune_record(
    payload: InternalFortuneRecordRequest,
    db: Session = Depends(get_db),
    authorization: str | None = Header(default=None, alias="X-Internal-Token"),
):
    require_internal(authorization)
    history = FortuneHistory(
        user_id=payload.user_id,
        source_id=payload.source_id,
        source_type=("Sen_Si" if "ใบที่" in payload.result_key else "Tarot"),
        result_key=payload.result_key,
        reading_date=payload.reading_date or datetime.utcnow(),
    )
    db.add(history)
    db.commit()
    return InternalFortuneRecordResponse(fortune_history_id=history.id)
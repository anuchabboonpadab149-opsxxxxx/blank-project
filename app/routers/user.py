from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db, User, UserCredit, Transaction, FortuneHistory
from ..schemas import CreditBalanceResponse, HistoryResponse, BuyHistoryItem, FortuneHistoryItem

router = APIRouter()


@router.get("/credits", response_model=CreditBalanceResponse)
def get_credits(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    credits = db.query(UserCredit).filter(UserCredit.user_id == user.id).first()
    balance = credits.balance if credits else 0
    return CreditBalanceResponse(credit_balance=balance)


@router.get("/history/all", response_model=HistoryResponse)
def get_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txs = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    buys = [
        BuyHistoryItem(
            transaction_id=t.id, package_id=t.package_id, amount=t.amount, status=t.status, created_at=t.created_at
        )
        for t in txs
    ]
    forts = (
        db.query(FortuneHistory)
        .filter(FortuneHistory.user_id == user.id)
        .order_by(FortuneHistory.reading_date.desc())
        .all()
    )
    fortunes = [
        FortuneHistoryItem(
            id=f.id,
            source_id=f.source_id,
            source_type=f.source_type,
            result_key=f.result_key,
            reading_date=f.reading_date,
            verse_content=f.verse_content,
            fate_summary=f.fate_summary,
        )
        for f in forts
    ]
    return HistoryResponse(buy_history=buys, fortune_history=fortunes)
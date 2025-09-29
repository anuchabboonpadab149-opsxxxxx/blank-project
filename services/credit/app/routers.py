import os
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from .db import get_db, Base, engine, UserCredit

Base.metadata.create_all(bind=engine)
router = APIRouter()
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")


def require_internal(token: str | None):
    if token != INTERNAL_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized internal call")


@router.post("/internal/credits/deduct")
def deduct(payload: dict, db: Session = Depends(get_db), authorization: str | None = Header(default=None, alias="X-Internal-Token")):
    require_internal(authorization)
    user_id = payload.get("user_id")
    amount = int(payload.get("amount", 0))
    if amount <= 0:
        return {"success": False, "error": "Invalid amount"}
    credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).with_for_update().first()
    if not credit or credit.balance < amount:
        return {"success": False, "error": "Insufficient credits"}
    credit.balance -= amount
    db.commit()
    return {"success": True, "new_balance": credit.balance}


@router.post("/internal/credits/add")
def add(payload: dict, db: Session = Depends(get_db), authorization: str | None = Header(default=None, alias="X-Internal-Token")):
    require_internal(authorization)
    user_id = payload.get("user_id")
    amount = int(payload.get("amount", 0))
    if amount <= 0:
        return {"success": False, "error": "Invalid amount"}
    credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).with_for_update().first()
    if not credit:
        credit = UserCredit(user_id=user_id, balance=0)
        db.add(credit)
    credit.balance += amount
    db.commit()
    return {"success": True, "new_balance": credit.balance}


@router.get("/internal/credits/{user_id}")
def get_balance(user_id: str, db: Session = Depends(get_db), authorization: str | None = Header(default=None, alias="X-Internal-Token")):
    require_internal(authorization)
    credit = db.query(UserCredit).filter(UserCredit.user_id == user_id).first()
    return {"balance": credit.balance if credit else 0}


@router.get("/internal/admin/stats")
def admin_stats(authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    rows = db.query(UserCredit).all()
    total_accounts = len(rows)
    total_balance = sum(r.balance for r in rows)
    return {"total_accounts": total_accounts, "total_balance": total_balance}
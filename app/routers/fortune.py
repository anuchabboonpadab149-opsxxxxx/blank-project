import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db, FortuneSource, FortuneContent, TarotContent, User, UserCredit, FortuneHistory
from ..schemas import FortuneSourceOut, FortuneDrawRequest, FortuneDrawSuccess, FortuneDrawError

router = APIRouter()


@router.get("/sources", response_model=list[FortuneSourceOut])
def list_sources(db: Session = Depends(get_db)):
    srcs = db.query(FortuneSource).all()
    return [FortuneSourceOut(id=s.id, name=s.name, type=s.type) for s in srcs]


@router.post("/draw", responses={200: {"model": FortuneDrawSuccess}, 402: {"model": FortuneDrawError}})
def draw_fortune(
    payload: FortuneDrawRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Deduct 1 credit
    credit = db.query(UserCredit).filter(UserCredit.user_id == user.id).with_for_update().first()
    if credit is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Credit account missing")
    if credit.balance < 1:
        return {"error": "Insufficient credits"}
    credit.balance -= 1

    # Execute fortune
    src = db.query(FortuneSource).filter(FortuneSource.id == payload.source_id).first()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    verse_content = None
    fate_summary = None
    result_key = ""

    if src.type == "Sen_Si":
        options = db.query(FortuneContent).filter(FortuneContent.source_id == src.id).all()
        if not options:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No fortune content")
        choice = random.choice(options)
        result_key = f"ใบที่ {choice.slip_number}"
        verse_content = choice.verse_content
        fate_summary = choice.fate_summary
    else:
        cards = db.query(TarotContent).all()
        if not cards:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No tarot content")
        card = random.choice(cards)
        upright = random.choice([True, False])
        result_key = card.card_name + (" (Upright)" if upright else " (Reversed)")
        verse_content = card.meaning_upright if upright else card.meaning_reversed
        fate_summary = None

    # Record history
    history = FortuneHistory(
        user_id=user.id,
        source_id=src.id,
        source_type=src.type,
        result_key=result_key,
        verse_content=verse_content,
        fate_summary=fate_summary,
        reading_date=datetime.utcnow(),
    )
    db.add(history)
    db.commit()
    new_balance = credit.balance
    return FortuneDrawSuccess(
        fortune_id=history.id,
        result_key=result_key,
        verse_content=verse_content,
        fate_summary=fate_summary,
        new_credit_balance=new_balance,
    )
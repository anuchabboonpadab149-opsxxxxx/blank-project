import os
import random
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from .db import Base, engine, get_db, FortuneSource, FortuneContent, TarotContent, FortuneHistory

Base.metadata.create_all(bind=engine)

router = APIRouter()
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")
DEFAULT_UPRIGHT_PROB = float(os.getenv("TAROT_UPRIGHT_PROB", "0.5"))

MAJOR_ARCANA = {
    "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
    "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
    "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
    "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement", "The World",
}


def require_internal(token: str | None):
    if token != INTERNAL_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized internal call")


@router.get("/internal/fortune/sources")
def sources(authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    rows = db.execute(select(FortuneSource)).scalars().all()
    return [{"id": r.id, "name": r.name, "type": r.type} for r in rows]


@router.post("/internal/fortune/execute")
def execute(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    source_id = int(payload.get("source_id"))
    src = db.query(FortuneSource).filter(FortuneSource.id == source_id).first()
    if not src:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

    if src.type == "Sen_Si":
        options = db.query(FortuneContent).filter(FortuneContent.source_id == src.id).all()
        if not options:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No fortune content")
        choice = random.choice(options)
        return {
            "result_key": f"ใบที่ {choice.slip_number}",
            "verse": choice.verse_content,
            "summary": choice.fate_summary,
        }
    else:
        # tarot
        upright_prob = src.upright_prob if src.upright_prob is not None else DEFAULT_UPRIGHT_PROB
        allowed_deck = src.allowed_deck
        query = db.query(TarotContent)
        if allowed_deck:
            if allowed_deck == "Major":
                query = query.filter(TarotContent.card_name.in_(list(MAJOR_ARCANA)))
            else:
                names = [n.strip() for n in allowed_deck.split("|") if n.strip()]
                if names:
                    query = query.filter(TarotContent.card_name.in_(names))

        cards = query.all()
        if not cards:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No tarot content")
        card = random.choice(cards)
        upright = random.random() < upright_prob
        return {
            "result_key": card.card_name + (" (Upright)" if upright else " (Reversed)"),
            "verse": card.meaning_upright if upright else card.meaning_reversed,
            "summary": None,
        }


@router.post("/internal/fortune/record")
def record(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    history = FortuneHistory(
        user_id=payload.get("user_id"),
        source_id=int(payload.get("source_id")),
        source_type=("Sen_Si" if "ใบที่" in payload.get("result_key", "") else "Tarot"),
        result_key=payload.get("result_key"),
        verse_content=payload.get("verse"),
        fate_summary=payload.get("summary"),
        reading_date=datetime.fromisoformat(payload.get("reading_date")) if payload.get("reading_date") else datetime.utcnow(),
    )
    db.add(history)
    db.commit()
    return {"fortune_history_id": history.id}


@router.get("/internal/fortune/user-history/{user_id}")
def user_history(user_id: str, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    rows = db.query(FortuneHistory).filter(FortuneHistory.user_id == user_id).order_by(FortuneHistory.reading_date.desc()).all()
    return [
        {
            "id": r.id,
            "source_id": r.source_id,
            "source_type": r.source_type,
            "result_key": r.result_key,
            "reading_date": r.reading_date.isoformat(),
            "verse_content": r.verse_content,
            "fate_summary": r.fate_summary,
        }
        for r in rows
    ]


# Admin endpoints
@router.post("/internal/admin/source")
def admin_upsert_source(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    name = payload.get("name")
    type_ = payload.get("type")
    upright_prob = payload.get("upright_prob")
    allowed_deck = payload.get("allowed_deck")
    src = db.query(FortuneSource).filter(FortuneSource.name == name, FortuneSource.type == type_).first()
    if not src:
        src = FortuneSource(name=name, type=type_, upright_prob=upright_prob, allowed_deck=allowed_deck)
        db.add(src)
    else:
        src.upright_prob = upright_prob
        src.allowed_deck = allowed_deck
    db.commit()
    db.refresh(src)
    return {"id": src.id, "name": src.name, "type": src.type, "upright_prob": src.upright_prob, "allowed_deck": src.allowed_deck}


@router.post("/internal/admin/sen-si")
def admin_add_sensi(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    fc = FortuneContent(
        source_id=int(payload.get("source_id")),
        slip_number=int(payload.get("slip_number")),
        verse_content=payload.get("verse_content"),
        fate_summary=payload.get("fate_summary"),
    )
    db.add(fc)
    db.commit()
    return {"id": fc.id}


@router.post("/internal/admin/tarot")
def admin_add_tarot(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    tc = TarotContent(
        card_name=payload.get("card_name"),
        meaning_upright=payload.get("meaning_upright"),
        meaning_reversed=payload.get("meaning_reversed"),
    )
    db.add(tc)
    db.commit()
    return {"id": tc.id}


@router.get("/internal/admin/stats")
def admin_stats(authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    total_sources = db.query(FortuneSource).count()
    total_sensi = db.query(FortuneContent).count()
    total_tarot_cards = db.query(TarotContent).count()
    total_fortunes = db.query(FortuneHistory).count()
    sen_si_count = db.query(FortuneHistory).filter(FortuneHistory.source_type == "Sen_Si").count()
    tarot_count = db.query(FortuneHistory).filter(FortuneHistory.source_type == "Tarot").count()
    return {
        "total_sources": total_sources,
        "total_sen_si_content": total_sensi,
        "total_tarot_cards": total_tarot_cards,
        "total_fortunes": total_fortunes,
        "by_type": {"Sen_Si": sen_si_count, "Tarot": tarot_count},
    }
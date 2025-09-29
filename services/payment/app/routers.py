import os
from io import BytesIO
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlalchemy.orm import Session
from promptpay import qrcode as pp_qrcode
import qrcode

from .db import Base, engine, get_db, Package, Transaction

Base.metadata.create_all(bind=engine)

router = APIRouter()

INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")
PROMPTPAY_ID = os.getenv("PROMPTPAY_ID", "0916974995")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8002")
CREDIT_SERVICE_URL = os.getenv("CREDIT_SERVICE_URL", "http://credit:8001")


def require_internal(token: str | None):
    if token != INTERNAL_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized internal call")


@router.get("/internal/packages")
def list_packages(authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    pkgs = db.query(Package).all()
    return [
        {"id": p.id, "name": p.name, "price": p.price, "credits": p.credits, "is_best_seller": p.is_best_seller}
        for p in pkgs
    ]


@router.post("/internal/payment/create")
def payment_create(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    user_id = payload.get("user_id")
    package_id = payload.get("package_id")
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    tx = Transaction(user_id=user_id, package_id=pkg.id, amount=pkg.price, status="CREATED")
    db.add(tx)
    db.commit()
    db.refresh(tx)

    payload_text = pp_qrcode.generate_payload(PROMPTPAY_ID, tx.amount)
    qr_url = f"{PUBLIC_BASE_URL}/internal/payment/qrcode/{tx.id}.png"
    return {"transaction_id": tx.id, "amount": tx.amount, "qr_code_url": qr_url, "qr_payload": payload_text}


@router.get("/internal/payment/qrcode/{tx_id}.png")
def payment_qrcode(tx_id: str, authorization: str | None = Header(default=None, alias="X-Internal-Token")):
    # For public access of QR image via browser, do not require token
    # But keep it internal by default if behind gateway. Here we allow public by not checking token.
    # Generate on the fly from transaction amount and PROMPTPAY_ID
    from .db import SessionLocal, Transaction

    with SessionLocal() as db:
        tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
        if not tx:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        payload_text = pp_qrcode.generate_payload(PROMPTPAY_ID, tx.amount)
        img = qrcode.make(payload_text)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")


@router.post("/internal/payment/verify")
def payment_verify(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    tx_id = payload.get("transaction_id")
    user_id = payload.get("user_id")
    slip_url = payload.get("slip_image_url")
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if tx.status == "CONFIRMED":
        return {"status": "Success", "message": "Already confirmed"}
    tx.status = "PENDING"
    tx.slip_image_url = slip_url
    db.commit()
    return {"status": "Pending", "message": "Payment under review"}


@router.post("/internal/payment/confirm")
def payment_confirm(payload: dict, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    tx_id = payload.get("transaction_id")
    user_id = payload.get("user_id")
    credits_to_add = int(payload.get("credits_to_add", 0))
    tx = db.query(Transaction).filter(Transaction.id == tx_id, Transaction.user_id == user_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if tx.status == "CONFIRMED":
        return {"status": "CONFIRMED", "credits_added": 0}
    # If credits_to_add not provided, use package credits
    if credits_to_add <= 0:
        pkg = db.query(Package).filter(Package.id == tx.package_id).first()
        credits_to_add = pkg.credits if pkg else 0

    # call credit service
    import httpx
    r = httpx.post(
        f"{CREDIT_SERVICE_URL}/internal/credits/add",
        json={"user_id": user_id, "amount": credits_to_add, "reason": "Package Purchase"},
        headers={"X-Internal-Token": INTERNAL_TOKEN},
        timeout=10,
    )
    if r.status_code != 200 or not r.json().get("success"):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Credit service failed")

    tx.status = "CONFIRMED"
    db.commit()
    return {"status": "CONFIRMED", "credits_added": credits_to_add}


@router.get("/internal/payment/lookup/{tx_id}")
def payment_lookup(tx_id: str, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return {"transaction_id": tx.id, "status": tx.status, "user_id": tx.user_id}


@router.get("/internal/payment/user-history/{user_id}")
def user_history(user_id: str, authorization: str | None = Header(default=None, alias="X-Internal-Token"), db: Session = Depends(get_db)):
    require_internal(authorization)
    txs = db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.created_at.desc()).all()
    return [
        {"transaction_id": t.id, "package_id": t.package_id, "amount": t.amount, "status": t.status, "created_at": t.created_at.isoformat()}
        for t in txs
    ]
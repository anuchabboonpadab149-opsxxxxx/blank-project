from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db, Package, Transaction, User
from ..schemas import PaymentCreateRequest, PaymentCreateResponse, PaymentVerifyRequest, PaymentVerifyResponse
from ..utils import promptpay_qr_url_placeholder

router = APIRouter()


@router.get("/packages")
def list_packages(db: Session = Depends(get_db)):
    pkgs = db.query(Package).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "credits": p.credits,
            "is_best_seller": p.is_best_seller,
        }
        for p in pkgs
    ]


@router.post("/payment/create", response_model=PaymentCreateResponse)
def payment_create(
    payload: PaymentCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pkg = db.query(Package).filter(Package.id == payload.package_id).first()
    if not pkg:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    tx = Transaction(user_id=user.id, package_id=pkg.id, amount=pkg.price, status="CREATED")
    db.add(tx)
    db.commit()
    db.refresh(tx)
    qr_url = promptpay_qr_url_placeholder(tx.id, tx.amount)
    return PaymentCreateResponse(transaction_id=tx.id, amount=tx.amount, qr_code_url=qr_url)


@router.post("/payment/verify", response_model=PaymentVerifyResponse)
def payment_verify(
    payload: PaymentVerifyRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tx = db.query(Transaction).filter(Transaction.id == payload.transaction_id, Transaction.user_id == user.id).first()
    if not tx:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    if tx.status == "CONFIRMED":
        return PaymentVerifyResponse(status="Success", message="Already confirmed")
    # Mark pending and store slip image url
    tx.status = "PENDING"
    tx.slip_image_url = payload.slip_image_url
    db.commit()
    return PaymentVerifyResponse(status="Pending", message="Payment under review")
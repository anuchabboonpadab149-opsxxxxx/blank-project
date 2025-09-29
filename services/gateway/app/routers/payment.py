import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from ..auth import get_current_user
from ..schemas import PaymentCreateRequest, PaymentCreateResponse, PaymentVerifyRequest, PaymentVerifyResponse

router = APIRouter()
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL", "http://payment:8002")
INTERNAL_TOKEN = os.getenv("INTERNAL_TOKEN", "internal-secret")


@router.post("/payment/create", response_model=PaymentCreateResponse)
def payment_create(payload: PaymentCreateRequest, request: Request, user=Depends(get_current_user)):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{PAYMENT_SERVICE_URL}/internal/payment/create",
            json={"package_id": payload.package_id, "user_id": user.id},
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=r.text)
        data = r.json()
        # rewrite qr_code_url to gateway proxy endpoint
        tx_id = data.get("transaction_id")
        gateway_base = str(request.base_url).rstrip("/")
        data["qr_code_url"] = f"{gateway_base}/payment/qrcode/{tx_id}.png"
        return PaymentCreateResponse(**data)


@router.get("/payment/qrcode/{tx_id}.png")
def proxy_qrcode(tx_id: str):
    # Fetch from payment service internal QR endpoint and return as PNG
    with httpx.Client(timeout=10) as client:
        r = client.get(f"{PAYMENT_SERVICE_URL}/internal/payment/qrcode/{tx_id}.png")
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail="QR not found")
        return Response(content=r.content, media_type="image/png")


@router.get("/payment/status/{tx_id}")
def payment_status(tx_id: str, user=Depends(get_current_user)):
    with httpx.Client(timeout=10) as client:
        r = client.get(
            f"{PAYMENT_SERVICE_URL}/internal/payment/lookup/{tx_id}",
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        data = r.json()
        if data.get("user_id") != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your transaction")
        return {"status": data.get("status")}


@router.post("/payment/verify", response_model=PaymentVerifyResponse)
def payment_verify(payload: PaymentVerifyRequest, user=Depends(get_current_user)):
    with httpx.Client(timeout=10) as client:
        r = client.post(
            f"{PAYMENT_SERVICE_URL}/internal/payment/verify",
            json={"transaction_id": payload.transaction_id, "user_id": user.id, "slip_image_url": payload.slip_image_url},
            headers={"X-Internal-Token": INTERNAL_TOKEN},
        )
        if r.status_code != 200:
            raise HTTPException(status_code=r.status_code, detail=r.text)
        data = r.json()
        return PaymentVerifyResponse(**data)
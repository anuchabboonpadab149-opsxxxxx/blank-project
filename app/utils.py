import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, expires_minutes: Optional[int] = None) -> tuple[str, int]:
    expires_in = expires_minutes or JWT_EXPIRES_MIN
    expire = datetime.utcnow() + timedelta(minutes=expires_in)
    payload = {"sub": user_id, "exp": expire}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)
    return token, expires_in


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload.get("sub")
    except Exception:
        return None


def is_internal_authorized(token: Optional[str]) -> bool:
    expected = os.getenv("INTERNAL_TOKEN", "internal-secret")
    return token == expected


def promptpay_qr_url_placeholder(transaction_id: str, amount: float) -> str:
    # In production, integrate PromptPay QR generator and file storage (S3, etc.)
    return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&amp;data=TX:{transaction_id}|AMT:{amount}"
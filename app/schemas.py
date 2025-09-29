from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# Auth
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    user_id: str
    token: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: str
    token: str
    expires_in: int


# User/Credits
class CreditBalanceResponse(BaseModel):
    credit_balance: int


# Packages
class PackageOut(BaseModel):
    id: int
    name: str
    price: float
    credits: int
    is_best_seller: bool


# Payment
class PaymentCreateRequest(BaseModel):
    package_id: int


class PaymentCreateResponse(BaseModel):
    transaction_id: str
    amount: float
    qr_code_url: str


class PaymentVerifyRequest(BaseModel):
    transaction_id: str
    slip_image_url: str


class PaymentVerifyResponse(BaseModel):
    status: str
    message: str


# Fortune
class FortuneSourceOut(BaseModel):
    id: int
    name: str
    type: str  # Sen_Si / Tarot


class FortuneDrawRequest(BaseModel):
    source_id: int


class FortuneDrawSuccess(BaseModel):
    fortune_id: str
    result_key: str
    verse_content: str | None = None
    fate_summary: str | None = None
    new_credit_balance: int


class FortuneDrawError(BaseModel):
    error: str


# History
class BuyHistoryItem(BaseModel):
    transaction_id: str
    package_id: int
    amount: float
    status: str
    created_at: datetime


class FortuneHistoryItem(BaseModel):
    id: str
    source_id: int
    source_type: str
    result_key: str
    reading_date: datetime
    verse_content: Optional[str] = None
    fate_summary: Optional[str] = None


class HistoryResponse(BaseModel):
    buy_history: List[BuyHistoryItem]
    fortune_history: List[FortuneHistoryItem]


# Internal service schemas
class InternalCreditAdjustRequest(BaseModel):
    user_id: str
    amount: int
    reason: str


class InternalCreditAdjustResponse(BaseModel):
    success: bool
    new_balance: Optional[int] = None
    error: Optional[str] = None


class InternalCreditGetResponse(BaseModel):
    balance: int


class InternalPaymentProcessSuccessRequest(BaseModel):
    user_id: str
    transaction_id: str
    credits_to_add: int


class InternalPaymentProcessSuccessResponse(BaseModel):
    status: str
    credits_added: int


class InternalPaymentLookupResponse(BaseModel):
    transaction_id: str
    status: str
    user_id: str


class InternalFortuneExecuteRequest(BaseModel):
    user_id: str
    source_id: int


class InternalFortuneExecuteResponse(BaseModel):
    result_key: str
    verse: Optional[str] = None
    summary: Optional[str] = None


class InternalFortuneRecordRequest(BaseModel):
    user_id: str
    source_id: int
    result_key: str
    reading_date: datetime


class InternalFortuneRecordResponse(BaseModel):
    fortune_history_id: str
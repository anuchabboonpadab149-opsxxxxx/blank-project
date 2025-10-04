import os
from typing import Optional

from sqlalchemy import create_engine, Integer, String, Text, Boolean, Float
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import OperationalError

DB_URL = os.getenv("DB_URL", "").strip()

_engine = None
_SessionLocal = None

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    pw_hash: Mapped[str] = mapped_column(String(128))
    salt: Mapped[str] = mapped_column(String(64))
    credits: Mapped[int] = mapped_column(Integer, default=0)
    created_ts: Mapped[float] = mapped_column(Float, default=0.0)
    last_login_ts: Mapped[Optional[float]] = mapped_column(Float, default=None)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(32), default="member")  # member|admin

class Topup(Base):
    __tablename__ = "topups"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    package_id: Mapped[str] = mapped_column(String(32))
    price: Mapped[int] = mapped_column(Integer)
    credits_on_approve: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), index=True)  # pending|approved
    slip_path: Mapped[Optional[str]] = mapped_column(String(255), default=None)
    created_ts: Mapped[float] = mapped_column(Float, default=0.0)
    approved_ts: Mapped[Optional[float]] = mapped_column(Float, default=None)
    approved_by: Mapped[Optional[str]] = mapped_column(String(64), default=None)

class History(Base):
    __tablename__ = "history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[float] = mapped_column(Float, index=True)
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    service: Mapped[str] = mapped_column(String(32), index=True)
    inputs: Mapped[str] = mapped_column(Text)   # json string
    result: Mapped[str] = mapped_column(Text)   # json string

class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ts: Mapped[float] = mapped_column(Float, index=True)
    type: Mapped[str] = mapped_column(String(16))  # add|deduct|topup_request
    user_id: Mapped[str] = mapped_column(String(64), index=True)
    delta: Mapped[int] = mapped_column(Integer, default=0)
    new_balance: Mapped[int] = mapped_column(Integer, default=0)
    reason: Mapped[Optional[str]] = mapped_column(String(64), default=None)
    meta: Mapped[Optional[str]] = mapped_column(Text, default=None)  # json string

def init_db() -> bool:
    global _engine, _SessionLocal
    if not DB_URL:
        return False
    _engine = create_engine(DB_URL, pool_pre_ping=True)
    _SessionLocal = sessionmaker(bind=_engine)
    try:
        Base.metadata.create_all(_engine)
    except OperationalError:
        # Possibly missing database; caller should ensure DB exists
        pass
    return True

def get_session():
    if not _SessionLocal:
        raise RuntimeError("DB not initialized")
    return _SessionLocal()
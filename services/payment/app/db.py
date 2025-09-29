import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payment.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class Package(Base):
    __tablename__ = "packages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    credits: Mapped[int] = mapped_column(Integer)
    is_best_seller: Mapped[bool] = mapped_column(Boolean, default=False)


class Transaction(Base):
    __tablename__ = "transactions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36))
    package_id: Mapped[int] = mapped_column(Integer, ForeignKey("packages.id"))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="CREATED")  # CREATED, PENDING, CONFIRMED
    slip_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    package: Mapped[Package] = relationship("Package")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_packages():
    from sqlalchemy import select
    with SessionLocal() as db:
        if not db.execute(select(Package)).first():
            db.add_all([
                Package(name="เริ่มต้น", price=29.0, credits=3, is_best_seller=False),
                Package(name="คุ้มค่า", price=99.0, credits=15, is_best_seller=True),
                Package(name="จัดเต็ม", price=199.0, credits=35, is_best_seller=False),
            ])
            db.commit()
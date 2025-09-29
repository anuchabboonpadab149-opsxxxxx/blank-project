import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, Integer, String, Text, Boolean, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    credits: Mapped["UserCredit"] = relationship("UserCredit", back_populates="user", uselist=False)
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
    fortunes: Mapped[list["FortuneHistory"]] = relationship("FortuneHistory", back_populates="user")


class UserCredit(Base):
    __tablename__ = "user_credits"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    balance: Mapped[int] = mapped_column(Integer, default=0)

    user: Mapped[User] = relationship("User", back_populates="credits")


class Package(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    price: Mapped[float] = mapped_column(Float)
    credits: Mapped[int] = mapped_column(Integer)
    is_best_seller: Mapped[bool] = mapped_column(Boolean, default=False)


class TransactionStatusEnum(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"  # reserved


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    package_id: Mapped[int] = mapped_column(Integer, ForeignKey("packages.id"))
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default=TransactionStatusEnum.CREATED)
    slip_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="transactions")
    package: Mapped[Package] = relationship("Package")


class FortuneSourceTypeEnum(str, Enum):
    Sen_Si = "Sen_Si"
    Tarot = "Tarot"


class FortuneSource(Base):
    __tablename__ = "fortune_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(20))  # 'Sen_Si' or 'Tarot'


class FortuneContent(Base):
    __tablename__ = "fortune_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("fortune_sources.id"))
    slip_number: Mapped[int] = mapped_column(Integer)
    verse_content: Mapped[str] = mapped_column(Text)
    fate_summary: Mapped[str] = mapped_column(String(255))

    source: Mapped[FortuneSource] = relationship("FortuneSource")


class TarotContent(Base):
    __tablename__ = "tarot_content"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_name: Mapped[str] = mapped_column(String(255))
    meaning_upright: Mapped[str] = mapped_column(Text)
    meaning_reversed: Mapped[str] = mapped_column(Text)


class FortuneHistory(Base):
    __tablename__ = "fortune_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"))
    source_id: Mapped[int] = mapped_column(Integer)
    source_type: Mapped[str] = mapped_column(String(20))  # 'Sen_Si' or 'Tarot'
    result_key: Mapped[str] = mapped_column(String(255))
    verse_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    fate_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship("User", back_populates="fortunes")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_initial_data():
    # Seed initial packages and sources if table empty
    from sqlalchemy import select
    with SessionLocal() as db:
        if not db.execute(select(Package)).first():
            db.add_all([
                Package(name="เริ่มต้น", price=29.0, credits=3, is_best_seller=False),
                Package(name="คุ้มค่า", price=99.0, credits=15, is_best_seller=True),
                Package(name="จัดเต็ม", price=199.0, credits=35, is_best_seller=False),
            ])
        if not db.execute(select(FortuneSource)).first():
            sen_si = FortuneSource(name="หลวงพ่อพระใส", type="Sen_Si")
            tarot = FortuneSource(name="อ.โทนี่สะท้อนกรรม", type="Tarot")
            db.add_all([sen_si, tarot])
            db.flush()
            # Seed a few sample sen-si slips
            db.add_all([
                FortuneContent(source_id=sen_si.id, slip_number=1, verse_content="ใบที่ ๑ ว่าสมมาตรปรารถนา...", fate_summary="ชะตาดี"),
                FortuneContent(source_id=sen_si.id, slip_number=2, verse_content="ใบที่ ๒ มีอุปสรรคบ้าง...", fate_summary="อุปสรรคเล็กน้อย"),
            ])
            # Seed a few tarot cards
            db.add_all([
                TarotContent(card_name="The Fool", meaning_upright="เริ่มต้นใหม่ อิสระ การผจญภัย", meaning_reversed="ความไม่ระมัดระวัง ความโง่เขลา"),
                TarotContent(card_name="The Magician", meaning_upright="พลังแห่งการสร้างสรรค์ การสื่อสาร", meaning_reversed="การหลอกลวง ความไม่มั่นคง"),
            ])
        db.commit()
import os
import uuid
from datetime import datetime

from sqlalchemy import create_engine, Integer, String, Text, Float, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fortune.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


class FortuneSource(Base):
    __tablename__ = "fortune_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(20))  # Sen_Si or Tarot
    upright_prob: Mapped[float | None] = mapped_column(Float, nullable=True)  # For Tarot only
    allowed_deck: Mapped[str | None] = mapped_column(String(255), nullable=True)  # e.g., "Major|The Fool|The Magician"


class FortuneContent(Base):
    __tablename__ = "fortune_content"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(Integer)
    slip_number: Mapped[int] = mapped_column(Integer)
    verse_content: Mapped[str] = mapped_column(Text)
    fate_summary: Mapped[str] = mapped_column(String(255))


class TarotContent(Base):
    __tablename__ = "tarot_content"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    card_name: Mapped[str] = mapped_column(String(255))
    meaning_upright: Mapped[str] = mapped_column(Text)
    meaning_reversed: Mapped[str] = mapped_column(Text)


class FortuneHistory(Base):
    __tablename__ = "fortune_history"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36))
    source_id: Mapped[int] = mapped_column(Integer)
    source_type: Mapped[str] = mapped_column(String(20))
    result_key: Mapped[str] = mapped_column(String(255))
    verse_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    fate_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    reading_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_sources_and_content():
    from sqlalchemy import select
    with SessionLocal() as db:
        if not db.execute(select(FortuneSource)).first():
            sen_si = FortuneSource(name="หลวงพ่อพระใส", type="Sen_Si")
            tarot = FortuneSource(name="อ.โทนี่สะท้อนกรรม", type="Tarot", upright_prob=None, allowed_deck=None)
            db.add_all([sen_si, tarot])
            db.flush()
            db.add_all([
                FortuneContent(source_id=sen_si.id, slip_number=1, verse_content="ใบที่ ๑ ว่าสมมาตรปรารถนา...", fate_summary="ชะตาดี"),
                FortuneContent(source_id=sen_si.id, slip_number=2, verse_content="ใบที่ ๒ มีอุปสรรคบ้าง...", fate_summary="อุปสรรคเล็กน้อย"),
            ])
            db.add_all([
                TarotContent(card_name="The Fool", meaning_upright="เริ่มต้นใหม่ อิสระ การผจญภัย", meaning_reversed="ความไม่ระมัดระวัง ความโง่เขลา"),
                TarotContent(card_name="The Magician", meaning_upright="พลังแห่งการสร้างสรรค์ การสื่อสาร", meaning_reversed="การหลอกลวง ความไม่มั่นคง"),
                TarotContent(card_name="The Lovers", meaning_upright="ความรัก การเลือก การสัมพันธ์", meaning_reversed="ความลังเล ความสัมพันธ์สั่นคลอน"),
            ])
            db.commit()
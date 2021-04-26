from datetime import datetime
from pytz import timezone, utc

from sqlalchemy import (
    Column,
    Integer,
    Date,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from .database import Base


class Diary(Base):
    __tablename__ = 'diary'

    KST = timezone('Asia/Seoul')
    now = datetime.utcnow()

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey('diary_users.name'))
    date = Column(Date, nullable=False)
    title = Column(String)
    content = Column(Text)
    image_type = Column(String)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc.localize(now).astimezone(KST)
    )

    creator = relationship("User", back_populates="diaries")


class User(Base):
    __tablename__ = 'diary_users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    email = Column(String)
    password = Column(String)

    diaries = relationship("Diary", back_populates="creator")
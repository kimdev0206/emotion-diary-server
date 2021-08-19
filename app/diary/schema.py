from typing import Dict, Optional, List
from datetime import date

from pydantic import BaseModel


class DiaryBase(BaseModel):
    user_id: str
    date: date

    class Config:
        orm_mode = True


class Diary(DiaryBase):
    title: str
    content: str
    image_type: str


class ShowDiary(BaseModel):
    body: Dict[str, List[Diary]] = {}


class DiaryYear(BaseModel):
    emotion_type: str
    year_count: int = 0
    color: Optional[str] = None


class ShowDiaryYear(BaseModel):
    body: Dict[str, List[DiaryYear]] = {}


class User(BaseModel):
    name: str
    email: str
    password: str


class ShowUser(BaseModel):
    name: str
    email: str

    class Config():
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None

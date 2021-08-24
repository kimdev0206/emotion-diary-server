from typing import Dict, Optional, List
from datetime import date

from pydantic import BaseModel


class DiaryBase(BaseModel):
    username: str
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

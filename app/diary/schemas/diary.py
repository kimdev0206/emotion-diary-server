from typing import Dict, Optional, List
from datetime import date

from pydantic import BaseModel, Json, validator

from ..dummy_data import ModelName, EmotionColor

EMOTION_COLOR_LIST = [each.name for each in EmotionColor]


class DiaryBase(BaseModel):
    username: ModelName
    date: date

    class Config:
        orm_mode = True


class Diary(DiaryBase):
    title: str
    content: str
    image_type: str

    @validator('image_type')
    def image_type_match(cls, value):
        if value not in EMOTION_COLOR_LIST:
            raise ValueError(f'{value} is not match')
        return value


class DiaryCategory(BaseModel):
    weather: Optional[str] = None
    activity: Optional[List[str]] = None

    @validator('weather')
    def weather_match(cls, value):
        # TODO: Need order?
        if value not in ["해", "비", "구름", "눈"]:
            raise ValueError(f'{value} is not match')
        return value
            
    @validator('activity')
    def activity_match(cls, target_list):
        if not all(target in ["공부", "운동", "게임", "여행", "만남"] for target in target_list):
            raise ValueError(f'{target_list} is not match')
        return target_list


class DiaryRead(Diary):
    # category_json: Json[DiaryCategory]
    category_json: DiaryCategory


class MetaBase(BaseModel):
    diary_count: int


class ShowCountMeta(MetaBase):
    day_count: int


class ShowCountChartMeta(MetaBase):
    username: str


class ShowDiary(BaseModel):
    meta: ShowCountMeta
    body: Dict[str, List[DiaryRead]] = {}


class EmotionCount(BaseModel):
    emotion_type: str
    emotion_count: int = 0
    color: Optional[str] = None


class ShowEmotionCount(BaseModel):
    meta: ShowCountChartMeta
    body: Dict[str, List[EmotionCount]] = {}

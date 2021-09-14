from typing import Dict, Optional, List
from datetime import date

from pydantic import BaseModel, Json, validator

from ..dummy_data import ModelName


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
    def image_type_contain(cls, value):
        # TODO: Extract Enum name
        if value not in ["blue", "unknown", "happy", "mood", "angry"]:
            raise ValueError('Hmm...')
        return value


class DiaryCategory(BaseModel):
    weather: Optional[List[str]] = None
    activity: Optional[List[str]] = None

    @validator('weather')
    def weather_contain(cls, target_list):
        # TODO: Need order
        if not all(target in ["해", "비", "구름", "눈"] for target in target_list):
            raise ValueError('Hmm...')
        return target_list
            
    @validator('activity')
    def activity_contain(cls, target_list):
        if not all(target in ["공부", "운동", "게임", "여행", "만남"] for target in target_list):
            raise ValueError('Hmm...')
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

from collections import defaultdict, Counter
from typing import List
import json

from fastapi import APIRouter, Depends, status, HTTPException, Response, Body
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract

from ..database import get_db
from ..models import Diary, User
from ..authentication.oauth2 import get_current_user
from ..schemas.auth import User as UserSchema
from ..schemas.diary import (
    DiaryBase, ShowDiary, DiaryRead,
    EmotionCount, ShowEmotionCount,
    ShowCountMeta, ShowCountChartMeta
)
from ..dummy_data import ModelName, EmotionColor


router = APIRouter(
    prefix='/diary',
    tags=['Diary']
)


@router.get('/chart', response_model=ShowEmotionCount)
def show_emotion_count(
        username: ModelName,
        year: int = 2021,
        db: Session = Depends(get_db),
        ):
    diaries = db.query(Diary).join(User).filter(
        and_(Diary.username == username,
             extract('year', Diary.date) == year)
    ).all()
    if not diaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'username: {username}는 이용가능하지 않습니다.'
        )
    emotion_count_dict = Counter([each.image_type for each in diaries])
    result = defaultdict(list)
    for emotion in EmotionColor:
        result[year].append(EmotionCount(
            emotion_type=emotion.name,
            emotion_count=emotion_count_dict[emotion.name],
            color=emotion.value
        ))
    return {"meta": ShowCountChartMeta(diary_count=len(diaries), username=username),
            "body": result}


@router.get('/all', response_model=ShowDiary)
def show_all_diary(
        db: Session = Depends(get_db)
        ):
    diaries = db.query(Diary).all()
    result = defaultdict(list)
    for each in diaries:
        key_date = each.date.strftime("%Y%m%d")
        each.category_json = json.dumps(each.category_json)
        result[key_date].append(each)

    return {"meta": ShowCountMeta(diary_count=len(diaries), day_count=len(result)),
            "body": sorted(result.items())}


@router.get('/', response_model=ShowDiary)
def show_diary(
        username: ModelName,
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ):
    diaries: List[DiaryRead] = []
    if username:
        # and_(Diary.username == username, User.email == current_user)
        diaries = db.query(Diary).join(User).filter(Diary.username == username).all()
        if not diaries:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'{username}의 데이터는 존재하지 않습니다.'
                )
    result = defaultdict(list)
    for each in diaries:
        key_date = each.date.strftime("%Y%m%d")
        # each.category_json = json.dumps(each.category_json)
        result[key_date].append(each)

    return {"meta": ShowCountMeta(diary_count=len(diaries), day_count=len(result)),
            "body": sorted(result.items())}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=DiaryRead)
def create_diary(
        request: DiaryRead = Body(...),
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ):
    exist_diary = db.query(Diary).filter(
        and_(Diary.username == request.username,
             Diary.date == request.date)
    ).first()

    if exist_diary:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{request.username}님의 {request.date} 내용이 존재합니다.'
        )
    # request.category_json = jsonable_encoder(request.category_json)
    new_diary = Diary(**request.dict())
    try:
        db.add(new_diary)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e
        )
    db.refresh(new_diary)
    return new_diary


@router.delete('/', status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def destroy_diary(
        request: DiaryBase,
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ) -> None:
    exist_diary = db.query(Diary).filter(
        and_(Diary.username == request.username,
             Diary.date == request.date)
    )

    if not exist_diary.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{request.username}님의 {request.date} 내용이 없습니다."
        )
    exist_diary.delete(synchronize_session=False)
    db.commit()


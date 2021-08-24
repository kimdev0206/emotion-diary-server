from collections import defaultdict, Counter
from typing import Union

from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract

from ..database import get_db
from ..models import Diary, User
from ..schema import Diary as DiarySchema
from ..schema import User as UserSchema
from ..schema import DiaryBase, ShowDiary, ShowDiaryYear, DiaryYear
from ..authentication.oauth2 import get_current_user


router = APIRouter(
    prefix='/diary',
    tags=['Diary']
)

EMOTION_COLOR = {
    "blue": "backgroundColor2",
    "unknown": "backgroundColor3",
    "happy": "backgroundColor4",
    "mood": "backgroundColor5",
    "angry": "backgroundColor6"
}


@router.get('/', response_model=Union[ShowDiary, ShowDiaryYear])
def show_diary(
        username: str = None,
        year: str = None,
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ):
    if year and username:
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
        for emotion in EMOTION_COLOR:
            result[year].append(DiaryYear(
                emotion_type=emotion,
                year_count=emotion_count_dict[emotion],
                color=EMOTION_COLOR[emotion]
            ))
        return {"body": result}
    elif not username and not year:
        diaries = db.query(Diary).all()
    else:
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
        result[key_date].append(each)
    result = sorted(result.items())
    return {"body": result}


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=DiarySchema)
def create_diary(
        request: DiarySchema,
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ):
    if request.image_type not in EMOTION_COLOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'{request.image_type}은 잘못된 감정타입 입니다.'
        )
    exist_diary = db.query(Diary).filter(
        and_(Diary.username == request.username,
             Diary.date == request.date)
    ).first()

    if exist_diary:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{request.username}님의 {request.date} 내용이 존재합니다.'
        )
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


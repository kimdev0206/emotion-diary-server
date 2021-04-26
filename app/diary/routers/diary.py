from collections import OrderedDict

from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ..database import get_db
from ..models import Diary, User
from ..schema import Diary as DiarySchema
from ..schema import User as UserSchema
from ..schema import DiaryBase, ShowDiary
from ..authentication.oauth2 import get_current_user


router = APIRouter(
    prefix='/diary',
    tags=['Diary']
)


# TODO: date 바 없애기
@router.get('/', response_model=ShowDiary)
def all_diaries(
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_user)
        ):
    diaries = db.query(Diary).all()

    result = OrderedDict()
    for each in diaries:
        result[each.date] = each
    result = sorted(result.items())
    return {"body": result}


@router.get(
    '/{user_id}',
    status_code=200,
    response_model=ShowDiary
)
def show_diary(
        user_id,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_user)
        ):

    diaries = db.query(Diary).join(User).filter(
        and_(Diary.user_id == user_id,
             User.email == current_user
             )
    ).all()

    if not diaries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Diary with the id {user_id} is not available'
        )
    result = OrderedDict()
    for each in diaries:
        result[each.date] = each
    return {"body": result}


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=DiarySchema
)
def create_diary(
        request: DiarySchema,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_user)
        ):
    exist_diary = db.query(Diary).filter(
        and_(Diary.user_id == request.user_id,
             Diary.date == request.date)
    ).first()

    if exist_diary:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{request.user_id}님의 {request.date} 내용이 존재합니다.'
        )
    new_diary = Diary(**request.dict())
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)
    return new_diary


@router.delete(
    '/',
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response
)
def destroy_diary(
        request: DiaryBase,
        db: Session = Depends(get_db),
        current_user: UserSchema = Depends(get_current_user)
        ) -> None:
    exist_diary = db.query(Diary).filter(
        and_(Diary.user_id == request.user_id,
             Diary.date == request.date)
    )

    if not exist_diary.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{request.user_id}님의 {request.date} 내용이 없습니다."
        )
    exist_diary.delete(synchronize_session=False)
    db.commit()


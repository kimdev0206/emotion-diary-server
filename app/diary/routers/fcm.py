from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import PushMailToken
from ..authentication.oauth2 import get_current_user_email
from ..schemas.auth import User as UserSchema
from ..schemas.fcm import Token as TokenSchema
from ..schemas.fcm import TokenBase, UpdateSubscribe
from ..fcm import send_mail

router = APIRouter(
    prefix='/fcm',
    tags=["FCM"],
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def create_token(
        request: TokenSchema,
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ):
    exist_token = db.query(PushMailToken).filter(PushMailToken.username == request.username) \
        .first()
    if exist_token:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{request.username}님의 토큰이 이미 존재합니다.'
        )
    new_token = PushMailToken(**request.dict())
    try:
        db.add(new_token)
        db.commit()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={e}
        )
    return {'detail': f'{request.username}님의 토큰이 성공적으로 등록되었습니다.'}


@router.get('/{username}', response_model=TokenSchema)
def get_token(username, db: Session = Depends(get_db)):
    token = db.query(PushMailToken).filter(PushMailToken.username == username)\
        .first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{username}의 토큰이 존재하지 않습니다.'
        )
    return token


@router.patch('/subscribe', response_model=UpdateSubscribe)
def update_subscribe(
        request: TokenBase,
        db: Session = Depends(get_db),
        # current_user: UserSchema = Depends(get_current_user)
        ):
    token = db.query(PushMailToken).filter(PushMailToken.username == request.username)\
        .first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{request.username}의 토큰이 존재하지 않습니다.'
        )
    previous_subscribe = token.is_subscribe
    token.is_subscribe = not token.is_subscribe
    db.commit()
    return UpdateSubscribe(
        username=request.username,
        previous_subscribe=previous_subscribe,
        is_subscribe=token.is_subscribe
    )


@router.get('/push/{username}')
def test_push_mail_service(
        username: str,
        db: Session = Depends(get_db)
        ):
    token = db.query(PushMailToken).filter(PushMailToken.username == username) \
        .first()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{username}의 토큰이 존재하지 않습니다.'
        )
    send_mail(title="타이틀", body="푸시알림테스트", token=token)
    return {'detail': 'it goes well, check your device'}

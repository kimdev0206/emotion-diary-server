from datetime import timedelta

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..models import User
from ..database import get_db
from ..hashing import Hash
from ..authentication.token import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token


router = APIRouter(
    tags=["Auth"]
)


# TODO: validation 필요
@router.post('/login')
def login(
        request: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
        ):
    user = db.query(User).filter(User.email == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Invalid Credentials'
        )
    if not Hash.verify(user.hashedpassword, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Incorrect password'
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.email}, expires_delta=access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}
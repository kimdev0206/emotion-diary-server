from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..hashing import Hash
from ..schemas.auth import User as UserSchema
from ..schemas.auth import ShowUser

router = APIRouter(
    prefix='/user',
    tags=["Users"]
)


@router.post('/', response_model=ShowUser)
def create_user(request: UserSchema, db: Session = Depends(get_db)):
    exist_user = db.query(User).filter(User.name == request.name).first()
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{request.name}이 존재합니다.'
        )
    new_user = User(
        name=request.name,
        email=request.email,
        hashedpassword=Hash.bcrypt(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{name}', response_model=ShowUser)
def get_user(name, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.name == name).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{name}이 존재하지 않습니다.'
        )
    return user

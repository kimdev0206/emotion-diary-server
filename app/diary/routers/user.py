from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from ..schema import User as UserSchema
from ..schema import ShowUser
from ..models import User
from ..database import get_db
from ..hashing import Hash

router = APIRouter(
    prefix='/user',
    tags=["Users"]
)


@router.post('/', response_model=ShowUser)
def create_user(request: UserSchema, db: Session = Depends(get_db)):
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
            detail=f'User with the id {name} is not available'
        )
    return user

from pydantic import BaseModel


class TokenBase(BaseModel):
    username: str
    is_subscribe: bool

    class Config:
        orm_mode = True


class Token(TokenBase):
    token: str


class UpdateSubscribe(TokenBase):
    previous_subscribe: bool

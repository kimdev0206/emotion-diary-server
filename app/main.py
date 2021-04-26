from fastapi import FastAPI

from diary import models
from diary.database import engine
from diary.routers import diary, auth, user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(diary.router)
app.include_router(user.router)

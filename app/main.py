from fastapi import FastAPI
import uvicorn

from diary import models
from diary.database import engine
from diary.middleware import RequireJSON
from diary.routers import diary, auth, user, fcm
from diary.dummy_data import tags_metadata

app = FastAPI(openapi_tags=tags_metadata)

models.Base.metadata.create_all(bind=engine)

# TODO: Need route-level Middleware
# app.add_middleware(RequireJSON)
app.include_router(auth.router)
app.include_router(diary.router)
app.include_router(user.router)
app.include_router(fcm.router)


@app.get("/", tags=['/'])
async def root():
    return {"message:": "/docs 에서 API 사용법 확인을 해주세요."}


# For Debug
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001, debug=True)
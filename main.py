# main.py
from fastapi import FastAPI
from app.api.v1.endpoints import router


app = FastAPI()

# 라우터 등록
app.include_router(router, prefix="/api/v1")

# main.py
from fastapi import FastAPI
from app.api.v1.chat_endpoints import router as chat_router

app = FastAPI()

# 라우터 등록
app.include_router(chat_router, prefix="/api/v1")

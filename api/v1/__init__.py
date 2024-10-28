from fastapi import APIRouter

from .endpoints import chat_router

router = APIRouter()
router.include_router(chat_router, prefix="/api/v1", tags=["Chat"])


__all__ = ["router"]
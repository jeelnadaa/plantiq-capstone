from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.predict import router as predict_router
from app.api.chat import router as chat_router
from app.api.voice import router as voice_router
from app.api.marketplace import router as market_router
from app.api.environment import router as env_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(predict_router)
api_router.include_router(chat_router)
api_router.include_router(voice_router)
api_router.include_router(market_router)
api_router.include_router(env_router)

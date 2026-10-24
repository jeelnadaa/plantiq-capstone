from fastapi import APIRouter

from app.api import auth, chat, marketplace, misc, predict, scans, users

api_router = APIRouter()
for r in (auth.router, users.router, predict.router, scans.router, chat.router, marketplace.router,
          misc.voice_router, misc.env_router, misc.media_router, misc.system_router):
    api_router.include_router(r)

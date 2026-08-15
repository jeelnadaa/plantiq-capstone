from fastapi import APIRouter, Query
from typing import Optional
from app.services.env_service import get_env_service

router = APIRouter(prefix="/environment", tags=["Environmental Weather"])

@router.get("/live")
def get_live_environment(latitude: Optional[float] = Query(None), longitude: Optional[float] = Query(None)):
    svc = get_env_service()
    return svc.get_environmental_data(latitude, longitude)

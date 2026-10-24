"""Voice transcription, weather, media upload/serving, system info."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import db_backend_name, get_db
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.core.uploads import MAX_AUDIO_BYTES, MAX_IMAGE_BYTES, check_audio, sanitize_filename
from app.models import User
from app.services import registry
from app.services.storage import MEDIA_ID_RE, media_path, media_url, save_image

voice_router = APIRouter(prefix="/voice", tags=["Voice"])
env_router = APIRouter(prefix="/environment", tags=["Weather"])
media_router = APIRouter(prefix="/media", tags=["Media"])
system_router = APIRouter(prefix="/system", tags=["System"])
public_media_router = APIRouter(tags=["Media"])


# ----------------------------------------------------------------- voice
@voice_router.post("/transcribe", dependencies=[Depends(rate_limit("heavy"))])
def transcribe(file: UploadFile = File(...), target_language: str = Form("kn", pattern="^(kn|en)$"),
               user: User = Depends(get_current_user)) -> dict:
    data = file.file.read(MAX_AUDIO_BYTES + 1)
    kind = check_audio(data)
    name = sanitize_filename(file.filename or f"voice.{kind}").rsplit(".", 1)[0] + f".{kind}"
    return registry.get_stt().transcribe(data, name, target_language, kind)


@voice_router.get("/status")
def voice_status(user: User = Depends(get_current_user)) -> dict:
    return registry.get_stt().status()


# ----------------------------------------------------------------- weather
def _check(lat: float | None, lng: float | None) -> None:
    if (lat is None) != (lng is None):
        raise HTTPException(422, "Give both latitude and longitude.")


@env_router.get("/live", dependencies=[Depends(rate_limit("default"))])
@env_router.get("/microclimate", include_in_schema=False)
def live(latitude: float | None = Query(None, ge=-90, le=90), longitude: float | None = Query(None, ge=-180, le=180)) -> dict:
    _check(latitude, longitude)
    return registry.get_env().get_environmental_data(latitude, longitude)


@env_router.get("/forecast", dependencies=[Depends(rate_limit("default"))])
def forecast(latitude: float = Query(..., ge=-90, le=90), longitude: float = Query(..., ge=-180, le=180)) -> dict:
    data = registry.get_env().get_environmental_data(latitude, longitude)
    return {"available": data["available"], "forecast": data.get("forecast", []), "spray_window": data.get("spray_window")}


# ----------------------------------------------------------------- media
class MediaOut(BaseModel):
    id: str
    url: str
    width: int
    height: int


@media_router.post("", response_model=MediaOut, dependencies=[Depends(rate_limit("heavy", 60))])
def upload_media(file: UploadFile = File(...), kind: str = Form("listing", pattern="^(listing|chat)$"),
                 user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MediaOut:
    row = save_image(db, file.file.read(MAX_IMAGE_BYTES + 1), owner_id=user.id, kind=kind, filename=file.filename)
    db.commit()
    return MediaOut(id=row.id, url=media_url(row.id), width=row.width, height=row.height)


@public_media_router.get("/media/{name}", include_in_schema=False)
def serve_media(name: str) -> FileResponse:
    """Media ids are 128-bit random capability URLs; content is always a re-encoded JPEG."""
    media_id = name.removesuffix(".jpg")
    if not MEDIA_ID_RE.fullmatch(media_id):
        raise HTTPException(404, "Not found.")
    path = media_path(media_id)
    if not path.exists():
        raise HTTPException(404, "Not found.")
    return FileResponse(path, media_type="image/jpeg", headers={
        "Cache-Control": "private, max-age=86400", "X-Content-Type-Options": "nosniff",
        "Content-Disposition": "inline",
    })


# ----------------------------------------------------------------- system
@system_router.get("/info")
def info() -> dict:
    rag_info = None
    if registry.loaded("rag"):
        try:
            rag_info = registry.get_rag().info()
        except Exception:
            rag_info = None
    from app.services.rag.index import read_meta
    from app.services.rag.profiles import choose_profile

    return {
        "name": settings.PROJECT_NAME, "version": settings.VERSION, "env": settings.ENV,
        "database": db_backend_name(), "fake_ml": settings.FAKE_ML,
        "llm_providers": registry.get_llm().providers() if registry.loaded("llm") or settings.FAKE_ML else
        [p for p, k in (("gemini", settings.GEMINI_API_KEY), ("groq", settings.GROQ_API_KEY)) if k],
        "rag": rag_info or {"profile_planned": choose_profile().name, "index": read_meta()},
        "cnn_loaded": registry.loaded("cnn"),
        "limits": {"max_image_mb": MAX_IMAGE_BYTES // 1024**2, "max_audio_mb": MAX_AUDIO_BYTES // 1024**2},
    }

"""Chatbot: messages with optional photo / past-scan context, thread list, rename, delete."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.core.uploads import MAX_IMAGE_BYTES, clean_image, decode_data_url
from app.models import ChatMessage, ChatThread, MediaFile, User
from app.services import registry
from app.services.chat import ChatInput, parse_scan_metadata, process_message
from app.services.storage import MEDIA_ID_RE, media_path, media_url, save_image

router = APIRouter(prefix="/chat", tags=["Chatbot"])


class ChatOut(BaseModel):
    session_id: str
    reply: str
    history: list[dict]
    disease: str | None = None
    language: str = "en"
    provider: str | None = None
    sources: list[dict] = []
    env_used: bool = False
    image_url: str | None = None


class ThreadOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime | None = None
    message_count: int


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    attached_image_name: str | None = None
    image_url: str | None = None
    image_data_url: str | None = None  # kept for clients of the original API
    disease: str | None = None
    created_at: datetime


class RenameIn(BaseModel):
    title: str = Field(min_length=1, max_length=120)


@router.post("/message", response_model=ChatOut, dependencies=[Depends(rate_limit("heavy"))])
def send_message(
    user_message: str = Form(..., min_length=1, max_length=2000),
    session_id: str | None = Form(None, max_length=36),
    attached_image_name: str | None = Form(None, max_length=160),
    disease_context: str | None = Form(None, max_length=40),
    image_base64: str | None = Form(None),
    media_id: str | None = Form(None, max_length=32),
    scan_metadata_json: str | None = Form(None, max_length=20000),
    image_file: UploadFile | None = File(None),
    language: str = Form("en", pattern="^(en|kn)$"),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatOut:
    image_bytes: bytes | None = None
    stored_media_id: str | None = None
    if image_file is not None:
        img = clean_image(image_file.file.read(MAX_IMAGE_BYTES + 1), image_file.filename)
        stored_media_id = save_image(db, img.data, owner_id=user.id, kind="chat", already_clean=img).id
        image_bytes = img.data
    elif image_base64 and image_base64.strip():
        img = clean_image(decode_data_url(image_base64.strip()), attached_image_name)
        stored_media_id = save_image(db, img.data, owner_id=user.id, kind="chat", already_clean=img).id
        image_bytes = img.data
    elif media_id:
        # Re-use a photo the farmer already uploaded (e.g. picked from scan history). Must be theirs.
        row = db.get(MediaFile, media_id) if MEDIA_ID_RE.fullmatch(media_id) else None
        if not row or row.owner_id != user.id:
            raise HTTPException(404, "Attached photo not found.")
        try:
            image_bytes = media_path(media_id).read_bytes()
        except OSError as exc:
            raise HTTPException(404, "Attached photo not found.") from exc
        stored_media_id = media_id

    if latitude is not None and longitude is not None and not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        latitude = longitude = None
    disease = disease_context if disease_context in ("Miner", "Rust", "Phoma", "Healthy", "Cerscospora") else None

    out = process_message(
        db,
        ChatInput(user_id=user.id, message=user_message.strip(), session_id=session_id, language=language,
                  latitude=latitude, longitude=longitude, image_bytes=image_bytes, media_id=stored_media_id,
                  attached_image_name=attached_image_name, disease_context=disease,
                  scan_metadata=parse_scan_metadata(scan_metadata_json)),
        cnn=registry.get_cnn(), rag=registry.get_rag(), llm=registry.get_llm(), env_service=registry.get_env(),
    )
    return ChatOut(**out, image_url=media_url(stored_media_id))


@router.get("/threads", response_model=list[ThreadOut])
def threads(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ThreadOut]:
    counts = dict(db.execute(select(ChatMessage.thread_id, func.count()).join(ChatThread)
                             .where(ChatThread.user_id == user.id).group_by(ChatMessage.thread_id)).all())
    rows = db.scalars(select(ChatThread).where(ChatThread.user_id == user.id)
                      .order_by(ChatThread.updated_at.desc(), ChatThread.created_at.desc())).all()
    return [ThreadOut(id=t.id, title=t.title, created_at=t.created_at, updated_at=t.updated_at,
                      message_count=counts.get(t.id, 0)) for t in rows]


def _owned(db: Session, user: User, thread_id: str) -> ChatThread:
    t = db.get(ChatThread, thread_id)
    if not t:
        raise HTTPException(404, "Conversation not found.")
    if t.user_id != user.id:
        raise HTTPException(403, "Not allowed to access this conversation.")
    return t


@router.get("/threads/{thread_id}/messages", response_model=list[MessageOut])
def thread_messages(thread_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[MessageOut]:
    t = _owned(db, user, thread_id)
    return [MessageOut(id=m.id, role=m.role, content=m.content, attached_image_name=m.attached_image_name,
                       image_url=media_url(m.media_id), image_data_url=media_url(m.media_id), disease=m.disease,
                       created_at=m.created_at) for m in t.messages]


@router.patch("/threads/{thread_id}", response_model=ThreadOut)
def rename_thread(thread_id: str, payload: RenameIn, user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)) -> ThreadOut:
    t = _owned(db, user, thread_id)
    t.title = payload.title.strip()[:120]
    db.commit()
    return ThreadOut(id=t.id, title=t.title, created_at=t.created_at, updated_at=t.updated_at, message_count=len(t.messages))


@router.delete("/threads/{thread_id}")
def delete_thread(thread_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    t = _owned(db, user, thread_id)
    db.delete(t)
    db.commit()
    return {"status": "deleted", "id": thread_id}

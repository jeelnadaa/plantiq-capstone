from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from typing import Optional, List
from sqlalchemy.orm import Session
import base64
from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.chat import ChatThread, ChatMessage
from app.services.chat_service import process_chat_message
from app.schemas.chat import ChatResponse, ThreadItem, MessageItem

router = APIRouter(prefix="/chat", tags=["Chatbot Assistant"])

@router.post("/message", response_model=ChatResponse)
async def send_message(
    session_id: Optional[str] = Form(None),
    user_message: str = Form(...),
    attached_image_name: Optional[str] = Form(None),
    disease_context: Optional[str] = Form(None),
    image_base64: Optional[str] = Form(None),
    scan_metadata_json: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    language: str = Form("en"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    
    image_bytes = None
    if image_file:
        image_bytes = await image_file.read()
    elif image_base64 and image_base64.strip():
        try:
            raw = image_base64.split(",", 1)[1] if "," in image_base64 else image_base64
            image_bytes = base64.b64decode(raw)
        except Exception as e:
            print(f"[Chat API] Image decode error: {e}")

    res = process_chat_message(
        db=db,
        session_id=session_id,
        user_message=user_message,
        attached_image_name=attached_image_name,
        image_bytes=image_bytes,
        image_data_url=image_base64,
        scan_metadata_json=scan_metadata_json,
        disease_context=disease_context,
        language=language,
        latitude=latitude,
        longitude=longitude,
        user_id=user_id
    )
    return res

@router.get("/threads", response_model=List[ThreadItem])
def get_threads(current_user: Optional[User] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    query = db.query(ChatThread)
    if current_user:
        query = query.filter((ChatThread.user_id == current_user.id) | (ChatThread.user_id.is_(None)))
    threads = query.order_by(ChatThread.created_at.desc()).all()
    
    result = []
    for t in threads:
        result.append(ThreadItem(
            id=t.id,
            title=t.title,
            created_at=t.created_at,
            message_count=len(t.messages)
        ))
    return result

@router.get("/threads/{thread_id}/messages", response_model=List[MessageItem])
def get_thread_messages(thread_id: str, db: Session = Depends(get_db)):
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    return [
        MessageItem(
            id=m.id,
            role=m.role,
            content=m.content,
            attached_image_name=m.attached_image_name,
            image_data_url=m.image_data_url,
            created_at=m.created_at
        )
        for m in thread.messages
    ]

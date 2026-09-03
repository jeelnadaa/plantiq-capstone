from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageItem(BaseModel):
    id: int
    role: str
    content: str
    attached_image_name: Optional[str] = None
    image_data_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ThreadItem(BaseModel):
    id: str
    title: str
    created_at: datetime
    message_count: int

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history: List[dict]
    disease: Optional[str] = None

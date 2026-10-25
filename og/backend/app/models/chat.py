from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ChatThread(Base):
    __tablename__ = 'chat_threads'
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship('ChatMessage', back_populates='thread', cascade='all, delete-orphan', order_by='ChatMessage.created_at')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, ForeignKey('chat_threads.id'), nullable=False, index=True)
    role = Column(String, nullable=False) # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    attached_image_name = Column(String, nullable=True)
    image_data_url = Column(Text, nullable=True) # Persistent base64 / image url
    created_at = Column(DateTime, default=datetime.utcnow)
    thread = relationship('ChatThread', back_populates='messages')

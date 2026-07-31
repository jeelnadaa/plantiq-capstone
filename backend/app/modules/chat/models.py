import uuid
import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base, engine
from app.modules.auth.models import User

class ChatThread(Base):
    __tablename__ = "chat_threads"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(255), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="thread", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(64), ForeignKey("chat_threads.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    sources_json = Column(Text, nullable=True)
    env_data_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("ChatThread", back_populates="messages")

# Ensure tables are created
Base.metadata.create_all(bind=engine)

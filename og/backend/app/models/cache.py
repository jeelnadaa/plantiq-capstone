from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean
from datetime import datetime
from app.core.database import Base

class ImageAnalysisCache(Base):
    __tablename__ = 'image_analysis_cache'
    id = Column(Integer, primary_key=True, index=True)
    image_hash = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=True, index=True)
    filename = Column(String, nullable=True)
    disease_class = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    distribution = Column(JSON, nullable=False)
    env_data = Column(JSON, nullable=True)
    advisory_text = Column(String, nullable=False)
    sources = Column(JSON, nullable=True)
    is_blended = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

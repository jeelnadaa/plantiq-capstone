from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class CropListing(Base):
    __tablename__ = 'crop_listings'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    title = Column(String, nullable=False)
    variety = Column(String, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    farmer_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    photos = Column(JSON, nullable=True) # List of dicts: [{"url": "...", "caption": "..."}]
    created_at = Column(DateTime, default=datetime.utcnow)

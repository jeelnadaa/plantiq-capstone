from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from app.core.database import Base, engine

class CropListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    crop_name = Column(String(100), nullable=False)
    variety = Column(String(100), default="Arabica")
    quantity_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    farmer_name = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

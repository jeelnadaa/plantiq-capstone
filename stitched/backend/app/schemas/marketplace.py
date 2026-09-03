from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ListingPhoto(BaseModel):
    url: str
    caption: Optional[str] = ""

class ListingCreate(BaseModel):
    title: str
    variety: str
    quantity_kg: float
    price_per_kg: float
    farmer_name: str
    phone_number: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[ListingPhoto]] = []

class ListingResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    variety: str
    quantity_kg: float
    price_per_kg: float
    farmer_name: str
    phone_number: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[ListingPhoto]] = []
    created_at: datetime
    google_maps_url: Optional[str] = None
    is_owner: bool = False

    class Config:
        from_attributes = True

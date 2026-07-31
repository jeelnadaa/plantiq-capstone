from pydantic import BaseModel, computed_field
from typing import Optional
from datetime import datetime

class CropListingCreate(BaseModel):
    crop_name: str
    variety: Optional[str] = "Arabica"
    quantity_kg: float
    price_per_kg: float
    farmer_name: str
    contact_phone: str
    address: str
    latitude: float
    longitude: float
    description: Optional[str] = ""

class CropListingResponse(CropListingCreate):
    id: int
    image_url: Optional[str] = None
    created_at: datetime

    @computed_field
    @property
    def google_maps_url(self) -> str:
        return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"

    class Config:
        from_attributes = True

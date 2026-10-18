from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import html

class ListingPhoto(BaseModel):
    url: str
    caption: Optional[str] = ""

class ListingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=120, description="Listing title")
    variety: str = Field(..., min_length=2, max_length=80, description="Crop variety (e.g. Arabica Sln 795, Robusta)")
    quantity_kg: float = Field(..., gt=0.0, le=100000.0, description="Quantity in kilograms (positive up to 100 metric tons)")
    price_per_kg: float = Field(..., gt=0.0, le=100000.0, description="Price in INR per kg (positive up to 100,000)")
    farmer_name: str = Field(..., min_length=2, max_length=100, description="Farmer name")
    phone_number: str = Field(..., min_length=7, max_length=25, description="Contact phone number")
    address: str = Field(..., min_length=3, max_length=300, description="Farm or town address")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    photos: Optional[List[ListingPhoto]] = []

    @field_validator('title', 'variety', 'farmer_name', 'phone_number', 'address', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return html.escape(v.strip())
        return v

class ListingReportCreate(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="Reason for reporting listing")

    @field_validator('reason', mode='before')
    @classmethod
    def sanitize_reason(cls, v):
        if isinstance(v, str):
            return html.escape(v.strip())
        return v

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


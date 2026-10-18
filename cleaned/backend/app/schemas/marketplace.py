from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import html

import math

class ListingPhoto(BaseModel):
    url: str
    caption: Optional[str] = ""

class ListingCreate(BaseModel):
    title: str = Field(default="Coffee Crop Lot", max_length=150, description="Listing title")
    variety: Optional[str] = Field(default="Arabica", max_length=100, description="Crop variety")
    quantity_kg: float = Field(default=100.0, ge=0.0, le=100000.0, description="Quantity in kilograms")
    price_per_kg: float = Field(default=0.0, ge=0.0, le=100000.0, description="Price in INR per kg")
    farmer_name: Optional[str] = Field(default="Coffee Grower", max_length=120, description="Farmer name")
    phone_number: Optional[str] = Field(default="", max_length=30, description="Contact phone number")
    address: Optional[str] = Field(default="Karnataka, India", max_length=300, description="Farm or town address")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[ListingPhoto]] = []

    @field_validator('title', 'variety', 'farmer_name', 'phone_number', 'address', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        if v is None:
            return ""
        if isinstance(v, str):
            return html.escape(v.strip())
        return str(v)

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def sanitize_coords(cls, v):
        if v is None or v == "" or v == "null" or v == "undefined":
            return None
        try:
            val = float(v)
            if math.isnan(val) or val < -180.0 or val > 180.0:
                return None
            return val
        except (ValueError, TypeError):
            return None

    @field_validator('quantity_kg', 'price_per_kg', mode='before')
    @classmethod
    def sanitize_numbers(cls, v):
        if v is None or v == "" or v == "null" or v == "undefined":
            return 0.0
        try:
            val = float(v)
            if math.isnan(val):
                return 0.0
            return val
        except (ValueError, TypeError):
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


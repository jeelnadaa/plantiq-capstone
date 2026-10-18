from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import html
import re
import math

def normalize_quantity_to_kg(qty: Optional[float], unit_str: Optional[str]) -> float:
    """Normalizes any agricultural unit (ton, quintal, bag, custom kg) to kilograms."""
    if qty is None or qty <= 0:
        return 0.0
    if not unit_str:
        return round(float(qty), 2)
    u = unit_str.lower().strip()
    # Tons / Tonnes (1 ton = 1000 kg, or "x ton")
    if "ton" in u or "tonne" in u:
        m = re.search(r'(\d+(?:\.\d+)?)\s*ton', u)
        mult = float(m.group(1)) if (m and m.group(1)) else 1.0
        return round(float(qty) * mult * 1000.0, 2)
    # Quintals (1 quintal = 100 kg)
    if "quintal" in u:
        m = re.search(r'(\d+(?:\.\d+)?)\s*quintal', u)
        mult = float(m.group(1)) if (m and m.group(1)) else 1.0
        return round(float(qty) * mult * 100.0, 2)
    # Bags (e.g. 50kg bag, 60kg bag)
    if "50kg" in u or "50 kg" in u:
        return round(float(qty) * 50.0, 2)
    if "60kg" in u or "60 kg" in u:
        return round(float(qty) * 60.0, 2)
    # Custom "x kg" (e.g. 25 kg sack, 10 kg box)
    m_kg = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo)', u)
    if m_kg and m_kg.group(1):
        return round(float(qty) * float(m_kg.group(1)), 2)
    return round(float(qty), 2)

def normalize_price_to_per_kg(price: Optional[float], unit_str: Optional[str]) -> float:
    """Normalizes any pricing unit ('per kg', 'per 2 kg', 'per ton', 'per y ton', 'per bag') to ₹/kg."""
    if price is None or price <= 0:
        return 0.0
    if not unit_str:
        return round(float(price), 2)
    u = unit_str.lower().strip()
    # Check for "per y ton" or "/ y ton" or "per ton"
    if "ton" in u or "tonne" in u:
        m = re.search(r'(\d+(?:\.\d+)?)\s*ton', u)
        tons = float(m.group(1)) if (m and m.group(1)) else 1.0
        kg = tons * 1000.0
        return round(float(price) / kg, 2)
    # Check for quintals (1 quintal = 100 kg)
    if "quintal" in u:
        m = re.search(r'(\d+(?:\.\d+)?)\s*quintal', u)
        quintals = float(m.group(1)) if (m and m.group(1)) else 1.0
        kg = quintals * 100.0
        return round(float(price) / kg, 2)
    # Bags
    if "50kg" in u or "50 kg" in u:
        return round(float(price) / 50.0, 2)
    if "60kg" in u or "60 kg" in u:
        return round(float(price) / 60.0, 2)
    # Check for "per x kg" or "/ x kg" (e.g. "per 2 kg" -> x = 2 kg)
    m_kg = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo)', u)
    if m_kg and m_kg.group(1):
        kg = float(m_kg.group(1))
        if kg > 0:
            return round(float(price) / kg, 2)
    return round(float(price), 2)

class ListingPhoto(BaseModel):
    url: str
    caption: Optional[str] = ""

class ListingCreate(BaseModel):
    title: str = Field(default="Coffee Crop Lot", max_length=150, description="Listing title")
    variety: Optional[str] = Field(default="Arabica", max_length=100, description="Crop variety")
    quantity: Optional[float] = Field(default=None, description="Raw quantity (e.g. 5, 50, 100)")
    quantity_unit: Optional[str] = Field(default="kg", max_length=50, description="Quantity unit (e.g. kg, ton, bag, custom)")
    quantity_kg: Optional[float] = Field(default=None, description="Normalized quantity in kg")
    price: Optional[float] = Field(default=None, description="Raw price (e.g. 420, 35000, 900)")
    price_unit: Optional[str] = Field(default="per kg", max_length=80, description="Pricing unit (e.g. per kg, per 2 kg, per ton, per y ton)")
    price_per_kg: Optional[float] = Field(default=None, description="Normalized price in INR per kg")
    farmer_name: Optional[str] = Field(default="Coffee Grower", max_length=120, description="Farmer name")
    phone_number: str = Field(..., description="Contact phone number (must be exact 10 digits)")
    address: Optional[str] = Field(default="Karnataka, India", max_length=300, description="Farm or town address")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[ListingPhoto]] = []

    @field_validator('phone_number', mode='before')
    @classmethod
    def validate_phone_number(cls, v):
        if not v:
            raise ValueError("Phone number is required and must contain exactly 10 digits.")
        val_str = str(v).strip()
        # Extract digits
        clean = re.sub(r'\D', '', val_str)
        # If passed with country code 91 and total length 12, extract the 10 national digits
        if len(clean) == 12 and clean.startswith("91"):
            clean = clean[2:]
        # Enforce exact 10 digits regex: not less, not more, no letters
        if not re.fullmatch(r'\d{10}', clean):
            raise ValueError("Phone number must contain exactly 10 digits (e.g., 9876543210).")
        return clean

    @field_validator('title', 'variety', 'farmer_name', 'address', 'quantity_unit', 'price_unit', mode='before')
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

    @field_validator('quantity', 'quantity_kg', 'price', 'price_per_kg', mode='before')
    @classmethod
    def sanitize_numbers(cls, v):
        if v is None or v == "" or v == "null" or v == "undefined":
            return None
        try:
            val = float(v)
            if math.isnan(val):
                return None
            return val
        except (ValueError, TypeError):
            return v

    @model_validator(mode='after')
    def resolve_units_and_bounds(self):
        # Resolve Quantity
        if self.quantity is not None and self.quantity_kg is None:
            self.quantity_kg = normalize_quantity_to_kg(self.quantity, self.quantity_unit)
        elif self.quantity_kg is not None and self.quantity is None:
            self.quantity = self.quantity_kg
            if not self.quantity_unit:
                self.quantity_unit = "kg"
        elif self.quantity_kg is None and self.quantity is None:
            self.quantity = 100.0
            self.quantity_kg = 100.0
            self.quantity_unit = "kg"

        # Resolve Price
        if self.price is not None and self.price_per_kg is None:
            self.price_per_kg = normalize_price_to_per_kg(self.price, self.price_unit)
        elif self.price_per_kg is not None and self.price is None:
            self.price = self.price_per_kg
            if not self.price_unit:
                self.price_unit = "per kg"
        elif self.price_per_kg is None and self.price is None:
            self.price = 0.0
            self.price_per_kg = 0.0
            self.price_unit = "per kg"

        # Bounds validation
        if self.price_per_kg < 0.0 or self.price < 0.0:
            raise ValueError("Price cannot be negative.")
        if self.quantity_kg > 100000.0:
            raise ValueError("Total quantity cannot exceed 100,000 kg (100 metric tons).")

        return self

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
    quantity: Optional[float] = None
    quantity_unit: Optional[str] = "kg"
    quantity_kg: float
    price: Optional[float] = None
    price_unit: Optional[str] = "per kg"
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



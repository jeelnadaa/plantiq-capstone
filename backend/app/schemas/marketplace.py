from __future__ import annotations

import math
import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.common import clean_text_field, normalize_phone

MAX_PRICE = 1_000_000.0
MAX_QTY_KG = 100_000.0


def _first_number(pattern: str, text: str) -> float:
    m = re.search(pattern, text)
    return float(m.group(1)) if m and m.group(1) else 1.0


def normalize_quantity_to_kg(qty: float | None, unit: str | None) -> float:
    """kg, ton/tonne, quintal, 50/60 kg bag, or custom "x kg" → kilograms (same rules as the original)."""
    if qty is None or qty <= 0:
        return 0.0
    u = (unit or "kg").lower().strip()
    if "ton" in u:
        return round(qty * _first_number(r"(\d+(?:\.\d+)?)\s*ton", u) * 1000.0, 2)
    if "quintal" in u:
        return round(qty * _first_number(r"(\d+(?:\.\d+)?)\s*quintal", u) * 100.0, 2)
    if "50kg" in u.replace(" ", ""):
        return round(qty * 50.0, 2)
    if "60kg" in u.replace(" ", ""):
        return round(qty * 60.0, 2)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilo)", u)
    if m:
        return round(qty * float(m.group(1)), 2)
    return round(qty, 2)


def normalize_price_to_per_kg(price: float | None, unit: str | None) -> float:
    """per kg / per x kg / per ton / per y ton / per quintal / per 50|60 kg bag → ₹ per kg."""
    if price is None or price <= 0:
        return 0.0
    u = (unit or "per kg").lower().strip()
    if "ton" in u:
        return round(price / (_first_number(r"(\d+(?:\.\d+)?)\s*ton", u) * 1000.0), 2)
    if "quintal" in u:
        return round(price / (_first_number(r"(\d+(?:\.\d+)?)\s*quintal", u) * 100.0), 2)
    if "50kg" in u.replace(" ", ""):
        return round(price / 50.0, 2)
    if "60kg" in u.replace(" ", ""):
        return round(price / 60.0, 2)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilo)", u)
    if m and float(m.group(1)) > 0:
        return round(price / float(m.group(1)), 2)
    return round(price, 2)


class PhotoIn(BaseModel):
    media_id: str | None = None
    url: str | None = None  # accepted for compatibility: "/media/<id>.jpg"
    caption: str = Field(default="", max_length=140)

    @model_validator(mode="after")
    def _resolve(self):
        mid = self.media_id
        if not mid and self.url:
            m = re.search(r"/media/([a-f0-9]{32})\.jpg$", self.url)
            mid = m.group(1) if m else None
        if not mid or not re.fullmatch(r"[a-f0-9]{32}", mid):
            raise ValueError("Each photo must be uploaded first (invalid photo reference).")
        self.media_id = mid
        self.url = None
        self.caption = re.sub(r"[<>]", "", re.sub(r"\s+", " ", self.caption or "")).strip()
        return self


def _num(v):
    if v is None or v == "" or v in ("null", "undefined"):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError) as exc:
        raise ValueError("Must be a number.") from exc
    if math.isnan(f) or math.isinf(f):
        raise ValueError("Must be a number.")
    return f


class ListingIn(BaseModel):
    title: str
    variety: str
    quantity: float | None = None
    quantity_unit: str = Field(default="kg", max_length=50)
    quantity_kg: float | None = None
    price: float | None = None
    price_unit: str = Field(default="per kg", max_length=80)
    price_per_kg: float | None = None
    farmer_name: str
    phone_number: str
    address: str
    latitude: float | None = None
    longitude: float | None = None
    photos: list[PhotoIn] = Field(default_factory=list, max_length=8)

    @field_validator("title", mode="before")
    @classmethod
    def _title(cls, v):
        return clean_text_field(v, min_len=3, max_len=150, label="Crop title")

    @field_validator("variety", mode="before")
    @classmethod
    def _variety(cls, v):
        return clean_text_field(v, min_len=2, max_len=100, label="Variety")

    @field_validator("farmer_name", mode="before")
    @classmethod
    def _farmer(cls, v):
        return clean_text_field(v, min_len=2, max_len=120, label="Farmer name")

    @field_validator("address", mode="before")
    @classmethod
    def _address(cls, v):
        return clean_text_field(v, min_len=3, max_len=300, label="Estate address")

    @field_validator("phone_number", mode="before")
    @classmethod
    def _phone(cls, v):
        return normalize_phone(v)

    @field_validator("quantity_unit", "price_unit", mode="before")
    @classmethod
    def _units(cls, v):
        return re.sub(r"[<>]", "", re.sub(r"\s+", " ", str(v or ""))).strip()

    @field_validator("quantity", "quantity_kg", "price", "price_per_kg", mode="before")
    @classmethod
    def _numbers(cls, v):
        return _num(v)

    @field_validator("latitude", mode="before")
    @classmethod
    def _lat(cls, v):
        v = _num(v)
        return v if v is not None and -90 <= v <= 90 else None

    @field_validator("longitude", mode="before")
    @classmethod
    def _lng(cls, v):
        v = _num(v)
        return v if v is not None and -180 <= v <= 180 else None

    @model_validator(mode="after")
    def _resolve_units(self):
        if not self.quantity_unit:
            self.quantity_unit = "kg"
        if not self.price_unit:
            self.price_unit = "per kg"
        if self.quantity is None and self.quantity_kg is None:
            raise ValueError("Harvest quantity is required and must be more than 0.")
        if self.quantity is None:
            self.quantity, self.quantity_unit = self.quantity_kg, "kg"
        if self.quantity <= 0:
            raise ValueError("Harvest quantity is required and must be more than 0.")
        self.quantity_kg = normalize_quantity_to_kg(self.quantity, self.quantity_unit)
        if self.price is None and self.price_per_kg is None:
            raise ValueError("Crop price is required and must be more than 0.")
        if self.price is None:
            self.price, self.price_unit = self.price_per_kg, "per kg"
        if self.price <= 0:
            raise ValueError("Crop price is required and must be more than 0.")
        self.price_per_kg = normalize_price_to_per_kg(self.price, self.price_unit)
        if self.price > MAX_PRICE or self.price_per_kg > MAX_PRICE:
            raise ValueError("Crop price cannot exceed ₹10,00,000.")
        if self.quantity_kg <= 0 or self.quantity_kg > MAX_QTY_KG:
            raise ValueError("Total quantity must be between 0 and 100,000 kg (100 tonnes).")
        if (self.latitude is None) != (self.longitude is None):
            self.latitude = self.longitude = None
        return self


class ReportIn(BaseModel):
    reason: str = Field(min_length=3, max_length=500)

    @field_validator("reason", mode="before")
    @classmethod
    def _reason(cls, v):
        return clean_text_field(v, min_len=3, max_len=500, label="Reason")


class PhotoOut(BaseModel):
    media_id: str
    url: str
    caption: str = ""


class ListingOut(BaseModel):
    id: int
    user_id: int
    title: str
    variety: str
    quantity: float
    quantity_unit: str
    quantity_kg: float
    price: float
    price_unit: str
    price_per_kg: float
    farmer_name: str
    phone_number: str
    address: str
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float | None = None
    photos: list[PhotoOut] = []
    created_at: datetime
    updated_at: datetime | None = None
    google_maps_url: str | None = None
    whatsapp_url: str | None = None
    is_owner: bool = False
    reported_by_me: bool = False

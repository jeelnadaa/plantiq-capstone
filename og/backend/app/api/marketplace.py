from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_optional, get_current_user
from app.models.user import User
from app.models.marketplace import CropListing, ListingReport
from app.schemas.marketplace import ListingCreate, ListingResponse, ListingReportCreate
from datetime import datetime

import math

router = APIRouter(prefix="/marketplace", tags=["Farmer Marketplace"])

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes the great-circle distance between two GPS coordinates using the Haversine formula.
    Returns distance in kilometers rounded to 1 decimal place.
    """
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2 +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


def format_listing_response(
    item: CropListing,
    current_user_id: Optional[int],
    buyer_lat: Optional[float] = None,
    buyer_lng: Optional[float] = None
) -> dict:
    maps_url = f"https://www.google.com/maps/search/?api=1&query={item.latitude},{item.longitude}" if (item.latitude and item.longitude) else None
    q_val = getattr(item, "quantity", None)
    if q_val is None:
        q_val = item.quantity_kg
    q_unit = getattr(item, "quantity_unit", None) or "kg"
    p_val = getattr(item, "price", None)
    if p_val is None:
        p_val = item.price_per_kg
    p_unit = getattr(item, "price_unit", None) or "per kg"

    distance_km = None
    if buyer_lat is not None and buyer_lng is not None and item.latitude is not None and item.longitude is not None:
        try:
            distance_km = haversine_distance(buyer_lat, buyer_lng, item.latitude, item.longitude)
        except Exception:
            distance_km = None

    return {
        "id": item.id,
        "user_id": item.user_id,
        "title": item.title,
        "variety": item.variety,
        "quantity": q_val,
        "quantity_unit": q_unit,
        "quantity_kg": item.quantity_kg,
        "price": p_val,
        "price_unit": p_unit,
        "price_per_kg": item.price_per_kg,
        "farmer_name": item.farmer_name,
        "phone_number": item.phone_number,
        "address": item.address,
        "latitude": item.latitude,
        "longitude": item.longitude,
        "distance_km": distance_km,
        "photos": item.photos or [],
        "created_at": item.created_at,
        "google_maps_url": maps_url,
        "is_owner": bool(current_user_id and item.user_id == current_user_id)
    }


@router.get("/listings", response_model=List[ListingResponse])
def get_all_listings(
    q: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_qty: Optional[float] = Query(None),
    variety: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    max_distance_km: Optional[float] = Query(None),
    has_photos: Optional[bool] = Query(None),
    sort_by: Optional[str] = Query("newest"),  # 'distance', 'newest', 'price_asc', 'price_desc', 'qty_desc'
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(CropListing)
    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        query = query.filter(
            CropListing.title.ilike(term) |
            CropListing.variety.ilike(term) |
            CropListing.address.ilike(term) |
            CropListing.farmer_name.ilike(term)
        )
    if min_price is not None:
        query = query.filter(CropListing.price_per_kg >= min_price)
    if max_price is not None:
        query = query.filter(CropListing.price_per_kg <= max_price)
    if min_qty is not None:
        query = query.filter(CropListing.quantity_kg >= min_qty)
    if variety and variety.strip() and variety.strip().lower() != "all":
        query = query.filter(CropListing.variety.ilike(f"%{variety.strip()}%"))

    items = query.all()
    user_id = current_user.id if current_user else None
    results = [format_listing_response(item, user_id, buyer_lat=latitude, buyer_lng=longitude) for item in items]

    # Filter by photos if requested
    if has_photos is True:
        results = [r for r in results if r.get("photos") and len(r["photos"]) > 0]

    # Filter by max_distance_km if requested
    if max_distance_km is not None and latitude is not None and longitude is not None:
        results = [r for r in results if r["distance_km"] is not None and r["distance_km"] <= max_distance_km]

    # Multi-criteria Sorting
    if sort_by == "distance" and latitude is not None and longitude is not None:
        # Distance sort: nearest first; listings without GPS coordinates are placed at the end
        results.sort(key=lambda x: (x["distance_km"] is None, x["distance_km"] if x["distance_km"] is not None else float("inf")))
    elif sort_by == "price_asc":
        results.sort(key=lambda x: x["price_per_kg"] if x["price_per_kg"] is not None else float("inf"))
    elif sort_by == "price_desc":
        results.sort(key=lambda x: x["price_per_kg"] if x["price_per_kg"] is not None else 0, reverse=True)
    elif sort_by == "qty_desc":
        results.sort(key=lambda x: x["quantity_kg"] if x["quantity_kg"] is not None else 0, reverse=True)
    else:  # default: newest
        results.sort(key=lambda x: x["created_at"], reverse=True)

    return results

@router.post("/listings", response_model=ListingResponse)
def create_listing(
    payload: ListingCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None

    # Quota check: Limit to max 50 active listings per user to prevent database flooding
    if user_id:
        existing_count = db.query(CropListing).filter(CropListing.user_id == user_id).count()
        if existing_count >= 50:
            raise HTTPException(
                status_code=429,
                detail="Maximum listing limit reached (50 listings per user). Please remove old listings."
            )

    photos_data = [p.dict() if hasattr(p, "dict") else p for p in (payload.photos or [])]
    item = CropListing(
        user_id=user_id,
        title=payload.title,
        variety=payload.variety,
        quantity=payload.quantity,
        quantity_unit=payload.quantity_unit or "kg",
        quantity_kg=payload.quantity_kg,
        price=payload.price,
        price_unit=payload.price_unit or "per kg",
        price_per_kg=payload.price_per_kg,
        farmer_name=payload.farmer_name,
        phone_number=payload.phone_number,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
        photos=photos_data
    )

    db.add(item)
    db.commit()
    db.refresh(item)
    return format_listing_response(item, user_id)

@router.get("/my-listings", response_model=List[ListingResponse])
def get_my_listings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(CropListing).filter(CropListing.user_id == current_user.id).order_by(CropListing.created_at.desc()).all()
    return [format_listing_response(item, current_user.id) for item in items]

@router.get("/listings/{listing_id}", response_model=ListingResponse)
def get_single_listing(
    listing_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    item = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    user_id = current_user.id if current_user else None
    return format_listing_response(item, user_id)

@router.put("/listings/{listing_id}", response_model=ListingResponse)
def update_listing(
    listing_id: int,
    payload: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    if item.user_id is not None and item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this listing")

    photos_data = [p.dict() if hasattr(p, "dict") else p for p in (payload.photos or [])]
    item.title = payload.title
    item.variety = payload.variety
    item.quantity = payload.quantity
    item.quantity_unit = payload.quantity_unit or "kg"
    item.quantity_kg = payload.quantity_kg
    item.price = payload.price
    item.price_unit = payload.price_unit or "per kg"
    item.price_per_kg = payload.price_per_kg
    item.farmer_name = payload.farmer_name
    item.phone_number = payload.phone_number
    item.address = payload.address
    if payload.latitude is not None:
        item.latitude = payload.latitude
    if payload.longitude is not None:
        item.longitude = payload.longitude
    if payload.photos is not None:
        item.photos = photos_data

    db.commit()
    db.refresh(item)
    return format_listing_response(item, current_user.id)

@router.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    if item.user_id is not None and item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": listing_id}

@router.post("/listings/{listing_id}/report")
def report_listing(
    listing_id: int,
    payload: ListingReportCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    item = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    report = ListingReport(
        listing_id=listing_id,
        reported_by_user_id=current_user.id if current_user else None,
        reason=payload.reason,
        created_at=datetime.utcnow()
    )
    db.add(report)
    db.commit()
    return {
        "status": "reported",
        "listing_id": listing_id,
        "message": "Listing has been reported for moderation review."
    }


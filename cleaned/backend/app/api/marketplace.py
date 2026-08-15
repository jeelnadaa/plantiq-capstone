from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_optional, get_current_user
from app.models.user import User
from app.models.marketplace import CropListing
from app.schemas.marketplace import ListingCreate, ListingResponse

router = APIRouter(prefix="/marketplace", tags=["Farmer Marketplace"])

def format_listing_response(item: CropListing, current_user_id: Optional[int]) -> dict:
    maps_url = f"https://www.google.com/maps/search/?api=1&query={item.latitude},{item.longitude}" if (item.latitude and item.longitude) else None
    return {
        "id": item.id,
        "user_id": item.user_id,
        "title": item.title,
        "variety": item.variety,
        "quantity_kg": item.quantity_kg,
        "price_per_kg": item.price_per_kg,
        "farmer_name": item.farmer_name,
        "phone_number": item.phone_number,
        "address": item.address,
        "latitude": item.latitude,
        "longitude": item.longitude,
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
    variety: Optional[str] = Query(None),
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
    if variety and variety.strip():
        query = query.filter(CropListing.variety.ilike(f"%{variety.strip()}%"))

    items = query.order_by(CropListing.created_at.desc()).all()
    user_id = current_user.id if current_user else None
    return [format_listing_response(item, user_id) for item in items]

@router.post("/listings", response_model=ListingResponse)
def create_listing(
    payload: ListingCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    user_id = current_user.id if current_user else None
    photos_data = [p.dict() if hasattr(p, "dict") else p for p in (payload.photos or [])]
    item = CropListing(
        user_id=user_id,
        title=payload.title,
        variety=payload.variety,
        quantity_kg=payload.quantity_kg,
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

@router.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, current_user: Optional[User] = Depends(get_current_user_optional), db: Session = Depends(get_db)):
    item = db.query(CropListing).filter(CropListing.id == listing_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Listing not found")
    if current_user and item.user_id and item.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this listing")
    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": listing_id}

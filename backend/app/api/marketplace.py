"""Farmer marketplace: browse with search / filters / haversine sort, sell, edit, delete, report."""
from __future__ import annotations

import math
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.core.timeutil import utcnow
from app.models import CropListing, ListingReport, MediaFile, User
from app.schemas.marketplace import ListingIn, ListingOut, PhotoOut, ReportIn
from app.services.storage import media_url

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])
SORTS = ("distance", "newest", "price_asc", "price_desc", "qty_desc")


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return round(r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)


def to_out(item: CropListing, me: User, buyer: tuple[float, float] | None = None, reported: set[int] | None = None) -> ListingOut:
    dist = None
    if buyer and item.latitude is not None and item.longitude is not None:
        dist = haversine_km(buyer[0], buyer[1], item.latitude, item.longitude)
    maps = (f"https://www.google.com/maps/search/?api=1&query={item.latitude},{item.longitude}"
            if item.latitude is not None and item.longitude is not None else
            f"https://www.google.com/maps/search/?api=1&query={quote(item.address)}")
    wa_text = f"Hi {item.farmer_name}, I saw your PlantIQ listing for {item.title}."
    return ListingOut(
        id=item.id, user_id=item.user_id, title=item.title, variety=item.variety, quantity=item.quantity,
        quantity_unit=item.quantity_unit, quantity_kg=item.quantity_kg, price=item.price, price_unit=item.price_unit,
        price_per_kg=item.price_per_kg, farmer_name=item.farmer_name, phone_number=item.phone_number, address=item.address,
        latitude=item.latitude, longitude=item.longitude, distance_km=dist,
        photos=[PhotoOut(media_id=p["media_id"], url=media_url(p["media_id"]), caption=p.get("caption", ""))
                for p in (item.photos or []) if p.get("media_id")],
        created_at=item.created_at, updated_at=item.updated_at, google_maps_url=maps,
        whatsapp_url=f"https://wa.me/91{item.phone_number}?text={quote(wa_text)}",
        is_owner=item.user_id == me.id, reported_by_me=bool(reported and item.id in reported),
    )


def _validate_photos(db: Session, user: User, payload: ListingIn, keep: set[str] | None = None) -> list[dict]:
    if len(payload.photos) > settings.MAX_PHOTOS_PER_LISTING:
        raise HTTPException(422, f"At most {settings.MAX_PHOTOS_PER_LISTING} photos per listing.")
    photos = []
    for p in payload.photos:
        row = db.get(MediaFile, p.media_id)
        if not row or (row.owner_id != user.id and p.media_id not in (keep or set())):
            raise HTTPException(422, "One of the photos was not found. Please upload it again.")
        photos.append({"media_id": p.media_id, "caption": p.caption})
    return photos


@router.get("/listings", response_model=list[ListingOut])
def list_listings(
    q: str | None = Query(None, max_length=100),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_qty: float | None = Query(None, ge=0),
    variety: str | None = Query(None, max_length=60),
    latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180),
    max_distance_km: float | None = Query(None, gt=0, le=20000),
    has_photos: bool | None = Query(None),
    sort_by: str = Query("newest"),
    limit: int = Query(100, ge=1, le=300),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ListingOut]:
    stmt = select(CropListing)
    if q and q.strip():
        term = f"%{q.strip().lower()}%"
        stmt = stmt.where(or_(func.lower(CropListing.title).like(term), func.lower(CropListing.variety).like(term),
                              func.lower(CropListing.address).like(term), func.lower(CropListing.farmer_name).like(term)))
    if min_price is not None:
        stmt = stmt.where(CropListing.price_per_kg >= min_price)
    if max_price is not None:
        stmt = stmt.where(CropListing.price_per_kg <= max_price)
    if min_qty is not None:
        stmt = stmt.where(CropListing.quantity_kg >= min_qty)
    if variety and variety.strip().lower() != "all":
        stmt = stmt.where(func.lower(CropListing.variety).like(f"%{variety.strip().lower()}%"))
    items = db.scalars(stmt.order_by(CropListing.created_at.desc()).limit(1000)).all()

    buyer = (latitude, longitude) if latitude is not None and longitude is not None else None
    reported = set(db.scalars(select(ListingReport.listing_id).where(ListingReport.reported_by_user_id == user.id)).all())
    out = [to_out(i, user, buyer, reported) for i in items]
    if has_photos:
        out = [o for o in out if o.photos]
    if max_distance_km is not None and buyer:
        out = [o for o in out if o.distance_km is not None and o.distance_km <= max_distance_km]

    sort_by = sort_by if sort_by in SORTS else "newest"
    if sort_by == "distance" and buyer:
        out.sort(key=lambda o: (o.distance_km is None, o.distance_km or 0.0))
    elif sort_by == "price_asc":
        out.sort(key=lambda o: o.price_per_kg)
    elif sort_by == "price_desc":
        out.sort(key=lambda o: o.price_per_kg, reverse=True)
    elif sort_by == "qty_desc":
        out.sort(key=lambda o: o.quantity_kg, reverse=True)
    return out[:limit]


@router.get("/my-listings", response_model=list[ListingOut])
def my_listings(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[ListingOut]:
    rows = db.scalars(select(CropListing).where(CropListing.user_id == user.id).order_by(CropListing.created_at.desc())).all()
    return [to_out(i, user) for i in rows]


@router.post("/listings", response_model=ListingOut, status_code=201, dependencies=[Depends(rate_limit("heavy"))])
def create_listing(payload: ListingIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ListingOut:
    count = db.scalar(select(func.count()).select_from(CropListing).where(CropListing.user_id == user.id)) or 0
    if count >= settings.MAX_LISTINGS_PER_USER:
        raise HTTPException(429, f"You can have at most {settings.MAX_LISTINGS_PER_USER} listings. Remove old ones first.")
    item = CropListing(user_id=user.id, **payload.model_dump(exclude={"photos"}), photos=_validate_photos(db, user, payload))
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_out(item, user)


def _owned(db: Session, user: User, listing_id: int) -> CropListing:
    item = db.get(CropListing, listing_id)
    if not item:
        raise HTTPException(404, "Listing not found.")
    if item.user_id != user.id:
        raise HTTPException(403, "You can only change your own listings.")
    return item


@router.get("/listings/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ListingOut:
    item = db.get(CropListing, listing_id)
    if not item:
        raise HTTPException(404, "Listing not found.")
    return to_out(item, user)


@router.put("/listings/{listing_id}", response_model=ListingOut)
def update_listing(listing_id: int, payload: ListingIn, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)) -> ListingOut:
    item = _owned(db, user, listing_id)
    keep = {p["media_id"] for p in (item.photos or [])}
    photos = _validate_photos(db, user, payload, keep)
    for k, v in payload.model_dump(exclude={"photos", "latitude", "longitude"}).items():
        setattr(item, k, v)
    if payload.latitude is not None and payload.longitude is not None:
        item.latitude, item.longitude = payload.latitude, payload.longitude
    item.photos = photos
    item.updated_at = utcnow()
    db.commit()
    db.refresh(item)
    return to_out(item, user)


@router.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    item = _owned(db, user, listing_id)
    db.delete(item)
    db.commit()
    return {"status": "deleted", "id": listing_id}


@router.post("/listings/{listing_id}/report", dependencies=[Depends(rate_limit("auth"))])
def report_listing(listing_id: int, payload: ReportIn, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)) -> dict:
    item = db.get(CropListing, listing_id)
    if not item:
        raise HTTPException(404, "Listing not found.")
    if item.user_id == user.id:
        raise HTTPException(400, "You cannot report your own listing.")
    db.add(ListingReport(listing_id=listing_id, reported_by_user_id=user.id, reason=payload.reason))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "You have already reported this listing.")
    return {"status": "reported", "listing_id": listing_id, "message": "Thanks — the listing will be reviewed."}

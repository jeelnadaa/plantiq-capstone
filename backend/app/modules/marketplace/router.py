from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import uuid
from app.core.database import get_db
from app.core.config import settings
from app.modules.marketplace.models import CropListing
from app.modules.marketplace.schemas import CropListingCreate, CropListingResponse
from app.modules.auth.security import get_current_user
from app.modules.auth.models import User

router = APIRouter(prefix="/api/marketplace", tags=["Marketplace"])

def format_google_maps_url(lat: float, lng: float) -> str:
    """Generates direct Google Maps deep link for location."""
    return f"https://www.google.com/maps/search/?api=1&query={lat},{lng}"

def seed_demo_listings_if_empty(db: Session):
    count = db.query(CropListing).count()
    if count == 0:
        demo_items = [
            CropListing(
                crop_name="Premium Organic Arabica Parchment",
                variety="SLN 795 / Chandragiri",
                quantity_kg=500.0,
                price_per_kg=320.0,
                farmer_name="Ramesh Gowda",
                contact_phone="+91 98450 12345",
                address="Chikmagalur Coffee Estate, Baba Budangiri Road, Chikmagalur",
                latitude=13.3161,
                longitude=75.7720,
                description="Sun-dried high altitude shade grown coffee. Harvested January 2026."
            ),
            CropListing(
                crop_name="Robusta Cherry Grade A",
                variety="CxR Robusta",
                quantity_kg=1200.0,
                price_per_kg=210.0,
                farmer_name="Kaveri Estate (Suresh Kumar)",
                contact_phone="+91 94481 67890",
                address="Madikeri Road, Coorg / Kodagu, Karnataka",
                latitude=12.4244,
                longitude=75.7382,
                description="Bold size cherry, well cured and stored in moisture-proof bags."
            ),
            CropListing(
                crop_name="Specialty Plantation AA Coffee Beans",
                variety="Arabica Selection 9",
                quantity_kg=350.0,
                price_per_kg=410.0,
                farmer_name="Ananth Hegde",
                contact_phone="+91 99002 34567",
                address="Sakleshpur Hills, Hassan District, Karnataka",
                latitude=12.9442,
                longitude=75.7861,
                description="Strictly high grown above 3800ft. Rich floral aroma and clean acidity."
            )
        ]
        db.add_all(demo_items)
        db.commit()

@router.get("/listings", response_model=List[CropListingResponse])
def get_all_listings(
    query: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    seed_demo_listings_if_empty(db)
    q = db.query(CropListing)
    if min_price is not None and min_price >= 0:
        q = q.filter(CropListing.price_per_kg >= min_price)
    if max_price is not None and max_price > 0:
        q = q.filter(CropListing.price_per_kg <= max_price)
    if query and query.strip():
        search_term = f"%{query.strip()}%"
        q = q.filter(
            (CropListing.crop_name.ilike(search_term)) |
            (CropListing.variety.ilike(search_term)) |
            (CropListing.address.ilike(search_term)) |
            (CropListing.farmer_name.ilike(search_term)) |
            (CropListing.description.ilike(search_term))
        )
    return q.order_by(CropListing.created_at.desc()).all()

@router.get("/my-listings", response_model=List[CropListingResponse])
def get_my_listings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieves crop listings created specifically by current authenticated farmer."""
    return db.query(CropListing).filter(CropListing.user_id == current_user.id).order_by(CropListing.created_at.desc()).all()

def geocode_address_if_needed(address: str, lat: Optional[float], lng: Optional[float]):
    if lat is not None and lng is not None and lat != 0 and lng != 0:
        return lat, lng
    try:
        import urllib.request, urllib.parse, json
        encoded_addr = urllib.parse.quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_addr}&format=json&limit=1"
        req = urllib.request.Request(url, headers={'User-Agent': 'PlantIQ-CapstoneApp/1.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data and len(data) > 0:
                    return float(data[0]['lat']), float(data[0]['lon'])
    except Exception as e:
        print(f"[Geocode Exception] {e}")
    return 13.3161, 75.7720

@router.post("/listings", response_model=CropListingResponse)
def create_listing(
    crop_name: str = Form(...),
    variety: str = Form("Arabica"),
    quantity_kg: float = Form(...),
    price_per_kg: float = Form(...),
    farmer_name: str = Form(...),
    contact_phone: str = Form(...),
    address: str = Form(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    description: str = Form(""),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    final_lat, final_lng = geocode_address_if_needed(address, latitude, longitude)

    image_url = None
    if image and image.filename:
        ext = os.path.splitext(image.filename)[1]
        filename = f"crop_{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image.file.read())
        image_url = f"/static/uploads/{filename}"

    new_listing = CropListing(
        crop_name=crop_name,
        variety=variety,
        quantity_kg=quantity_kg,
        price_per_kg=price_per_kg,
        farmer_name=farmer_name,
        contact_phone=contact_phone,
        address=address,
        latitude=final_lat,
        longitude=final_lng,
        description=description,
        image_url=image_url,
        user_id=current_user.id
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    return CropListingResponse.model_validate(new_listing)

@router.delete("/listings/{listing_id}")
def delete_my_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deletes a crop listing owned by current user."""
    listing = db.query(CropListing).filter(CropListing.id == listing_id, CropListing.user_id == current_user.id).first()
    if not listing:
        raise HTTPException(status_code=4404, detail="Listing not found or unauthorized.")
    db.delete(listing)
    db.commit()
    return {"status": "deleted", "id": listing_id}

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import uuid
from app.core.database import get_db
from app.core.config import settings
from app.modules.marketplace.models import CropListing
from app.modules.marketplace.schemas import CropListingCreate, CropListingResponse

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
def get_all_listings(db: Session = Depends(get_db)):
    seed_demo_listings_if_empty(db)
    listings = db.query(CropListing).order_by(CropListing.created_at.desc()).all()
    return [CropListingResponse.model_validate(item) for item in listings]

@router.post("/listings", response_model=CropListingResponse)
def create_listing(
    crop_name: str = Form(...),
    variety: str = Form("Arabica"),
    quantity_kg: float = Form(...),
    price_per_kg: float = Form(...),
    farmer_name: str = Form(...),
    contact_phone: str = Form(...),
    address: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: str = Form(""),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
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
        latitude=latitude,
        longitude=longitude,
        description=description,
        image_url=image_url
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    return CropListingResponse.model_validate(new_listing)

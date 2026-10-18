"""
Test Suite: Module 4 — Spatial Peer-to-Peer Marketplace & Discovery
File: tests/test_market.py
Coverage:
- Marketplace CropListing Validation & Multi-Photo JSON Galleries
- Haversine Great-Circle Distance Formulation
- Dynamic Google Maps Navigation & WhatsApp Direct Intent Handshakes
- Marketplace Search Filtering & Price Range Constraints
"""

import math
import urllib.parse
import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.models.marketplace import Base as MktBase, CropListing, ListingReport
from app.api.marketplace import format_listing_response
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Ensure database tables exist
MktBase.metadata.create_all(bind=engine)


class TestMarketModule:
    """Module 4: Spatial Market Discovery Functional Test Suite"""

    # --- 1. Marketplace Listing CRUD & Photo Galleries ---
    def test_marketplace_listing_creation_and_photos(self):
        """TC-MKT-01: Verifies listing creation, multi-photo JSON, and dynamic Google Maps URL."""
        db = SessionLocal()
        listing_id = None
        try:
            photos_payload = [
                {"url": "data:image/jpeg;base64,AAA111", "caption": "Sun-dried parchment batch #1"},
                {"url": "data:image/jpeg;base64,BBB222", "caption": "Screen 18 beans moisture 10.2%"}
            ]

            item = CropListing(
                user_id=10,
                title="Premium Arabica Selection 795 Lot",
                variety="Arabica Sln 795",
                quantity_kg=1500.0,
                price_per_kg=480.0,
                farmer_name="Shreedhar Hegde",
                phone_number="+91 94481 12345",
                address="Balehonnur, Chikkamagaluru",
                latitude=13.3541,
                longitude=75.4682,
                photos=photos_payload
            )
            db.add(item)
            db.commit()
            db.refresh(item)
            listing_id = item.id

            formatted = format_listing_response(item, current_user_id=10)
            assert formatted["id"] == listing_id
            assert formatted["is_owner"] is True
            assert len(formatted["photos"]) == 2
            assert formatted["photos"][0]["caption"] == "Sun-dried parchment batch #1"
            assert "https://www.google.com/maps/search/?api=1&query=13.3541,75.4682" in formatted["google_maps_url"]
        finally:
            if listing_id:
                db.query(CropListing).filter(CropListing.id == listing_id).delete()
                db.commit()
            db.close()

    # --- 2. Haversine Distance Spatial Formulation ---
    def test_haversine_great_circle_distance(self):
        """TC-MKT-02: Verifies Haversine formula calculates correct spatial distance between coordinates."""
        # Chikkamagaluru (13.3161°N, 75.7720°E) to Mudigere (13.1364°N, 75.6417°E)
        lat1, lng1 = 13.3161, 75.7720
        lat2, lng2 = 13.1364, 75.6417

        r = 6371.0  # Earth radius in km
        d_lat = math.radians(lat2 - lat1)
        d_lng = math.radians(lng2 - lng1)
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        distance_km = r * c

        # Physical distance between Chikkamagaluru and Mudigere is ~24-26 km
        assert 22.0 <= distance_km <= 28.0, f"Calculated distance {distance_km:.2f} km outside expected range"

    # --- 3. Direct Communication Handshakes ---
    def test_whatsapp_and_telephony_intent_url_generation(self):
        """TC-MKT-03: Verifies WhatsApp direct URL and native telephone dialer formatting."""
        phone = "+91 94812 34567"
        clean_phone = "".join(filter(str.isdigit, phone))
        assert clean_phone == "919481234567"

        farmer_name = "Manjunath"
        title = "Arabica Cherry"
        msg = f"Hi {farmer_name}, I saw your listing on PlantIQ for {title}."
        encoded_msg = urllib.parse.quote(msg)

        wa_url = f"https://wa.me/{clean_phone}?text={encoded_msg}"
        tel_url = f"tel:{phone}"

        assert wa_url.startswith("https://wa.me/919481234567?text=Hi%20Manjunath")
        assert tel_url == "tel:+91 94812 34567"

    # --- 4. Marketplace Query Search and Price Filtering ---
    def test_marketplace_filtering_and_search(self):
        """TC-MKT-04: Verifies SQL-level filtering by price range and variety keyword."""
        db = SessionLocal()
        item_id = None
        try:
            item = CropListing(
                user_id=12,
                title="Robusta Parchment Grade AB",
                variety="Robusta CXR",
                quantity_kg=800.0,
                price_per_kg=320.0,
                farmer_name="Anand Rao",
                phone_number="9845112233",
                address="Sakleshpur, Hassan",
                latitude=12.9442,
                longitude=75.7865
            )
            db.add(item)
            db.commit()
            db.refresh(item)
            item_id = item.id

            # Filter by price range
            matches = db.query(CropListing).filter(
                CropListing.price_per_kg >= 300.0,
                CropListing.price_per_kg <= 350.0,
                CropListing.variety.ilike("%Robusta%")
            ).all()

            assert len(matches) > 0
            assert any(m.id == item_id for m in matches)
        finally:
            if item_id:
                db.query(CropListing).filter(CropListing.id == item_id).delete()
                db.commit()
            db.close()

    # --- 5. Security: Bounds Validation, XSS Neutralization & Abuse Reporting ---
    def test_marketplace_security_bounds_and_reporting(self):
        """TC-MKT-05: Verifies negative price bounds rejection, XSS escaping, and moderation reporting."""
        # 1. Negative price must be rejected with 422 Unprocessable Entity
        invalid_payload = {
            "title": "Subsidized Crop Lot",
            "variety": "Robusta",
            "quantity_kg": 500.0,
            "price_per_kg": -25.0,  # Negative price -> invalid
            "farmer_name": "Ravi Kumar",
            "phone_number": "9876543210",
            "address": "Chikkamagaluru"
        }
        resp_bad = client.post("/api/marketplace/listings", json=invalid_payload)
        assert resp_bad.status_code == 422, f"Expected 422 for negative price, got {resp_bad.status_code}"

        # 2. Extreme quantity overflow (> 100,000 kg) must be rejected with 422
        overflow_payload = {
            "title": "Massive Bogus Lot",
            "variety": "Arabica",
            "quantity_kg": 5000000.0,  # 5,000 tons -> exceeds 100,000 kg limit
            "price_per_kg": 400.0,
            "farmer_name": "Ravi Kumar",
            "phone_number": "9876543210",
            "address": "Chikkamagaluru"
        }
        resp_overflow = client.post("/api/marketplace/listings", json=overflow_payload)
        assert resp_overflow.status_code == 422, f"Expected 422 for overflow quantity, got {resp_overflow.status_code}"

        # 3. Valid listing with HTML injection attempt must be safely escaped
        xss_payload = {
            "title": "Parchment Lot <script>alert('xss')</script>",
            "variety": "Arabica Sln 9",
            "quantity_kg": 250.0,
            "price_per_kg": 420.0,
            "farmer_name": "<b>Farmer Suresh</b>",
            "phone_number": "9876543210",
            "address": "Aldur, Chikkamagaluru"
        }
        resp_create = client.post("/api/marketplace/listings", json=xss_payload)
        assert resp_create.status_code == 200
        created = resp_create.json()
        listing_id = created["id"]

        try:
            # Verify HTML characters were escaped
            assert "<script>" not in created["title"]
            assert "&lt;script&gt;" in created["title"]
            assert "<b>" not in created["farmer_name"]
            assert "&lt;b&gt;" in created["farmer_name"]

            # 4. Report the listing for moderation review
            report_resp = client.post(
                f"/api/marketplace/listings/{listing_id}/report",
                json={"reason": "Suspected spam or incorrect price entry"}
            )
            assert report_resp.status_code == 200
            assert report_resp.json()["status"] == "reported"
        finally:
            # Clean up
            db = SessionLocal()
            db.query(ListingReport).filter(ListingReport.listing_id == listing_id).delete()
            db.query(CropListing).filter(CropListing.id == listing_id).delete()
            db.commit()
            db.close()

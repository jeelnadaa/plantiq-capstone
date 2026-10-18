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

    # --- 6. Phone Number 10-Digit Regex & Flexible Agricultural Units ---
    def test_marketplace_phone_regex_and_custom_units(self):
        """TC-MKT-06: Verifies strict 10-digit phone regex checking and dynamic unit conversions (per x kg, per y ton)."""
        created_ids = []
        db = SessionLocal()
        try:
            # 1. Phone number regex rejection tests (must be exact 10 digits)
            for bad_phone in ["12345", "987654321", "98765432101", "abcdefghij", "987654321a"]:
                bad_resp = client.post("/api/marketplace/listings", json={
                    "title": "Invalid Phone Test",
                    "variety": "Arabica",
                    "quantity": 100.0,
                    "quantity_unit": "kg",
                    "price": 400.0,
                    "price_unit": "per kg",
                    "farmer_name": "Test Farmer",
                    "phone_number": bad_phone,
                    "address": "Chikkamagaluru"
                })
                assert bad_resp.status_code == 422, f"Expected 422 for phone '{bad_phone}', got {bad_resp.status_code}"

            # 2. Test Custom Quantity Units (e.g. 5 ton -> 5000 kg, 20 bags of 50kg -> 1000 kg)
            ton_resp = client.post("/api/marketplace/listings", json={
                "title": "Bulk Estate Parchment Lot",
                "variety": "Arabica Sln 795",
                "quantity": 5.0,
                "quantity_unit": "ton",
                "price": 35000.0,
                "price_unit": "per ton",
                "farmer_name": "Estate Manager",
                "phone_number": "9448112345",
                "address": "Balehonnur"
            })
            assert ton_resp.status_code == 200
            ton_data = ton_resp.json()
            created_ids.append(ton_data["id"])
            assert ton_data["quantity"] == 5.0
            assert ton_data["quantity_unit"] == "ton"
            assert ton_data["quantity_kg"] == 5000.0  # 5 * 1000 kg
            assert ton_data["price"] == 35000.0
            assert ton_data["price_unit"] == "per ton"
            assert ton_data["price_per_kg"] == 35.0  # 35000 / 1000 kg

            # 3. Test Custom Price Units: "per 2 kg" (e.g. ₹900 per 2 kg -> ₹450 / kg)
            two_kg_resp = client.post("/api/marketplace/listings", json={
                "title": "Specialty Roasted Beans Sample",
                "variety": "Geisha",
                "quantity": 10.0,
                "quantity_unit": "kg",
                "price": 900.0,
                "price_unit": "per 2 kg",
                "farmer_name": "Roaster Kumar",
                "phone_number": "9876501234",
                "address": "Aldur"
            })
            assert two_kg_resp.status_code == 200
            two_kg_data = two_kg_resp.json()
            created_ids.append(two_kg_data["id"])
            assert two_kg_data["price"] == 900.0
            assert two_kg_data["price_unit"] == "per 2 kg"
            assert two_kg_data["price_per_kg"] == 450.0  # 900 / 2 kg

            # 4. Test Custom Price Units: "per 2 ton" (e.g. ₹70,000 per 2 ton -> ₹35 / kg)
            two_ton_resp = client.post("/api/marketplace/listings", json={
                "title": "Commercial Grade Robusta",
                "variety": "Robusta CXR",
                "quantity": 2.0,
                "quantity_unit": "ton",
                "price": 70000.0,
                "price_unit": "per 2 ton",
                "farmer_name": "Grower Anand",
                "phone_number": "9123456780",
                "address": "Sakleshpur"
            })
            assert two_ton_resp.status_code == 200
            two_ton_data = two_ton_resp.json()
            created_ids.append(two_ton_data["id"])
            assert two_ton_data["price"] == 70000.0
            assert two_ton_data["price_unit"] == "per 2 ton"
            assert two_ton_data["price_per_kg"] == 35.0  # 70000 / 2000 kg

            # 5. Test Bag Unit: "per 50kg bag" (e.g. ₹2,500 per 50kg bag -> ₹50 / kg)
            bag_resp = client.post("/api/marketplace/listings", json={
                "title": "Standard Cherry Lot",
                "variety": "Arabica",
                "quantity": 20.0,
                "quantity_unit": "bag (50kg)",
                "price": 2500.0,
                "price_unit": "per 50kg bag",
                "farmer_name": "Farmer Naveen",
                "phone_number": "9845112233",
                "address": "Mudigere"
            })
            assert bag_resp.status_code == 200
            bag_data = bag_resp.json()
            created_ids.append(bag_data["id"])
            assert bag_data["quantity_kg"] == 1000.0  # 20 * 50 kg
            assert bag_data["price_per_kg"] == 50.0  # 2500 / 50 kg

        finally:
            for lid in created_ids:
                db.query(ListingReport).filter(ListingReport.listing_id == lid).delete()
                db.query(CropListing).filter(CropListing.id == lid).delete()
            db.commit()
            db.close()


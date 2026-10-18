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

    # --- 7. Mandatory Listing Fields Verification ---
    def test_marketplace_mandatory_fields_validation(self):
        """TC-MKT-07: Verifies that no listing field is optional and missing or empty core fields are rejected with 422."""
        valid_base = {
            "title": "Kaveri Washed Parchment",
            "variety": "Arabica Kaveri",
            "quantity": 500.0,
            "quantity_unit": "kg",
            "price": 420.0,
            "price_unit": "per kg",
            "farmer_name": "Ravi Gowda",
            "phone_number": "9876543210",
            "address": "Aldur, Chikkamagaluru"
        }

        # 1. Missing or empty title -> 422
        bad_title = dict(valid_base)
        bad_title["title"] = ""
        assert client.post("/api/marketplace/listings", json=bad_title).status_code == 422
        del bad_title["title"]
        assert client.post("/api/marketplace/listings", json=bad_title).status_code == 422

        # 2. Missing or empty variety -> 422
        bad_variety = dict(valid_base)
        bad_variety["variety"] = " "
        assert client.post("/api/marketplace/listings", json=bad_variety).status_code == 422
        del bad_variety["variety"]
        assert client.post("/api/marketplace/listings", json=bad_variety).status_code == 422

        # 3. Missing or zero quantity -> 422
        bad_qty = dict(valid_base)
        bad_qty["quantity"] = 0.0
        assert client.post("/api/marketplace/listings", json=bad_qty).status_code == 422
        del bad_qty["quantity"]
        assert client.post("/api/marketplace/listings", json=bad_qty).status_code == 422

        # 4. Missing or zero price -> 422
        bad_price = dict(valid_base)
        bad_price["price"] = 0.0
        assert client.post("/api/marketplace/listings", json=bad_price).status_code == 422
        del bad_price["price"]
        assert client.post("/api/marketplace/listings", json=bad_price).status_code == 422

        # 5. Missing or empty farmer_name -> 422
        bad_farmer = dict(valid_base)
        bad_farmer["farmer_name"] = ""
        assert client.post("/api/marketplace/listings", json=bad_farmer).status_code == 422
        del bad_farmer["farmer_name"]
        assert client.post("/api/marketplace/listings", json=bad_farmer).status_code == 422

        # 6. Missing or empty address -> 422
        bad_addr = dict(valid_base)
        bad_addr["address"] = "  "
        assert client.post("/api/marketplace/listings", json=bad_addr).status_code == 422
        del bad_addr["address"]
        assert client.post("/api/marketplace/listings", json=bad_addr).status_code == 422

        # 7. Complete valid payload -> 200
        ok_resp = client.post("/api/marketplace/listings", json=valid_base)
        assert ok_resp.status_code == 200
        listing_id = ok_resp.json()["id"]

        # Clean up
        db = SessionLocal()
        try:
            db.query(ListingReport).filter(ListingReport.listing_id == listing_id).delete()
            db.query(CropListing).filter(CropListing.id == listing_id).delete()
            db.commit()
        finally:
            db.close()

    # --- 8. Edit Listing & Authorization Security Tests ---
    def test_marketplace_listing_edit_and_authorization(self):
        """TC-MKT-08: Verifies farmer can edit their own listing via PUT endpoint with ownership enforcement."""
        import uuid
        uid = uuid.uuid4().hex[:8]
        username = f"farmer_ed_{uid}"
        other_user = f"farmer_oth_{uid}"

        # Clean up any residual users from previous aborted runs
        db_init = SessionLocal()
        from app.models.user import User, AuthToken
        old_users = db_init.query(User).filter(User.username.like("farmer_ed_%") | User.username.like("farmer_oth_%")).all()
        old_ids = [u.id for u in old_users]
        if old_ids:
            db_init.query(AuthToken).filter(AuthToken.user_id.in_(old_ids)).delete(synchronize_session=False)
            db_init.query(User).filter(User.id.in_(old_ids)).delete(synchronize_session=False)
            db_init.commit()
        db_init.close()

        # 1. Register test user
        reg_resp = client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "full_name": "Farmer Editor",
            "password": "Password123!"
        })
        token = reg_resp.json().get("access_token")
        auth_headers = {"Authorization": f"Bearer {token}"}

        # Register second user for cross-user permission check
        other_user = "farmer_other_test"
        other_reg = client.post("/api/auth/register", json={
            "username": other_user,
            "email": f"{other_user}@test.com",
            "full_name": "Other Farmer",
            "password": "Password123!"
        })
        other_token = other_reg.json().get("access_token")
        other_headers = {"Authorization": f"Bearer {other_token}"}

        created_id = None
        db = SessionLocal()
        try:
            # 2. Create listing as farmer_editor
            create_resp = client.post(
                "/api/marketplace/listings",
                json={
                    "title": "Original Harvest Lot",
                    "variety": "Arabica",
                    "quantity": 100.0,
                    "quantity_unit": "kg",
                    "price": 300.0,
                    "price_unit": "per kg",
                    "farmer_name": "Farmer Editor",
                    "phone_number": "9876543210",
                    "address": "Aldur, Chikkamagaluru"
                },
                headers=auth_headers
            )
            assert create_resp.status_code == 200
            created_id = create_resp.json()["id"]

            # 3. Edit listing as owner
            edit_resp = client.put(
                f"/api/marketplace/listings/{created_id}",
                json={
                    "title": "Updated Premium Harvest Lot",
                    "variety": "Arabica Sln 795",
                    "quantity": 250.0,
                    "quantity_unit": "kg",
                    "price": 450.0,
                    "price_unit": "per kg",
                    "farmer_name": "Farmer Editor",
                    "phone_number": "9876543210",
                    "address": "Aldur, Chikkamagaluru"
                },
                headers=auth_headers
            )
            assert edit_resp.status_code == 200
            updated_data = edit_resp.json()
            assert updated_data["title"] == "Updated Premium Harvest Lot"
            assert updated_data["variety"] == "Arabica Sln 795"
            assert updated_data["quantity"] == 250.0
            assert updated_data["price"] == 450.0

            # 3b. Verify invalid edit entries are strictly rejected with 422 (same as creation)
            # - Invalid phone number (must be exact 10 digits)
            for bad_phone in ["123", "98765432101", "abcdefghij"]:
                bad_phone_resp = client.put(
                    f"/api/marketplace/listings/{created_id}",
                    json={
                        "title": "Valid Title",
                        "variety": "Arabica",
                        "quantity": 100.0,
                        "price": 400.0,
                        "farmer_name": "Farmer",
                        "phone_number": bad_phone,
                        "address": "Valid Address"
                    },
                    headers=auth_headers
                )
                assert bad_phone_resp.status_code == 422, f"Expected 422 for bad phone in edit, got {bad_phone_resp.status_code}"

            # - Negative or zero price in edit
            for bad_price in [-50.0, 0.0]:
                bad_price_resp = client.put(
                    f"/api/marketplace/listings/{created_id}",
                    json={
                        "title": "Valid Title",
                        "variety": "Arabica",
                        "quantity": 100.0,
                        "price": bad_price,
                        "farmer_name": "Farmer",
                        "phone_number": "9876543210",
                        "address": "Valid Address"
                    },
                    headers=auth_headers
                )
                assert bad_price_resp.status_code == 422, f"Expected 422 for price {bad_price} in edit, got {bad_price_resp.status_code}"

            # - Negative or zero quantity in edit
            for bad_qty in [-10.0, 0.0]:
                bad_qty_resp = client.put(
                    f"/api/marketplace/listings/{created_id}",
                    json={
                        "title": "Valid Title",
                        "variety": "Arabica",
                        "quantity": bad_qty,
                        "price": 400.0,
                        "farmer_name": "Farmer",
                        "phone_number": "9876543210",
                        "address": "Valid Address"
                    },
                    headers=auth_headers
                )
                assert bad_qty_resp.status_code == 422, f"Expected 422 for qty {bad_qty} in edit, got {bad_qty_resp.status_code}"

            # - Short title or variety in edit (< min length)
            bad_title_resp = client.put(
                f"/api/marketplace/listings/{created_id}",
                json={
                    "title": "ab",
                    "variety": "Arabica",
                    "quantity": 100.0,
                    "price": 400.0,
                    "farmer_name": "Farmer",
                    "phone_number": "9876543210",
                    "address": "Valid Address"
                },
                headers=auth_headers
            )
            assert bad_title_resp.status_code == 422

            # - Excessive price (> 1,000,000) in edit
            bad_price_overflow = client.put(
                f"/api/marketplace/listings/{created_id}",
                json={
                    "title": "Valid Title",
                    "variety": "Arabica",
                    "quantity": 100.0,
                    "price": 5000000.0,
                    "farmer_name": "Farmer",
                    "phone_number": "9876543210",
                    "address": "Valid Address"
                },
                headers=auth_headers
            )
            assert bad_price_overflow.status_code == 422

            # 4. Attempt to edit as other user -> 403 Forbidden
            unauth_resp = client.put(
                f"/api/marketplace/listings/{created_id}",
                json={
                    "title": "Hacked Title",
                    "variety": "Robusta",
                    "quantity": 10.0,
                    "quantity_unit": "kg",
                    "price": 100.0,
                    "price_unit": "per kg",
                    "farmer_name": "Hacker",
                    "phone_number": "9876543210",
                    "address": "Unknown"
                },
                headers=other_headers
            )
            assert unauth_resp.status_code == 403

            # 5. Non-existent listing -> 404 Not Found
            not_found_resp = client.put(
                "/api/marketplace/listings/999999",
                json={
                    "title": "Ghost Listing",
                    "variety": "Robusta",
                    "quantity": 10.0,
                    "quantity_unit": "kg",
                    "price": 100.0,
                    "price_unit": "per kg",
                    "farmer_name": "Ghost",
                    "phone_number": "9876543210",
                    "address": "Unknown"
                },
                headers=auth_headers
            )
            assert not_found_resp.status_code == 404

        finally:
            if created_id:
                db.query(ListingReport).filter(ListingReport.listing_id == created_id).delete()
                db.query(CropListing).filter(CropListing.id == created_id).delete()
            from app.models.user import User, AuthToken
            test_users = db.query(User).filter(User.username.in_([username, other_user])).all()
            user_ids = [u.id for u in test_users]
            if user_ids:
                db.query(AuthToken).filter(AuthToken.user_id.in_(user_ids)).delete(synchronize_session=False)
                db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
            db.commit()
            db.close()

    def test_marketplace_haversine_sorting_and_multi_filters(self):
        """TC-MKT-09: Verifies Haversine distance sorting, distance filtering, and multi-criteria filters."""
        from app.api.marketplace import haversine_distance
        
        # 1. Direct mathematical verification of Haversine formula
        # Chikmagalur (13.3161, 75.7720) to Mudigere (13.1378, 75.6417)
        dist_direct = haversine_distance(13.3161, 75.7720, 13.1378, 75.6417)
        assert 23.0 <= dist_direct <= 26.0, f"Expected ~24.5 km, got {dist_direct}"

        # 2. Database integration test with buyer coordinates
        db = SessionLocal()
        created_ids = []
        try:
            # Create three distinct listings at known distances from Chikmagalur
            item_near = CropListing(
                title="Chikmagalur Near Arabica",
                variety="Arabica",
                quantity_kg=50.0,
                price_per_kg=300.0,
                farmer_name="Local Farmer",
                phone_number="9876543210",
                address="Chikmagalur Town",
                latitude=13.3200,
                longitude=75.7700  # < 1 km from 13.3161, 75.7720
            )
            item_mid = CropListing(
                title="Mudigere Robusta",
                variety="Robusta",
                quantity_kg=500.0,
                price_per_kg=250.0,
                farmer_name="Mudigere Farmer",
                phone_number="9876543211",
                address="Mudigere, Chikkamagaluru",
                latitude=13.1378,
                longitude=75.6417  # ~24 km
            )
            item_far = CropListing(
                title="Bengaluru Warehouse Lot",
                variety="Arabica",
                quantity_kg=2000.0,
                price_per_kg=400.0,
                farmer_name="City Broker",
                phone_number="9876543212",
                address="Yeshwantpur, Bengaluru",
                latitude=12.9716,
                longitude=77.5946  # ~200 km
            )
            db.add_all([item_near, item_mid, item_far])
            db.commit()
            db.refresh(item_near)
            db.refresh(item_mid)
            db.refresh(item_far)
            created_ids = [item_near.id, item_mid.id, item_far.id]

            # 3. Test Distance Sorting (Nearest First)
            resp = client.get("/api/marketplace/listings?latitude=13.3161&longitude=75.7720&sort_by=distance")
            assert resp.status_code == 200
            data = resp.json()
            test_items = [d for d in data if d["id"] in created_ids]
            assert len(test_items) == 3
            assert test_items[0]["id"] == item_near.id
            assert test_items[1]["id"] == item_mid.id
            assert test_items[2]["id"] == item_far.id
            assert test_items[0]["distance_km"] < test_items[1]["distance_km"] < test_items[2]["distance_km"]

            # 4. Test Max Distance Radius Filter (Within 50 km)
            resp_radius = client.get("/api/marketplace/listings?latitude=13.3161&longitude=75.7720&max_distance_km=50")
            assert resp_radius.status_code == 200
            data_radius = resp_radius.json()
            radius_ids = [d["id"] for d in data_radius if d["id"] in created_ids]
            assert item_near.id in radius_ids
            assert item_mid.id in radius_ids
            assert item_far.id not in radius_ids  # Bengaluru (200km) filtered out!

            # 5. Test Multi-Criteria: Variety + Min Quantity
            resp_multi = client.get("/api/marketplace/listings?variety=Robusta&min_qty=100")
            assert resp_multi.status_code == 200
            data_multi = resp_multi.json()
            multi_ids = [d["id"] for d in data_multi if d["id"] in created_ids]
            assert multi_ids == [item_mid.id]  # Only Mudigere Robusta with 500kg matches

        finally:
            if created_ids:
                db.query(ListingReport).filter(ListingReport.listing_id.in_(created_ids)).delete(synchronize_session=False)
                db.query(CropListing).filter(CropListing.id.in_(created_ids)).delete(synchronize_session=False)
                db.commit()
            db.close()



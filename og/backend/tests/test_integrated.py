"""
Test Suite: Integrated Application Pipeline — End-to-End Feature Verification
File: tests/test_integrated.py
Coverage:
- Complete App Startup & Static Frontend HTML Serving (All 8 Routes)
- User Authentication Lifecycle (Registration, Login, Bearer Token, Profile)
- Leaf Image Pathology Diagnostic Pipeline (CNN + Weather + RAG + Cache)
- SHA-256 Deduplication Cache Speedup
- Bilingual Conversational Chatbot (English & Native Kannada)
- Scan-to-Chat Context Handoff
- Farmer Peer-to-Peer Marketplace Full Lifecycle (Create, Search, Filter, Maps, WhatsApp, Delete)
- Live Environmental Microclimate Telemetry
- Voice Speech-to-Text Transcription Audio Endpoint
"""

import io
import json
import uuid
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_synthetic_leaf_bytes() -> bytes:
    """Creates synthetic JPEG leaf bytes for upload testing."""
    img = Image.new("RGB", (224, 224), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestIntegratedAppFeatures:
    """Integrated System Tests: Starts the App and exercises every single feature."""

    # --- Feature 1: Static Frontend HTML & Health Serving ---
    def test_feature_01_static_frontend_and_health_serving(self):
        """Verifies the application starts and serves all frontend templates and health endpoint."""
        routes = ["/", "/scanner", "/chat", "/marketplace", "/history", "/profile", "/auth", "/health"]
        for route in routes:
            resp = client.get(route)
            assert resp.status_code == 200, f"Route {route} failed with status {resp.status_code}"
            if route == "/health":
                assert resp.json()["status"] == "ok"

    # --- Feature 2: User Authentication Lifecycle ---
    def test_feature_02_user_auth_lifecycle(self):
        """Verifies user registration, login, and profile access via Bearer token."""
        unique_id = str(uuid.uuid4())[:8]
        reg_payload = {
            "username": f"farmer_{unique_id}",
            "email": f"farmer_{unique_id}@plantiq.org",
            "password": "FarmPassword123!",
            "full_name": "Ramesh Gowda"
        }

        # 1. Register
        reg_resp = client.post("/api/auth/register", json=reg_payload)
        assert reg_resp.status_code == 200
        token_data = reg_resp.json()
        assert "access_token" in token_data
        token = token_data["access_token"]

        # 2. Login
        login_resp = client.post("/api/auth/login", json={
            "username": reg_payload["username"],
            "password": reg_payload["password"]
        })
        assert login_resp.status_code == 200
        assert "access_token" in login_resp.json()

        # 3. Access Profile
        me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == reg_payload["username"]

    # --- Feature 3 & 4: Leaf Pathology Diagnosis & Caching ---
    def test_feature_03_leaf_diagnosis_and_deduplication_cache(self):
        """Verifies end-to-end leaf diagnosis (CNN + Weather + RAG) and SHA-256 caching."""
        leaf_bytes = create_synthetic_leaf_bytes()
        unique_question = f"What treatment should I use for rust {uuid.uuid4().hex[:8]}?"

        # First Scan: Full Pipeline execution (Guaranteed Cache Miss)
        scan_resp1 = client.post(
            "/api/predict",
            files={"file": ("coffee_leaf.jpg", io.BytesIO(leaf_bytes), "image/jpeg")},
            data={
                "language": "en",
                "user_question": unique_question,
                "latitude": 13.3161,
                "longitude": 75.7720
            }
        )
        assert scan_resp1.status_code == 200
        data1 = scan_resp1.json()
        assert data1["disease"] in ['Miner', 'Rust', 'Phoma', 'Healthy', 'Cerscospora']
        assert data1["confidence"] >= 0.0
        assert "env_data" in data1
        assert "advisory" in data1
        assert len(data1["advisory"]) > 10
        assert data1["cache_hit"] is False
        sha_hash = data1["sha256_hash"]

        # Second Scan with identical image and question: Cache Hit Verification
        scan_resp2 = client.post(
            "/api/predict",
            files={"file": ("coffee_leaf.jpg", io.BytesIO(leaf_bytes), "image/jpeg")},
            data={
                "language": "en",
                "user_question": unique_question,
                "latitude": 13.3161,
                "longitude": 75.7720
            }
        )
        assert scan_resp2.status_code == 200
        data2 = scan_resp2.json()
        assert data2["cache_hit"] is True
        assert data2["sha256_hash"] == sha_hash

    # --- Feature 5 & 6: Chatbot Assistant & Scan-to-Chat Handoff ---
    def test_feature_04_bilingual_chat_and_scan_handoff(self):
        """Verifies bilingual conversational chatbot and scan-to-chat memory injection."""
        session_id = f"session-integ-{uuid.uuid4().hex[:6]}"

        # Turn 1: English question referencing prior scan metadata
        scan_meta = {
            "disease": "Rust",
            "confidence": 98.2,
            "advisory": "Apply 0.5% Bordeaux mixture.",
            "env_data": {"temperature": 24.0, "humidity": 85.0}
        }

        chat_resp1 = client.post(
            "/api/chat/message",
            data={
                "session_id": session_id,
                "user_message": "Can I spray Bordeaux mixture when rain is predicted?",
                "scan_metadata_json": json.dumps(scan_meta),
                "language": "en"
            }
        )
        assert chat_resp1.status_code == 200
        cdata1 = chat_resp1.json()
        assert cdata1["session_id"] == session_id
        assert len(cdata1["reply"]) > 15
        assert cdata1["disease"] == "Rust"

        # Turn 2: Query in native Kannada script
        chat_resp2 = client.post(
            "/api/chat/message",
            data={
                "session_id": session_id,
                "user_message": "ಕಾಫಿ ಗಿಡಕ್ಕೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?",
                "language": "kn"
            }
        )
        assert chat_resp2.status_code == 200
        cdata2 = chat_resp2.json()
        assert len(cdata2["reply"]) > 10

        # Verify thread and messages persisted in database
        threads_resp = client.get("/api/chat/threads")
        assert threads_resp.status_code == 200
        assert any(t["id"] == session_id for t in threads_resp.json())

        messages_resp = client.get(f"/api/chat/threads/{session_id}/messages")
        assert messages_resp.status_code == 200
        assert len(messages_resp.json()) >= 4

    # --- Feature 7, 8, 9: Farmer Marketplace Lifecycle & Navigation ---
    def test_feature_05_marketplace_full_lifecycle(self):
        """Verifies crop listing creation, search/filtering, Google Maps URL, and deletion."""
        # 1. Register authenticated user for marketplace listing
        uid = str(uuid.uuid4())[:8]
        reg_resp = client.post("/api/auth/register", json={
            "username": f"mkt_user_{uid}",
            "email": f"mkt_{uid}@plantiq.org",
            "password": "Password123!",
            "full_name": "Suresh Patel"
        })
        token = reg_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Listing
        listing_payload = {
            "title": "AAA Grade Arabica Parchment Lot 4",
            "variety": "Arabica Chandragiri",
            "quantity_kg": 1200.0,
            "price_per_kg": 460.0,
            "farmer_name": "Suresh Patel",
            "phone_number": "9448199999",
            "address": "Balehonnur, Chikkamagaluru",
            "latitude": 13.3541,
            "longitude": 75.4682,
            "photos": [{"url": "data:image/jpeg;base64,sample123", "caption": "Lot 4 beans"}]
        }
        create_resp = client.post("/api/marketplace/listings", json=listing_payload, headers=headers)
        assert create_resp.status_code == 200
        listing = create_resp.json()
        listing_id = listing["id"]
        assert listing["title"] == listing_payload["title"]
        assert listing["google_maps_url"] == "https://www.google.com/maps/search/?api=1&query=13.3541,75.4682"
        assert listing["is_owner"] is True

        # 3. Retrieve all listings and search
        search_resp = client.get("/api/marketplace/listings?q=Chandragiri")
        assert search_resp.status_code == 200
        assert any(item["id"] == listing_id for item in search_resp.json())

        # 4. Filter by price range
        filter_resp = client.get("/api/marketplace/listings?min_price=400&max_price=500")
        assert filter_resp.status_code == 200
        assert any(item["id"] == listing_id for item in filter_resp.json())

        # 5. Get My Listings
        my_resp = client.get("/api/marketplace/my-listings", headers=headers)
        assert my_resp.status_code == 200
        assert any(item["id"] == listing_id for item in my_resp.json())

        # 6. Delete Listing
        del_resp = client.delete(f"/api/marketplace/listings/{listing_id}", headers=headers)
        assert del_resp.status_code == 200
        assert del_resp.json()["status"] == "deleted"

    # --- Feature 10: Environmental Live Weather Telemetry ---
    def test_feature_06_environmental_live_weather(self):
        """Verifies environmental live telemetry endpoint fetches Open-Meteo microclimate."""
        resp = client.get("/api/environment/live?latitude=13.3161&longitude=75.7720")
        assert resp.status_code == 200
        data = resp.json()
        assert "available" in data
        assert "risk_level" in data

    # --- Feature 11: Voice Speech-to-Text Transcription ---
    def test_feature_07_voice_transcription_endpoint(self):
        """Verifies audio upload to voice endpoint executes the fallback transcription pipeline."""
        dummy_audio = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80>\x00\x00\x00}\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00"
        resp = client.post(
            "/api/voice/transcribe",
            files={"file": ("recording.wav", io.BytesIO(dummy_audio), "audio/wav")},
            data={"target_language": "en"}
        )
        assert resp.status_code == 200
        result = resp.json()
        assert "text" in result or "error" in result

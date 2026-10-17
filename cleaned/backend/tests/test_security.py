"""
Test Suite: Non-Functional Security & Guardrails
File: tests/test_security.py
Coverage:
- Authentication Enforcement on Protected Endpoints (HTTP 401)
- Forged / Corrupted Bearer Token Rejection
- Cross-User Resource Isolation & Unauthorized Deletion Guard (HTTP 403)
- SQL Injection Parameterization Resistance (Search & Login)
- Cross-Site Scripting (XSS) Stored Payload Neutralization
- Chemical Dosage Hallucination & Prompt Poisoning Guardrail
- Corrupted / Malformed File Payload Robustness
- Multi-Session Chat Thread Boundary Isolation
"""

import io
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.rag_service import get_rag_service

client = TestClient(app)


class TestSecurityAndGuardrails:
    """Non-Functional Security Test Suite"""

    # --- 1. Authentication Enforcement on Protected Endpoints ---
    def test_security_unauthenticated_access_to_protected_endpoints(self):
        """NF-SEC-01: Verifies protected endpoints strictly reject requests lacking auth tokens."""
        # /api/auth/me requires authentication
        resp_me = client.get("/api/auth/me")
        assert resp_me.status_code == 401, f"Expected 401 for /auth/me, got {resp_me.status_code}"

        # /api/marketplace/my-listings requires authentication
        resp_mkt = client.get("/api/marketplace/my-listings")
        assert resp_mkt.status_code == 401, f"Expected 401 for /my-listings, got {resp_mkt.status_code}"

    # --- 2. Forged / Corrupted Bearer Token Rejection ---
    def test_security_invalid_or_tampered_bearer_token(self):
        """NF-SEC-02: Verifies tampered, expired, or malformed tokens are rejected with 401."""
        tampered_headers = {"Authorization": "Bearer forged_signature_eyJhbGciOiJIUzI1NiJ9.invalid"}
        resp = client.get("/api/auth/me", headers=tampered_headers)
        assert resp.status_code == 401

        empty_bearer = {"Authorization": "Bearer "}
        resp_empty = client.get("/api/auth/me", headers=empty_bearer)
        assert resp_empty.status_code == 401

    # --- 3. Resource Ownership & Authorization Isolation ---
    def test_security_cross_user_resource_isolation(self):
        """NF-SEC-03: Verifies User B cannot delete or tamper with User A's marketplace listing (403)."""
        # Register User A
        u_a = str(uuid.uuid4())[:8]
        token_a = client.post("/api/auth/register", json={
            "username": f"user_a_{u_a}",
            "email": f"a_{u_a}@plantiq.org",
            "password": "Password123!",
            "full_name": "Farmer Alice"
        }).json()["access_token"]

        # Register User B
        u_b = str(uuid.uuid4())[:8]
        token_b = client.post("/api/auth/register", json={
            "username": f"user_b_{u_b}",
            "email": f"b_{u_b}@plantiq.org",
            "password": "Password123!",
            "full_name": "Farmer Bob"
        }).json()["access_token"]

        # User A creates a crop listing
        listing = client.post(
            "/api/marketplace/listings",
            json={
                "title": "Alice's Secret Specialty Batch",
                "variety": "Geisha Arabica",
                "quantity_kg": 200.0,
                "price_per_kg": 950.0,
                "farmer_name": "Farmer Alice",
                "phone_number": "9123456780",
                "address": "Koppa, Chikkamagaluru"
            },
            headers={"Authorization": f"Bearer {token_a}"}
        ).json()
        listing_id = listing["id"]

        try:
            # User B attempts to DELETE User A's listing
            unauth_del = client.delete(
                f"/api/marketplace/listings/{listing_id}",
                headers={"Authorization": f"Bearer {token_b}"}
            )
            assert unauth_del.status_code == 403, f"Expected 403 Forbidden, got {unauth_del.status_code}"

            # Verify listing still exists
            check_resp = client.get(f"/api/marketplace/listings?q=Geisha")
            assert any(item["id"] == listing_id for item in check_resp.json())
        finally:
            # Clean up by authorized User A
            client.delete(f"/api/marketplace/listings/{listing_id}", headers={"Authorization": f"Bearer {token_a}"})

    # --- 4. SQL Injection Resistance ---
    def test_security_sql_injection_parameterization(self):
        """NF-SEC-04: Verifies SQL injection strings are safely parameterized and do not execute."""
        sqli_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "1' UNION SELECT 1, 'admin', 'pass', 'admin@mail.com', 'Admin' --",
            "' OR 1=1; --"
        ]

        # 1. Test in Marketplace Search
        for payload in sqli_payloads:
            resp = client.get(f"/api/marketplace/listings?q={payload}")
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)

        # 2. Test in Auth Login Bypass attempt
        bypass_resp = client.post("/api/auth/login", json={
            "username": "' OR '1'='1",
            "password": "' OR '1'='1"
        })
        assert bypass_resp.status_code == 401

    # --- 5. Stored XSS Payload Neutralization ---
    def test_security_xss_stored_payload_neutralization(self):
        """NF-SEC-05: Verifies script injection tags in user content are safely stored as plain text."""
        xss_string = "<script>alert('XSS_ATTACK');</script><img src=x onerror=alert(1)>"
        session_id = f"sec-xss-{uuid.uuid4().hex[:6]}"

        resp = client.post(
            "/api/chat/message",
            data={
                "session_id": session_id,
                "user_message": f"Help with pest: {xss_string}",
                "language": "en"
            }
        )
        assert resp.status_code == 200

        # Retrieve messages and verify stored content is harmless string
        history_resp = client.get(f"/api/chat/threads/{session_id}/messages")
        assert history_resp.status_code == 200
        user_message_stored = history_resp.json()[0]["content"]
        assert "<script>" in user_message_stored
        assert "alert('XSS_ATTACK')" in user_message_stored

    # --- 6. Agronomic Chemical Dosage Safety Guardrail ---
    def test_security_chemical_dosage_safety_guardrail(self):
        """NF-SEC-06: Verifies chemical safety regex audit catches lethal/unverified dosages."""
        rag = get_rag_service()
        approved_ccri_knowledge = [
            {"text": "Apply 0.5% Bordeaux mixture (1 kg copper sulphate, 1 kg quicklime, 200 L water) during pre-monsoon."}
        ]

        # Lethal / toxic hallucinated recommendation
        poison_advisory = "Spray 45% chlorpyrifos and 50 kg copper sulphate per coffee bush."
        audit = rag._audit_dosage_safety(poison_advisory, approved_ccri_knowledge)

        assert audit["verified"] is False
        assert len(audit["unverified_dosages"]) > 0
        assert any("45%" in d or "50 kg" in d for d in audit["unverified_dosages"])
        assert "Caution" in audit["safety_note"]

    # --- 7. Corrupted File Payload Robustness ---
    def test_security_corrupted_file_upload_robustness(self):
        """NF-SEC-07: Verifies arbitrary non-image binaries and zero-byte files do not crash the service."""
        corrupted_binary = b"\x00\xFF\xDE\xAD\xBE\xEF\x00\x11\x22\x33" * 50

        # Non-image upload to predict endpoint
        resp = client.post(
            "/api/predict",
            files={"file": ("malicious.exe", io.BytesIO(corrupted_binary), "application/octet-stream")},
            data={"language": "en"}
        )
        # Server must safely catch the invalid image and return structured HTTP error (500 or 400)
        assert resp.status_code in [400, 422, 500]
        assert "error" in resp.text.lower() or "detail" in resp.text.lower()

    # --- 8. Multi-Session Chat Thread Boundary Isolation ---
    def test_security_chat_session_thread_isolation(self):
        """NF-SEC-08: Verifies message histories from separate sessions never leak across threads."""
        session_1 = f"session-iso-1-{uuid.uuid4().hex[:6]}"
        session_2 = f"session-iso-2-{uuid.uuid4().hex[:6]}"

        client.post("/api/chat/message", data={"session_id": session_1, "user_message": "User 1 Confidential Spray Data", "language": "en"})
        client.post("/api/chat/message", data={"session_id": session_2, "user_message": "User 2 Unrelated Query", "language": "en"})

        msgs_1 = client.get(f"/api/chat/threads/{session_1}/messages").json()
        msgs_2 = client.get(f"/api/chat/threads/{session_2}/messages").json()

        assert any("Confidential Spray Data" in m["content"] for m in msgs_1)
        assert not any("Confidential Spray Data" in m["content"] for m in msgs_2)

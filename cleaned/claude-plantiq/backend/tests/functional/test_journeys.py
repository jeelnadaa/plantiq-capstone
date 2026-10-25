"""End-to-end user journeys through the public API (what a farmer actually does in the app)."""
import json

import pytest

from tests.conftest import PASSWORD, image_bytes, register, webm_bytes

pytestmark = pytest.mark.functional
API = "/api/v1"


def test_farmer_scan_to_chat_to_history_journey(client, leaf_jpg):
    ravi = register(client, username="ravi", preferred_language="en")
    h = ravi["headers"]

    # 1. Voice question → text
    q = client.post(f"{API}/voice/transcribe", headers=h, files={"file": ("q.webm", webm_bytes(), "audio/webm")},
                    data={"target_language": "en"}).json()["text"]
    # 2. Scan with weather
    scan = client.post(f"{API}/predict", headers=h, files={"file": ("leaf.jpg", leaf_jpg, "image/jpeg")},
                       data={"language": "en", "latitude": "13.3161", "longitude": "75.7720", "user_question": q}).json()
    assert scan["advisory"] and scan["env_data"]["available"]
    # 3. "Ask follow-up in chat" hand-off (scan metadata + image from history)
    media_id = scan["image_url"].split("/")[-1][:-4]
    meta = {k: scan[k] for k in ("disease", "confidence", "advisory", "env_data")}
    chat = client.post(f"{API}/chat/message", headers=h, data={
        "user_message": f"I just diagnosed {scan['disease']}. What spray timing for my estate?",
        "scan_metadata_json": json.dumps(meta), "media_id": media_id, "latitude": "13.3161", "longitude": "75.7720",
    }).json()
    assert chat["disease"] == scan["disease"] and chat["image_url"] == scan["image_url"]
    follow = client.post(f"{API}/chat/message", headers=h, data={"user_message": "Any organic option?",
                                                                  "session_id": chat["session_id"]}).json()
    assert len(follow["history"]) == 4
    # 4. History: open details, delete with undo, clear all with undo
    hist = client.get(f"{API}/scans", headers=h).json()
    assert hist[0]["id"] == scan["scan_id"]
    client.delete(f"{API}/scans/{scan['scan_id']}", headers=h)
    client.post(f"{API}/scans/{scan['scan_id']}/restore", headers=h)
    assert len(client.get(f"{API}/scans", headers=h).json()) == 1
    # 5. Profile stats reflect activity
    assert client.get(f"{API}/users/me/stats", headers=h).json() == {"scans": 1, "listings": 0, "chats": 1}


def test_marketplace_seller_and_buyer_journey(client):
    seller = register(client, username="ravi")
    buyer = register(client, username="meena", phone="9123456780")
    photo = client.post(f"{API}/media", headers=seller["headers"],
                        files={"file": ("lot.jpg", image_bytes(), "image/jpeg")}).json()
    listing = client.post(f"{API}/marketplace/listings", headers=seller["headers"], json={
        "title": "Robusta Cherry", "variety": "Robusta CXR", "quantity": 40, "quantity_unit": "bag (50kg)",
        "price": 9500, "price_unit": "per 50kg bag", "farmer_name": "Ravi Gowda", "phone_number": "98765 43210",
        "address": "Sakleshpur, Hassan", "latitude": 12.94, "longitude": 75.78,
        "photos": [{"media_id": photo["id"], "caption": "Fresh cherry"}]}).json()
    assert listing["price_per_kg"] == 190

    found = client.get(f"{API}/marketplace/listings", headers=buyer["headers"],
                       params={"latitude": 13.0, "longitude": 75.9, "sort_by": "distance", "max_distance_km": 60,
                               "variety": "Robusta", "has_photos": True}).json()
    assert [f["id"] for f in found] == [listing["id"]] and found[0]["distance_km"] < 60
    assert found[0]["whatsapp_url"].startswith("https://wa.me/919876543210") and found[0]["google_maps_url"]
    assert client.post(f"{API}/marketplace/listings/{listing['id']}/report", headers=buyer["headers"],
                       json={"reason": "Price looks wrong"}).status_code == 200

    edited = client.put(f"{API}/marketplace/listings/{listing['id']}", headers=seller["headers"], json={
        **{k: listing[k] for k in ("title", "variety", "quantity", "quantity_unit", "farmer_name", "address")},
        "price": 9000, "price_unit": "per 50kg bag", "phone_number": "9876543210",
        "photos": [{"media_id": photo["id"], "caption": "Fresh cherry, sorted"}]}).json()
    assert edited["price_per_kg"] == 180 and edited["photos"][0]["caption"] == "Fresh cherry, sorted"
    assert client.delete(f"{API}/marketplace/listings/{listing['id']}", headers=seller["headers"]).status_code == 200
    assert client.get(f"{API}/marketplace/listings", headers=buyer["headers"]).json() == []


def test_account_lifecycle_journey(client):
    data = register(client, username="ravi", email="ravi@example.com")
    h = data["headers"]
    client.patch(f"{API}/users/me", json={"preferred_language": "kn"}, headers=h)
    login = client.post(f"{API}/auth/login", json={"identifier": "ravi@example.com", "password": PASSWORD, "remember": False}).json()
    assert login["user"]["preferred_language"] == "kn"
    refreshed = client.post(f"{API}/auth/refresh", json={"refresh_token": login["refresh_token"]}).json()
    nh = {"Authorization": f"Bearer {refreshed['access_token']}"}
    client.post(f"{API}/predict", headers=nh, files={"file": ("l.jpg", image_bytes(), "image/jpeg")})
    client.post(f"{API}/chat/message", headers=nh, data={"user_message": "hello"})
    r = client.request("DELETE", f"{API}/users/me", json={"password": PASSWORD}, headers=nh)
    assert r.status_code == 200
    again = register(client, username="ravi", email="ravi@example.com")  # identifiers are free again
    assert client.get(f"{API}/scans", headers=again["headers"]).json() == []

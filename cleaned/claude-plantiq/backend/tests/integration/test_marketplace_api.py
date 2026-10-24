import pytest

from app.core.config import settings
from tests.conftest import image_bytes

pytestmark = pytest.mark.integration
API = "/api/v1"


def body(**over):
    b = dict(title="Arabica Parchment AA", variety="Arabica SLN 795", quantity=2, quantity_unit="ton", price=420,
             price_unit="per kg", farmer_name="Ravi Gowda", phone_number="9876543210", address="Mudigere, Chikkamagaluru",
             latitude=13.21, longitude=75.64)
    b.update(over)
    return b


def upload(client, headers, color=(10, 120, 30)):
    r = client.post(f"{API}/media", headers=headers, files={"file": ("lot.jpg", image_bytes(color=color), "image/jpeg")},
                    data={"kind": "listing"})
    assert r.status_code == 200, r.text
    return r.json()


def create(client, headers, **over):
    r = client.post(f"{API}/marketplace/listings", json=body(**over), headers=headers)
    assert r.status_code == 201, r.text
    return r.json()


def test_create_listing_with_photos_and_units(client, farmer):
    p1, p2 = upload(client, farmer["headers"]), upload(client, farmer["headers"], (200, 10, 10))
    item = create(client, farmer["headers"], quantity=40, quantity_unit="bag (50kg)", price=9500, price_unit="per 50kg bag",
                  photos=[{"media_id": p1["id"], "caption": "Drying yard"}, {"url": p2["url"], "caption": "Beans"}])
    assert item["quantity_kg"] == 2000 and item["price_per_kg"] == 190 and item["is_owner"]
    assert [p["caption"] for p in item["photos"]] == ["Drying yard", "Beans"]
    assert item["photos"][0]["url"] == p1["url"] and client.get(p1["url"]).status_code == 200
    assert "13.21,75.64" in item["google_maps_url"] and item["whatsapp_url"].startswith("https://wa.me/919876543210")


def test_listing_requires_auth_and_valid_body(client, farmer):
    assert client.post(f"{API}/marketplace/listings", json=body()).status_code == 401
    r = client.post(f"{API}/marketplace/listings", json=body(phone_number="12345"), headers=farmer["headers"])
    assert r.status_code == 422 and r.json()["errors"][0]["field"] == "phone_number"
    r = client.post(f"{API}/marketplace/listings", json=body(price=0), headers=farmer["headers"])
    assert r.status_code == 422 and "price" in r.json()["detail"].lower()


def test_cannot_attach_someone_elses_photo(client, farmer, buyer):
    theirs = upload(client, buyer["headers"])
    r = client.post(f"{API}/marketplace/listings", json=body(photos=[{"media_id": theirs["id"]}]), headers=farmer["headers"])
    assert r.status_code == 422
    r = client.post(f"{API}/marketplace/listings", json=body(photos=[{"media_id": "f" * 32}]), headers=farmer["headers"])
    assert r.status_code == 422


def test_search_filters_and_sorting(client, farmer, buyer):
    h = farmer["headers"]
    create(client, h, title="Arabica near", variety="Arabica", price=400, quantity=100, quantity_unit="kg",
           latitude=13.32, longitude=75.78, photos=[{"media_id": upload(client, h)["id"]}])
    create(client, h, title="Robusta far", variety="Robusta CXR", price=190, quantity=5, quantity_unit="ton",
           latitude=12.42, longitude=75.74, address="Madikeri, Kodagu")
    create(client, h, title="Liberica no gps", variety="Liberica", price=250, quantity=60, quantity_unit="kg",
           latitude=None, longitude=None, farmer_name="Suma")
    q = lambda **p: client.get(f"{API}/marketplace/listings", params=p, headers=buyer["headers"]).json()  # noqa: E731
    me = {"latitude": 13.3161, "longitude": 75.7720}

    near_first = q(sort_by="distance", **me)
    assert [i["title"] for i in near_first] == ["Arabica near", "Robusta far", "Liberica no gps"]
    assert near_first[0]["distance_km"] < 2 and near_first[1]["distance_km"] > 90 and near_first[2]["distance_km"] is None
    assert [i["title"] for i in q(sort_by="price_asc")] == ["Robusta far", "Liberica no gps", "Arabica near"]
    assert q(sort_by="price_desc")[0]["title"] == "Arabica near"
    assert q(sort_by="qty_desc")[0]["title"] == "Robusta far"
    assert q(sort_by="newest")[0]["title"] == "Liberica no gps"
    assert [i["title"] for i in q(max_distance_km=30, **me)] == ["Arabica near"]
    assert len(q(variety="robusta")) == 1 and len(q(variety="all")) == 3
    assert [i["title"] for i in q(min_qty=1000)] == ["Robusta far"]
    assert {i["title"] for i in q(min_price=200, max_price=300)} == {"Liberica no gps"}
    assert [i["title"] for i in q(has_photos=True)] == ["Arabica near"]
    assert {i["title"] for i in q(q="kodagu")} == {"Robusta far"}
    assert {i["title"] for i in q(q="suma")} == {"Liberica no gps"}
    assert not any(i["is_owner"] for i in q())
    assert q(sort_by="nonsense")[0]["title"] == "Liberica no gps"


def test_my_listings_edit_delete(client, farmer, buyer):
    h = farmer["headers"]
    item = create(client, h)
    create(client, buyer["headers"], title="Buyer lot", phone_number="9123456780")
    mine = client.get(f"{API}/marketplace/my-listings", headers=h).json()
    assert [m["id"] for m in mine] == [item["id"]]
    upd = client.put(f"{API}/marketplace/listings/{item['id']}", json=body(title="Updated AA", price=450), headers=h)
    assert upd.status_code == 200 and upd.json()["title"] == "Updated AA" and upd.json()["price_per_kg"] == 450
    assert upd.json()["latitude"] == 13.21
    assert client.get(f"{API}/marketplace/listings/{item['id']}", headers=buyer["headers"]).json()["title"] == "Updated AA"
    assert client.get(f"{API}/users/me/stats", headers=h).json()["listings"] == 1
    assert client.delete(f"{API}/marketplace/listings/{item['id']}", headers=h).status_code == 200
    assert client.get(f"{API}/marketplace/listings/{item['id']}", headers=h).status_code == 404


def test_owner_only_edit_and_delete(client, farmer, buyer):
    item = create(client, farmer["headers"])
    assert client.put(f"{API}/marketplace/listings/{item['id']}", json=body(title="Hijack"), headers=buyer["headers"]).status_code == 403
    assert client.delete(f"{API}/marketplace/listings/{item['id']}", headers=buyer["headers"]).status_code == 403


def test_report_once_and_not_own(client, farmer, buyer):
    item = create(client, farmer["headers"])
    url = f"{API}/marketplace/listings/{item['id']}/report"
    assert client.post(url, json={"reason": "Fake phone number"}, headers=farmer["headers"]).status_code == 400
    assert client.post(url, json={"reason": "Fake phone number"}, headers=buyer["headers"]).status_code == 200
    assert client.post(url, json={"reason": "again"}, headers=buyer["headers"]).status_code == 409
    listed = client.get(f"{API}/marketplace/listings", headers=buyer["headers"]).json()
    assert listed[0]["reported_by_me"] is True
    assert client.post(f"{API}/marketplace/listings/999/report", json={"reason": "abc"}, headers=buyer["headers"]).status_code == 404


def test_listing_quota(client, farmer, monkeypatch):
    monkeypatch.setattr(settings, "MAX_LISTINGS_PER_USER", 2)
    create(client, farmer["headers"])
    create(client, farmer["headers"])
    r = client.post(f"{API}/marketplace/listings", json=body(), headers=farmer["headers"])
    assert r.status_code == 429 and "at most 2" in r.json()["detail"]

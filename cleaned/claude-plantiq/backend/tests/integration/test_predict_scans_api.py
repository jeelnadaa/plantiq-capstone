import pytest

from app.services import registry
from tests.conftest import image_bytes

pytestmark = pytest.mark.integration
API = "/api/v1"


def predict(client, headers, data: bytes, **form):
    return client.post(f"{API}/predict", headers=headers, files={"file": ("leaf.jpg", data, "image/jpeg")},
                       data={"language": "en", **form})


def test_predict_returns_full_diagnosis_and_saves_scan(client, farmer, leaf_jpg):
    r = predict(client, farmer["headers"], leaf_jpg, latitude="13.3161", longitude="75.7720", user_question="When to spray?")
    assert r.status_code == 200, r.text
    d = r.json()
    for key in ("disease", "disease_display", "disease_display_kn", "confidence", "distribution", "env_data", "advisory",
                "citations", "safety_audit", "is_blended", "reasons", "scan_id", "image_url", "sha256_hash"):
        assert key in d
    assert d["cache_hit"] is False and len(d["distribution"]) == 5
    assert d["env_data"]["available"] and d["env_data"]["region_name"].startswith("Chikkamagaluru")
    assert d["advisory"] and d["provider"].startswith("fake")
    img = client.get(d["image_url"])
    assert img.status_code == 200 and img.headers["content-type"] == "image/jpeg"
    scans = client.get(f"{API}/scans", headers=farmer["headers"]).json()
    assert len(scans) == 1 and scans[0]["id"] == d["scan_id"] and scans[0]["question"] == "When to spray?"


def test_predict_without_location_has_unavailable_env(client, farmer, leaf_jpg):
    d = predict(client, farmer["headers"], leaf_jpg).json()
    assert d["env_data"]["available"] is False


def test_predict_cache_hit_on_same_photo_and_question(client, farmer, leaf_jpg):
    first = predict(client, farmer["headers"], leaf_jpg, user_question="dose?").json()
    second = predict(client, farmer["headers"], leaf_jpg, user_question="dose?").json()
    third = predict(client, farmer["headers"], leaf_jpg, user_question="other?").json()
    assert second["cache_hit"] is True and second["disease"] == first["disease"] and second["sha256_hash"] == first["sha256_hash"]
    assert third["cache_hit"] is False
    assert "earlier" in second["reasons"][0]
    assert len(client.get(f"{API}/scans", headers=farmer["headers"]).json()) == 3


def test_predict_cache_is_scoped_per_user(client, farmer, buyer, leaf_jpg):
    predict(client, farmer["headers"], leaf_jpg)
    assert predict(client, buyer["headers"], leaf_jpg).json()["cache_hit"] is False


def test_predict_kannada(client, farmer, leaf_jpg):
    d = predict(client, farmer["headers"], leaf_jpg, language="kn").json()
    assert d["language"] == "kn"


def test_predict_requires_auth_and_valid_image(client, farmer):
    assert predict(client, {}, image_bytes()).status_code == 401
    assert predict(client, farmer["headers"], b"not an image").status_code == 415
    assert predict(client, farmer["headers"], image_bytes(), language="fr").status_code == 422


def test_predict_handles_cnn_failure_safely(client_noraise, farmer):
    client = client_noraise
    class Boom:
        def predict(self, b):
            raise RuntimeError("cuda exploded with secret path C:/secret")

    registry.override("cnn", Boom())
    r = predict(client, farmer["headers"], image_bytes())
    assert r.status_code == 500 and "secret" not in r.text and r.json()["request_id"]


def test_scan_filters_delete_restore(client, farmer):
    h = farmer["headers"]
    ids = [predict(client, h, image_bytes(color=(i * 40, 90, 30))).json()["scan_id"] for i in range(4)]
    all_scans = client.get(f"{API}/scans", headers=h).json()
    assert [s["id"] for s in all_scans] == ids[::-1]  # newest first
    healthy = client.get(f"{API}/scans", params={"kind": "healthy"}, headers=h).json()
    disease = client.get(f"{API}/scans", params={"kind": "disease"}, headers=h).json()
    assert len(healthy) + len(disease) == 4

    assert client.delete(f"{API}/scans/{ids[0]}", headers=h).json()["undo_seconds"] == 3
    assert client.get(f"{API}/scans/{ids[0]}", headers=h).status_code == 404
    assert client.post(f"{API}/scans/{ids[0]}/restore", headers=h).status_code == 200
    assert client.get(f"{API}/scans/{ids[0]}", headers=h).status_code == 200

    cleared = client.delete(f"{API}/scans", headers=h).json()
    assert cleared["count"] == 4 and client.get(f"{API}/scans", headers=h).json() == []
    assert client.post(f"{API}/scans/restore", json={"ids": cleared["ids"]}, headers=h).json()["restored"] == 4
    assert len(client.get(f"{API}/scans", headers=h).json()) == 4
    assert client.get(f"{API}/users/me/stats", headers=h).json()["scans"] == 4


def test_scan_details_contains_report(client, farmer, leaf_jpg):
    sid = predict(client, farmer["headers"], leaf_jpg, latitude="13.3", longitude="75.7").json()["scan_id"]
    s = client.get(f"{API}/scans/{sid}", headers=farmer["headers"]).json()
    assert s["advisory"] and s["env_data"]["available"] and s["distribution"] and s["latitude"] == 13.3


def test_purge_soft_deleted(client, farmer):
    from datetime import timedelta

    from app.api.scans import purge_soft_deleted
    from app.core.db import SessionLocal

    h = farmer["headers"]
    d = predict(client, h, image_bytes()).json()
    client.delete(f"{API}/scans/{d['scan_id']}", headers=h)
    with SessionLocal() as db:
        assert purge_soft_deleted(db, older_than=timedelta(seconds=-1)) == 1
    assert client.get(d["image_url"]).status_code == 404


def test_classes_endpoint(client):
    assert {c["id"] for c in client.get(f"{API}/predict/classes").json()} == {"Miner", "Rust", "Phoma", "Healthy", "Cerscospora"}

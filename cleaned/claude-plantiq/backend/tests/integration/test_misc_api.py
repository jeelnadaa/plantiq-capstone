import pytest

from app.core.config import settings
from tests.conftest import webm_bytes

pytestmark = pytest.mark.integration
API = "/api/v1"


def test_health_both_paths(client):
    for path in ("/health", "/api/health"):
        r = client.get(path)
        assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["version"] == settings.VERSION


def test_original_api_prefix_alias(client, farmer):
    assert client.get("/api/auth/me", headers=farmer["headers"]).status_code == 200
    assert client.get("/api/marketplace/listings", headers=farmer["headers"]).status_code == 200


def test_voice_transcribe_and_status(client, farmer):
    r = client.post(f"{API}/voice/transcribe", headers=farmer["headers"],
                    files={"file": ("voice_note.webm", webm_bytes(), "audio/webm")}, data={"target_language": "kn"})
    assert r.status_code == 200 and r.json()["language"] == "kn" and r.json()["text"]
    en = client.post(f"{API}/voice/transcribe", headers=farmer["headers"],
                     files={"file": ("v.webm", webm_bytes(), "audio/webm")}, data={"target_language": "en"}).json()
    assert en["language"] == "en"
    assert client.get(f"{API}/voice/status", headers=farmer["headers"]).json()["fake"] is True


def test_voice_rejects_bad_audio_and_requires_auth(client, farmer):
    files = {"file": ("x.webm", b"plain text pretending", "audio/webm")}
    assert client.post(f"{API}/voice/transcribe", headers=farmer["headers"], files=files).status_code == 415
    assert client.post(f"{API}/voice/transcribe", files={"file": ("v.webm", webm_bytes(), "audio/webm")}).status_code == 401
    bad_lang = client.post(f"{API}/voice/transcribe", headers=farmer["headers"],
                           files={"file": ("v.webm", webm_bytes(), "audio/webm")}, data={"target_language": "fr"})
    assert bad_lang.status_code == 422


def test_environment_endpoints(client):
    live = client.get(f"{API}/environment/live", params={"latitude": 13.3161, "longitude": 75.772}).json()
    assert live["available"] and live["risk_level"] == "high" and live["spray_window"]
    alias = client.get("/api/environment/microclimate", params={"latitude": 13.3161, "longitude": 75.772}).json()
    assert alias["temperature"] == live["temperature"]
    assert client.get(f"{API}/environment/live").json()["available"] is False
    assert client.get(f"{API}/environment/live", params={"latitude": 13.3}).status_code == 422
    assert client.get(f"{API}/environment/live", params={"latitude": 100, "longitude": 1}).status_code == 422
    fc = client.get(f"{API}/environment/forecast", params={"latitude": 13.3, "longitude": 75.7}).json()
    assert len(fc["forecast"]) == 3


def test_media_upload_and_serving(client, farmer):
    from tests.conftest import image_bytes

    r = client.post(f"{API}/media", headers=farmer["headers"], files={"file": ("a.png", image_bytes("PNG"), "image/png")})
    m = r.json()
    assert r.status_code == 200 and m["url"] == f"/media/{m['id']}.jpg"
    got = client.get(m["url"])
    assert got.status_code == 200 and got.content.startswith(b"\xff\xd8") and got.headers["x-content-type-options"] == "nosniff"
    for bad in ("/media/notanid.jpg", f"/media/{'0' * 32}.jpg", "/media/%2e%2e%2fsecret.jpg"):
        assert client.get(bad).status_code == 404
    traversal = client.get("/media/../../app/core/config.py")  # client normalises to /app/core/config.py
    assert b"SECRET_KEY" not in traversal.content and traversal.headers["content-type"].startswith("application/json")


def test_system_info_has_no_secrets(client, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "AIza-super-secret-value")
    body = client.get(f"{API}/system/info").text
    assert "super-secret" not in body and settings.SECRET_KEY not in body
    assert '"fake_ml":true' in body.replace(" ", "")


def test_spa_fallback_and_unknown_api(client, tmp_path, monkeypatch):
    assert client.get("/api/v1/does-not-exist").status_code == 404
    r = client.get("/some/client/route")
    assert r.status_code == 200  # JSON hint when the UI is not built, index.html when it is


def test_openapi_docs_available_in_dev(client):
    assert client.get("/docs").status_code == 200
    assert "/api/v1/predict" in client.get("/openapi.json").json()["paths"]

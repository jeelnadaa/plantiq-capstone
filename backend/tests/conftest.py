"""Shared fixtures. Environment is fixed BEFORE the app is imported: fake ML, temp SQLite, no real LLM keys."""
from __future__ import annotations

import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="plantiq-tests-"))
os.environ.update({
    "ENV": "test",
    "PLANTIQ_FAKE_ML": "1",
    "DATABASE_URL": f"sqlite:///{(_TMP / 'test.db').as_posix()}",
    "VAR_DIR": str(_TMP / "var"),
    "STATIC_DIR": str(_TMP / "static"),
    "RAG_INDEX_DIR": str(_TMP / "index"),
    "GEMINI_API_KEY": "",
    "GROQ_API_KEY": "",
    "HF_TOKEN": "",
    "RATE_LIMIT_ENABLED": "false",
    "SECRET_KEY": "test-secret-key-for-plantiq-which-is-long-enough-123",
    "ML_DEVICE": "cpu",
})
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx  # noqa: E402
import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.db import Base, engine  # noqa: E402
from app.core.ratelimit import limiter  # noqa: E402
from app.services import registry  # noqa: E402
from app.services.environment import EnvironmentService  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
LEAVES = FIXTURES / "leaves"
PASSWORD = "Coffee2026!"

OPEN_METEO_SAMPLE = {
    "elevation": 1090.0,
    "current": {"temperature_2m": 24.6, "relative_humidity_2m": 88, "rain": 0.0, "precipitation": 0.0,
                "wind_speed_10m": 6.1, "apparent_temperature": 26.0},
    "daily": {"time": ["2026-10-26", "2026-10-27", "2026-10-28"], "precipitation_sum": [6.0, 3.1, 0.2],
              "precipitation_probability_max": [80, 65, 10], "temperature_2m_max": [27, 26, 28],
              "temperature_2m_min": [18, 18, 17], "weather_code": [61, 61, 1]},
}


def weather_transport(payload: dict | None = None, status: int = 200) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json=payload if payload is not None else OPEN_METEO_SAMPLE)
    return httpx.MockTransport(handler)


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    shutil.rmtree(_TMP, ignore_errors=True)


@pytest.fixture(autouse=True)
def _clean_state():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    registry.reset()
    registry.override("env", EnvironmentService(transport=weather_transport()))
    limiter.reset()
    settings.RATE_LIMIT_ENABLED = False
    yield
    registry.reset()


@pytest.fixture
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def register(client: TestClient, username: str = "ravi", phone: str | None = "9876543210", email: str | None = None,
             password: str = PASSWORD, **extra) -> dict:
    body = {"full_name": f"{username.title()} Gowda", "username": username, "password": password,
            "confirm_password": password, "accept_terms": True, **extra}
    if phone:
        body["phone"] = phone
    if email:
        body["email"] = email
    r = client.post("/api/v1/auth/register", json=body)
    assert r.status_code == 201, r.text
    data = r.json()
    data["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
    return data


@pytest.fixture
def farmer(client):
    return register(client)


@pytest.fixture
def buyer(client):
    return register(client, username="meena", phone="9123456780")


def image_bytes(fmt: str = "JPEG", size=(320, 240), color=(40, 120, 60), exif: bytes | None = None) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    kwargs = {"exif": exif} if exif else {}
    img.save(buf, format=fmt, **kwargs)
    return buf.getvalue()


@pytest.fixture
def leaf_jpg() -> bytes:
    path = LEAVES / "rust_sample.jpg"
    return path.read_bytes() if path.exists() else image_bytes()


def webm_bytes() -> bytes:
    return b"\x1a\x45\xdf\xa3" + b"\x00" * 2000


@pytest.fixture
def client_noraise():
    """Client that returns 500 responses instead of re-raising server exceptions."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

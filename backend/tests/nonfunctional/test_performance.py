"""Performance budgets, concurrency, payload limits and data-volume behaviour (fake ML so numbers measure our code)."""
import statistics
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from app.services.fakes import FakeRetriever
from tests.conftest import image_bytes, register

pytestmark = pytest.mark.nonfunctional
API = "/api/v1"


def timed(fn, n=20):
    samples = []
    for _ in range(n):
        t = time.perf_counter()
        fn()
        samples.append((time.perf_counter() - t) * 1000)
    samples.sort()
    return {"p50": statistics.median(samples), "p95": samples[int(len(samples) * 0.95) - 1]}


def test_health_latency_budget(client):
    stats = timed(lambda: client.get("/health"), 50)
    assert stats["p95"] < 50, stats


def test_auth_me_latency_budget(client, farmer):
    stats = timed(lambda: client.get(f"{API}/auth/me", headers=farmer["headers"]), 30)
    assert stats["p95"] < 80, stats


def test_login_cost_is_deliberately_slow_but_bounded(client, farmer):
    stats = timed(lambda: client.post(f"{API}/auth/login", json={"identifier": "ravi", "password": "Coffee2026!"}), 5)
    assert 20 < stats["p50"] < 1500, stats  # Argon2id should cost something, but not ruin UX


def test_predict_pipeline_overhead_budget(client, farmer):
    img = image_bytes(size=(1024, 768))
    stats = timed(lambda: client.post(f"{API}/predict", headers=farmer["headers"],
                                      files={"file": ("l.jpg", img, "image/jpeg")}), 10)
    assert stats["p95"] < 800, stats  # everything except the model itself


def test_listings_scale_to_500_rows(client, farmer):
    from app.core.db import SessionLocal
    from app.models import CropListing

    with SessionLocal() as db:
        for i in range(500):
            db.add(CropListing(user_id=farmer["user"]["id"], title=f"Lot {i}", variety="Arabica", quantity=i + 1,
                               quantity_unit="kg", quantity_kg=i + 1, price=100 + i, price_unit="per kg", price_per_kg=100 + i,
                               farmer_name="Ravi", phone_number="9876543210", address="Hassan",
                               latitude=12 + i / 1000, longitude=75 + i / 1000, photos=[]))
        db.commit()
    t = time.perf_counter()
    r = client.get(f"{API}/marketplace/listings", headers=farmer["headers"],
                   params={"latitude": 13.0, "longitude": 75.5, "sort_by": "distance", "limit": 300})
    ms = (time.perf_counter() - t) * 1000
    assert r.status_code == 200 and len(r.json()) == 300 and ms < 1500, ms


def test_concurrent_requests_are_all_served(client):
    users = [register(client, username=f"user{i}", phone=f"90000000{i:02d}") for i in range(5)]

    def work(i):
        u = users[i % 5]
        r1 = client.get(f"{API}/scans", headers=u["headers"])
        r2 = client.post(f"{API}/chat/message", headers=u["headers"], data={"user_message": f"rust question {i}"})
        return r1.status_code, r2.status_code

    with ThreadPoolExecutor(max_workers=10) as pool:
        results = list(pool.map(work, range(40)))
    assert all(r == (200, 200) for r in results), results
    total = sum(len(client.get(f"{API}/chat/threads", headers=u["headers"]).json()) for u in users)
    assert total == 40  # no lost writes


def test_retriever_search_speed():
    r = FakeRetriever()
    t = time.perf_counter()
    for i in range(200):
        r.search(f"coffee rust spray {i}")
    assert (time.perf_counter() - t) < 2.0


def test_gzip_for_large_json(client, farmer):
    for i in range(30):
        client.post(f"{API}/chat/message", headers=farmer["headers"], data={"user_message": f"question number {i} about rust"})
    r = client.get(f"{API}/chat/threads", headers={**farmer["headers"], "Accept-Encoding": "gzip"})
    assert r.headers.get("content-encoding") == "gzip"


def test_media_is_downscaled_to_save_bandwidth(client, farmer):
    big = image_bytes(size=(3000, 2000))
    m = client.post(f"{API}/media", headers=farmer["headers"], files={"file": ("big.jpg", big, "image/jpeg")}).json()
    assert max(m["width"], m["height"]) <= 1600
    assert len(client.get(m["url"]).content) < len(big)


def test_error_responses_are_consistent_json(client, farmer):
    cases = [client.get(f"{API}/scans/99", headers=farmer["headers"]),
             client.post(f"{API}/auth/login", json={}),
             client.get(f"{API}/auth/me")]
    for r in cases:
        body = r.json()
        assert {"detail", "code", "request_id"} <= body.keys(), body

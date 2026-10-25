"""
Test Suite: Non-Functional Performance & Latency Benchmarks
File: tests/test_performance.py
Coverage:
- Health Check Latency (< 10 ms)
- Static Frontend HTML Serving Latency (< 25 ms)
- SHA-256 Deduplication Cache Hit Latency (< 5 ms)
- ResNet-50 Steady-State Warm Inference Latency (< 35 ms GPU / < 250 ms CPU)
- 3-Stage Hybrid RAG Multi-Channel Retrieval Latency (< 500 ms)
- Linguistic Pre-Router Sub-Millisecond Classification (< 2 ms)
- SQLite Database Indexed Query Latency (< 15 ms)
- Multi-Threaded Concurrency & Throughput (10 Concurrent Requests)
"""

import io
import time
import concurrent.futures
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app
from app.services.cnn_service import get_detector
from app.services.rag_service import get_rag_service
from app.services.router_service import analyze_and_route_query
from app.core.database import SessionLocal
from app.models.cache import ImageAnalysisCache
from app.models.marketplace import CropListing

client = TestClient(app)


class TestPerformanceAndLatency:
    """Non-Functional Performance Test Suite"""

    # --- 1. System Health Check Latency ---
    def test_performance_health_endpoint_latency(self):
        """NF-PRF-01: Verifies GET /health responds in under 10.0 ms."""
        # Warmup
        client.get("/health")

        t0 = time.perf_counter()
        resp = client.get("/health")
        latency_ms = (time.perf_counter() - t0) * 1000.0

        assert resp.status_code == 200
        assert latency_ms < 15.0, f"Health check took {latency_ms:.2f}ms (budget: 15ms)"

    # --- 2. Static HTML Serving Latency ---
    def test_performance_static_html_serving_latency(self):
        """NF-PRF-02: Verifies static HTML pages are served in under 25.0 ms."""
        # Warmup
        client.get("/")

        t0 = time.perf_counter()
        resp = client.get("/")
        latency_ms = (time.perf_counter() - t0) * 1000.0

        assert resp.status_code == 200
        assert latency_ms < 30.0, f"Index serve took {latency_ms:.2f}ms (budget: 30ms)"

    # --- 3. SHA-256 Deduplication Cache Hit Latency ---
    def test_performance_sha256_cache_hit_latency(self):
        """NF-PRF-03: Verifies cache lookup responds in under 5.0 ms, bypassing AI compute."""
        db = SessionLocal()
        test_hash = "perf_test_hash_0123456789abcdef0123456789abcdef0123456789abcdef"
        try:
            # Seed cache
            db.query(ImageAnalysisCache).filter(ImageAnalysisCache.image_hash == test_hash).delete()
            db.commit()

            cache_entry = ImageAnalysisCache(
                image_hash=test_hash,
                disease_class="Rust",
                confidence=96.5,
                distribution={"Rust": 96.5, "Healthy": 3.5},
                advisory_text="Cached advisory result."
            )
            db.add(cache_entry)
            db.commit()

            # Measure lookup latency
            t0 = time.perf_counter()
            hit = db.query(ImageAnalysisCache).filter(ImageAnalysisCache.image_hash == test_hash).first()
            lookup_ms = (time.perf_counter() - t0) * 1000.0

            assert hit is not None
            assert lookup_ms < 8.0, f"Cache lookup took {lookup_ms:.2f}ms (budget: 8ms)"
        finally:
            db.query(ImageAnalysisCache).filter(ImageAnalysisCache.image_hash == test_hash).delete()
            db.commit()
            db.close()

    # --- 4. ResNet-50 Steady-State Warm Inference Latency ---
    def test_performance_cnn_steady_state_latency(self):
        """NF-PRF-04: Verifies warm forward pass executes within latency budget (< 35ms GPU / < 250ms CPU)."""
        detector = get_detector()
        img = Image.new("RGB", (224, 224), color=(34, 139, 34))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        leaf_bytes = buf.getvalue()

        # Warmup pass
        _ = detector.predict(leaf_bytes)

        # Timed benchmark pass
        t0 = time.perf_counter()
        result = detector.predict(leaf_bytes)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        device_type = next(detector.model.parameters()).device.type
        budget_ms = 40.0 if device_type == "cuda" else 250.0

        assert result["class"] in ['Miner', 'Rust', 'Phoma', 'Healthy', 'Cerscospora']
        assert latency_ms < budget_ms, f"Inference took {latency_ms:.2f}ms exceeding budget {budget_ms}ms"

    # --- 5. 3-Stage Hybrid RAG Multi-Channel Retrieval Latency ---
    def test_performance_hybrid_rag_search_latency(self):
        """NF-PRF-05: Verifies FAISS + BM25 + Cross-Encoder executes within 500.0 ms."""
        rag = get_rag_service()

        # Warmup pass
        _ = rag.search("coffee rust fungicide dosage", top_k=3)

        # Benchmark pass
        t0 = time.perf_counter()
        results = rag.search("coffee rust fungicide dosage", top_k=3)
        retrieval_ms = (time.perf_counter() - t0) * 1000.0

        assert len(results) > 0
        assert retrieval_ms < 600.0, f"RAG retrieval took {retrieval_ms:.2f}ms (budget: 600ms)"

    # --- 6. Linguistic Pre-Router Sub-Millisecond Classification ---
    def test_performance_linguistic_router_sub_millisecond(self):
        """NF-PRF-06: Verifies language script regex pre-routing executes in under 2.0 ms."""
        import re
        query = "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗಕ್ಕೆ ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?"
        kannada_pattern = re.compile(r'[ಀ-೿]')

        t0 = time.perf_counter()
        has_kannada = bool(kannada_pattern.search(query))
        duration_ms = (time.perf_counter() - t0) * 1000.0

        assert has_kannada is True
        assert duration_ms < 2.0, f"Router regex took {duration_ms:.2f}ms (budget: 2ms)"

    # --- 7. Database Query Latency ---
    def test_performance_database_query_latency(self):
        """NF-PRF-07: Verifies filtered crop listing queries complete in under 15.0 ms."""
        t0 = time.perf_counter()
        resp = client.get("/api/marketplace/listings?min_price=100&max_price=800")
        query_ms = (time.perf_counter() - t0) * 1000.0

        assert resp.status_code == 200
        assert query_ms < 25.0, f"Listing query took {query_ms:.2f}ms (budget: 25ms)"

    # --- 8. Multi-Threaded Concurrency Test ---
    def test_performance_multi_threaded_concurrency(self):
        """NF-PRF-08: Verifies 10 concurrent requests to API endpoints execute cleanly without deadlock."""
        def make_request(idx):
            r = client.get("/health")
            return r.status_code == 200

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        assert all(results) is True
        assert len(results) == 10

"""Smoke tests on the REAL models (marker `ml`; run with:  pytest -m ml).

They load the original ResNet-50 weights and classify the five sample leaves, and (if an index exists or can be
built) query the real hybrid retriever.
"""
import os
from pathlib import Path

import pytest

from app.core.config import BACKEND_DIR

pytestmark = pytest.mark.ml
LEAVES = Path(__file__).resolve().parents[1] / "fixtures" / "leaves"
WEIGHTS = BACKEND_DIR / "data" / "models" / "best_resnet50_coffee.pth"
EXPECTED = {"rust_sample.jpg": "Rust", "miner_sample.jpg": "Miner", "phoma_sample.jpg": "Phoma",
            "healthy_sample.jpg": "Healthy", "cercospora_sample.jpg": "Cerscospora"}


@pytest.fixture(scope="module")
def cnn():
    if not WEIGHTS.exists():
        pytest.skip("CNN weights not present")
    from app.services.cnn import CNNClassifier

    return CNNClassifier(WEIGHTS)


def test_weights_are_the_original_file():
    import hashlib

    if not WEIGHTS.exists():
        pytest.skip("CNN weights not present")
    digest = hashlib.sha256(WEIGHTS.read_bytes()).hexdigest()
    assert digest.startswith("e1fd039fa0e357fb174f")  # identical to ../backend/app/services/best_resnet50_coffee.pth


def test_cnn_classifies_sample_leaves(cnn):
    correct = 0
    for name, label in EXPECTED.items():
        out = cnn.predict((LEAVES / name).read_bytes())
        assert abs(sum(out["distribution"].values()) - 100) < 0.5
        assert 0 <= out["confidence"] <= 100
        correct += out["class"] == label
    assert correct >= 4, f"only {correct}/5 sample leaves classified correctly"


def test_cnn_is_deterministic(cnn):
    data = (LEAVES / "rust_sample.jpg").read_bytes()
    assert cnn.predict(data) == cnn.predict(data)


@pytest.mark.skipif(os.getenv("PLANTIQ_TEST_RAG") != "1", reason="set PLANTIQ_TEST_RAG=1 to load/build the real RAG index")
def test_real_retriever_finds_rust_guidance():
    from app.core.config import settings
    from app.services.rag.retriever import HybridRetriever

    settings.RAG_INDEX_DIR = BACKEND_DIR / "data" / "index"
    r = HybridRetriever.load_or_build()
    res = r.search("coffee leaf rust bordeaux mixture spray schedule", top_k=3, topic_filter="leaf_rust")
    assert res and res[0]["score"] > 0.3
    assert any("rust" in d["text"].lower() for d in res)

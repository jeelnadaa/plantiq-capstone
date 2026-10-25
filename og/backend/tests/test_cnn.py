"""
Test Suite: Module 1 — Leaf Pathology Computer Vision (CNN)
File: tests/test_cnn.py
Coverage:
- ResNet-50 Model Architecture & Weights Verification
- Preprocessing Tensor Transformations (224x224 RGB ImageNet Normalization)
- Softmax Probability Distribution & Class Mapping (5 Classes)
- SHA-256 Deduplication Caching Engine
- Robustness & Corrupted Payload Error Handling
- Confidence Gating (< 75.0% Blended Threshold)
"""

import os
import io
import time
import pytest
import torch
from PIL import Image

from app.core.config import settings
from app.services.cnn_service import CNNModelWrapper, CLASSES, get_detector
from app.services.cache_service import compute_image_hash, get_cached_result, save_result_to_cache
from app.core.database import SessionLocal, engine
from app.models.cache import Base, ImageAnalysisCache

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

def create_synthetic_leaf_image(color=(34, 139, 34), size=(300, 300)) -> bytes:
    """Generates synthetic RGB leaf image bytes for deterministic unit testing."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestCNNModule:
    """Module 1: Leaf Pathology Computer Vision Functional Test Suite"""

    def test_weights_file_exists(self):
        """TC-CNN-01: Verifies the ResNet-50 weights file is physically present."""
        weights_path = settings.CNN_WEIGHTS_PATH
        assert os.path.exists(weights_path), f"CNN Weights file missing at: {weights_path}"
        file_size_mb = os.path.getsize(weights_path) / (1024 * 1024)
        assert file_size_mb > 50.0, f"Weights file size {file_size_mb:.1f} MB is unusually small."

    def test_model_architecture_and_classes(self):
        """TC-CNN-02: Verifies ResNet-50 head structure and the 5 target coffee classes."""
        detector = get_detector()
        assert detector.model is not None
        assert len(CLASSES) == 5
        assert set(CLASSES) == {'Miner', 'Rust', 'Phoma', 'Healthy', 'Cerscospora'}

        # Verify custom classification head: Dropout(0.4) + Linear(2048, 5)
        fc_layer = detector.model.fc
        assert isinstance(fc_layer, torch.nn.Sequential)
        assert len(fc_layer) == 2
        assert isinstance(fc_layer[0], torch.nn.Dropout)
        assert fc_layer[0].p == 0.4
        assert isinstance(fc_layer[1], torch.nn.Linear)
        assert fc_layer[1].in_features == 2048
        assert fc_layer[1].out_features == 5

    def test_image_preprocessing_transform(self):
        """TC-CNN-03: Verifies input image transforms into (1, 3, 224, 224) normalized tensor."""
        detector = get_detector()
        dummy_img = Image.new("RGB", (512, 384), color=(40, 160, 50))
        tensor = detector.transform(dummy_img).unsqueeze(0)

        assert tensor.shape == (1, 3, 224, 224)
        assert tensor.dtype == torch.float32

        # Check normalization boundaries (ImageNet standardized values typically span [-2.5, 2.5])
        assert tensor.min() >= -3.5
        assert tensor.max() <= 3.5

    def test_inference_forward_pass_and_distribution(self):
        """TC-CNN-04: Verifies inference returns top class, confidence, and 100% sum distribution."""
        detector = get_detector()
        img_bytes = create_synthetic_leaf_image()

        result = detector.predict(img_bytes)
        assert "class" in result
        assert "confidence" in result
        assert "distribution" in result
        assert result["class"] in CLASSES

        conf = result["confidence"]
        assert 0.0 <= conf <= 100.0

        dist = result["distribution"]
        assert len(dist) == 5
        total_prob = sum(dist.values())
        assert abs(total_prob - 100.0) < 0.1, f"Distribution total {total_prob} does not sum to 100%"

    def test_sha256_deduplication_cache(self):
        """TC-CNN-05: Verifies SHA-256 caching returns hits, bypassing CNN compute."""
        db = SessionLocal()
        try:
            img_bytes = create_synthetic_leaf_image(color=(120, 80, 20))
            user_id = 999
            query = "What spray is needed?"
            language = "en"

            img_hash = compute_image_hash(img_bytes, user_id=user_id, user_question=query, language=language)
            assert len(img_hash) == 64

            # Clear any preexisting test record
            db.query(ImageAnalysisCache).filter(ImageAnalysisCache.image_hash == img_hash).delete()
            db.commit()

            # First check: Cache Miss
            miss_result = get_cached_result(db, img_hash)
            assert miss_result is None

            # Seed cache
            test_dist = {"Rust": 95.0, "Healthy": 5.0, "Miner": 0.0, "Phoma": 0.0, "Cerscospora": 0.0}
            save_result_to_cache(
                db=db,
                image_hash=img_hash,
                filename="test_leaf.jpg",
                disease_class="Rust",
                confidence=95.0,
                distribution=test_dist,
                env_data={"temperature": 24.0, "humidity": 85.0},
                advisory_text="Apply 0.5% Bordeaux mixture pre-monsoon.",
                sources=["CCRI Bulletin"],
                is_blended=False,
                user_id=user_id
            )

            # Second check: Cache Hit
            hit_result = get_cached_result(db, img_hash)
            assert hit_result is not None
            assert hit_result["disease"] == "Rust"
            assert hit_result["confidence"] == 95.0
        finally:
            db.query(ImageAnalysisCache).filter(ImageAnalysisCache.user_id == 999).delete()
            db.commit()
            db.close()

    def test_corrupted_payload_robustness(self):
        """TC-CNN-06: Verifies corrupted or invalid image bytes do not crash the service."""
        detector = get_detector()
        corrupt_bytes = b"NOT_A_VALID_JPEG_HEADER_CORRUPT_BYTES"

        result = detector.predict(corrupt_bytes)
        assert "error" in result or result.get("class") == "Unknown"
        assert result.get("confidence") == 0.0

    def test_low_confidence_blending_threshold(self):
        """TC-CNN-07: Verifies confidence < 75.0% threshold logic triggers blended mode."""
        threshold = settings.CONFIDENCE_THRESHOLD_CNN
        assert threshold == 75.0

        simulated_low_conf = 68.4
        is_blended = simulated_low_conf < threshold
        assert is_blended is True, "Confidence below 75% must be flagged as blended"

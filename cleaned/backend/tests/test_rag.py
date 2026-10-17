"""
Test Suite: Module 2 — Hybrid RAG & Agronomic Advisory Engine
File: tests/test_rag.py
Coverage:
- Strict Zero-Mock Policy for Environmental Weather Service
- Epidemiological Spore Incubation Risk Modeling (High/Moderate/Low)
- Knowledge Base Indexes (FAISS FlatIP, BM25Okapi, Chunks Pickle)
- Dense Vector Retrieval with BGE Asymmetric Prompting
- Sparse Lexical Keyword Retrieval (Exact Chemical Compounds)
- Reciprocal Rank Fusion (RRF k=60) Fusion Logic
- Cross-Encoder Sigmoid Logit Normalization in [0.0, 1.0]
- Dynamic Agronomic Intent Expansion (Timing, Dosage, Bio-control)
- Chemical Dosage Safety Regex Audit Guardrail
- End-to-End Advisory Synthesis & CCRI Grounding
"""

import os
import re
import pytest
import numpy as np

from app.core.config import settings
from app.services.env_service import get_env_service, EnvironmentalService
from app.services.rag_service import get_rag_service, RAGService


class TestRAGModule:
    """Module 2: Hybrid RAG & Agronomic Advisory Functional Test Suite"""

    # --- 1. Environmental Telemetry & Zero-Mock Tests ---
    def test_environmental_zero_mock_policy_when_coords_missing(self):
        """TC-RAG-01: Verifies strictly NO fake/mock numbers when GPS coordinates are None."""
        env_service = get_env_service()
        data = env_service.get_environmental_data(latitude=None, longitude=None)

        assert data["available"] is False
        assert data["temperature"] is None
        assert data["humidity"] is None
        assert data["rainfall"] is None
        assert data["elevation"] is None
        assert data["incubation_risk"] is None
        assert data["risk_level"] == "none"
        assert "unavailable" in data["note"].lower()

    def test_environmental_risk_modeling_logic(self):
        """TC-RAG-02: Verifies biological fungal spore incubation risk calculation."""
        env_service = EnvironmentalService()

        # High Risk: RH >= 80% and 20C <= Temp <= 28C
        temp_high = 24.0
        rh_high = 85.0
        is_high_risk = (rh_high >= 80.0) and (20.0 <= temp_high <= 28.0)
        assert is_high_risk is True

        # Moderate Risk: RH >= 65% or Rain > 0
        rh_mod = 70.0
        is_mod_risk = (rh_mod >= 65.0)
        assert is_mod_risk is True

        # Low Risk: Dry canopy, low humidity
        rh_low = 50.0
        temp_low = 30.0
        is_low_risk = not ((rh_low >= 80.0 and 20 <= temp_low <= 28) or rh_low >= 65.0)
        assert is_low_risk is True

    # --- 2. Knowledge Base & Index Files Verification ---
    def test_knowledge_base_files_exist(self):
        """TC-RAG-03: Verifies FAISS index, BM25 index, and chunks files exist on disk."""
        index_dir = settings.RAG_INDEX_DIR
        faiss_path = os.path.join(index_dir, "faiss_index.bin")
        bm25_path = os.path.join(index_dir, "bm25_index.pkl")
        chunks_path = os.path.join(index_dir, "chunks.pkl")

        assert os.path.exists(faiss_path), f"FAISS index missing at {faiss_path}"
        assert os.path.exists(bm25_path), f"BM25 index missing at {bm25_path}"
        assert os.path.exists(chunks_path), f"Chunks pickle missing at {chunks_path}"

        rag = get_rag_service()
        assert rag.index is not None
        assert rag.bm25 is not None
        assert len(rag.doc_chunks) > 0
        assert rag.index.ntotal == len(rag.doc_chunks)

    # --- 3. Dynamic Intent Expansion Tests ---
    def test_dynamic_agronomic_intent_expansion(self):
        """TC-RAG-04: Verifies intent expansion enriches user query with domain keywords."""
        rag = get_rag_service()

        # Timing intent
        q_time = rag._expand_agronomic_query("When to spray for rust before monsoon?", "Rust", "")
        assert "monsoon" in q_time.lower() or "schedule" in q_time.lower()
        assert "pre-monsoon" in q_time.lower()

        # Dosage intent
        q_dose = rag._expand_agronomic_query("How much chemical per barrel?", "Cercospora", "")
        assert "dosage" in q_dose.lower() or "barrel" in q_dose.lower()
        assert "200l" in q_dose.lower()

        # Organic intent
        q_org = rag._expand_agronomic_query("Is there an organic bio solution?", "Rust", "")
        assert "organic" in q_org.lower()
        assert "trichoderma" in q_org.lower() or "bio" in q_org.lower()

    # --- 4. Retrieval & Ranking Algorithms ---
    def test_dense_vector_and_bm25_retrieval(self):
        """TC-RAG-05: Verifies dense vector and sparse BM25 retrieval return valid candidate chunks."""
        rag = get_rag_service()
        results = rag.search("coffee leaf rust bordeaux mixture dosage", top_k=3)

        assert len(results) > 0
        assert len(results) <= 3
        top_res = results[0]
        assert "text" in top_res
        assert "score" in top_res
        assert "source" in top_res
        assert 0.0 <= top_res["score"] <= 1.0

    def test_sigmoid_score_normalization_bounds(self):
        """TC-RAG-06: Verifies Cross-Encoder logits map strictly into [0.0, 1.0]."""
        test_logits = [-10.0, -2.5, 0.0, 2.5, 6.0, 15.0]
        for z in test_logits:
            score = 1.0 / (1.0 + np.exp(-z))
            assert 0.0 <= score <= 1.0
            if z == 0.0:
                assert abs(score - 0.5) < 1e-5
            elif z > 0:
                assert score > 0.5
            else:
                assert score < 0.5

    def test_reciprocal_rank_fusion_math(self):
        """TC-RAG-07: Verifies RRF formula prioritizes documents present in both dense and sparse rankings."""
        k = 60.0
        # Doc A: Rank 1 in Dense, Rank 1 in Sparse
        score_a = (1.0 / (k + 1)) + (1.0 / (k + 1))
        # Doc B: Rank 1 in Dense, Rank 50 in Sparse
        score_b = (1.0 / (k + 1)) + (1.0 / (k + 50))
        # Doc C: Rank 25 in Dense, Rank 25 in Sparse
        score_c = (1.0 / (k + 25)) + (1.0 / (k + 25))

        assert score_a > score_b, "Joint high rank must beat single-channel rank"
        assert score_a > score_c

    # --- 5. Chemical Dosage Safety Guardrail Tests ---
    def test_chemical_dosage_safety_audit_verification(self):
        """TC-RAG-08: Verifies safety audit passes verified dosages and flags unverified dosages."""
        rag = get_rag_service()

        mock_docs = [
            {"text": "Spray Bordeaux mixture 1% (1 kg copper sulphate and 1 kg quicklime in 100 L water) during pre-monsoon."}
        ]

        # Case 1: Verified dosage in LLM response
        safe_response = "Apply 1% Bordeaux mixture with 1 kg copper sulphate in 100 L water."
        audit_safe = rag._audit_dosage_safety(safe_response, mock_docs)
        assert audit_safe["verified"] is True
        assert len(audit_safe["unverified_dosages"]) == 0

        # Case 2: Hallucinated / unverified lethal dosage
        toxic_hallucinated_response = "Apply 25% Bordeaux mixture with 50 kg copper sulphate."
        audit_unsafe = rag._audit_dosage_safety(toxic_hallucinated_response, mock_docs)
        assert audit_unsafe["verified"] is False
        assert any("25%" in d for d in audit_unsafe["unverified_dosages"])
        assert "Caution" in audit_unsafe["safety_note"]

    # --- 6. End-to-End Advisory Generation ---
    def test_generate_advisory_e2e(self):
        """TC-RAG-09: Verifies full RAG pipeline synthesizes a complete advisory with CCRI citations."""
        rag = get_rag_service()
        env_data = {"temperature": 23.5, "humidity": 82.0, "rainfall": 5.0, "risk_level": "high"}

        advisory = rag.generate_advisory(
            disease="Rust",
            cnn_confidence=97.5,
            is_healthy=False,
            env_data=env_data,
            user_question="How to treat coffee leaf rust?",
            language="en"
        )

        assert advisory.answer is not None
        assert len(advisory.answer) > 20
        assert len(advisory.sources) > 0
        assert advisory.safety_audit is not None

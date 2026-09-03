"""
rag_service.py
==============
PlantIQ Cleaned Production Hybrid RAG Service.
Features:
- Dense Vector Retrieval: BAAI/bge-base-en-v1.5 (768-dim normalized embeddings) via FAISS FlatIP.
- Sparse Lexical Retrieval: BM25Okapi for exact chemical, dosage, and pathogen terminology.
- Deep Cross-Encoder Reranking: ms-marco-MiniLM-L-6-v2 for joint query-document relevance.
- Sigmoid Score Normalization: Maps logits to [0.0, 1.0] for stable confidence thresholding.
- Semantic Section Chunking & Topic Filtering: Contextual agronomic boundaries.
"""

import os
import re
import pickle
import numpy as np
import torch
import faiss
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.core.config import settings
from app.services.router_service import analyze_and_route_query

# Optimize PyTorch CPU multi-threading
torch.set_num_threads(max(1, min(8, os.cpu_count() or 4)))

class AdvisoryResult(BaseModel):
    answer: str
    sources: List[str]
    is_blended: bool
    reasons: List[str]

class RAGService:
    def __init__(self):
        self.embedding_model_name = "BAAI/bge-base-en-v1.5"
        self.reranker_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self.index_dir = settings.RAG_INDEX_DIR
        
        self.embedding_model = None
        self.reranker = None
        self.index = None
        self.bm25 = None
        self.doc_chunks = []
        
        self._load_models()
        self._load_index()

    def _load_models(self):
        try:
            print(f"[Cleaned RAG] Loading Dense Embedding model: {self.embedding_model_name}...")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            print(f"[Cleaned RAG] Loading Cross-Encoder Reranker: {self.reranker_model_name}...")
            self.reranker = CrossEncoder(self.reranker_model_name)
            print("[Cleaned RAG] AI Models initialized successfully.")
        except Exception as e:
            print(f"[Cleaned RAG] Warning during model initialization: {e}")

    def _load_index(self):
        index_file = os.path.join(self.index_dir, "faiss_index.bin")
        chunks_file = os.path.join(self.index_dir, "chunks.pkl")
        bm25_file = os.path.join(self.index_dir, "bm25_index.pkl")

        if os.path.exists(index_file) and os.path.exists(chunks_file):
            try:
                self.index = faiss.read_index(index_file)
                with open(chunks_file, "rb") as f:
                    self.doc_chunks = pickle.load(f)
                print(f"[Cleaned RAG] Loaded FAISS index ({self.index.ntotal} vectors, {len(self.doc_chunks)} chunks).")
            except Exception as e:
                print(f"[Cleaned RAG] Error loading FAISS index/chunks: {e}")

        if os.path.exists(bm25_file):
            try:
                with open(bm25_file, "rb") as f:
                    data = pickle.load(f)
                    self.bm25 = data["bm25"]
                print("[Cleaned RAG] Loaded BM25 Lexical Index.")
            except Exception as e:
                print(f"[Cleaned RAG] Error loading BM25 index: {e}")

        if not self.index or len(self.doc_chunks) == 0 or not self.bm25:
            print(f"[Cleaned RAG] Index files missing or incomplete in {self.index_dir}. Auto-rebuilding from knowledge_base PDFs...")
            try:
                from app.services.build_index import build_knowledge_index
                build_knowledge_index()
                # Reload after rebuild
                if os.path.exists(index_file) and os.path.exists(chunks_file):
                    self.index = faiss.read_index(index_file)
                    with open(chunks_file, "rb") as f:
                        self.doc_chunks = pickle.load(f)
                if os.path.exists(bm25_file):
                    with open(bm25_file, "rb") as f:
                        data = pickle.load(f)
                        self.bm25 = data["bm25"]
                print(f"[Cleaned RAG] Auto-rebuild complete! Loaded {len(self.doc_chunks)} chunks.")
            except Exception as e:
                print(f"[Cleaned RAG] Auto-rebuild failed: {e}")

    def search(
        self, 
        query: str, 
        top_k: int = 3, 
        topic_filter: Optional[str] = None,
        candidate_pool_size: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Executes 3-Stage Hybrid Retrieval:
        1. Dense Vector Search (BGE) -> Top Candidate IDs
        2. Sparse Lexical Search (BM25) -> Top Candidate IDs
        3. Cross-Encoder Joint Reranker -> Top-K Results with Sigmoid Normalization
        """
        if not query or not query.strip() or len(self.doc_chunks) == 0:
            return []

        clean_q = query.strip()
        k_candidates = min(candidate_pool_size, len(self.doc_chunks))
        candidate_indices = set()
        dense_scores_map = {}
        sparse_scores_map = {}

        # ── Stage 1: Dense Vector Retrieval ───────────────────────────
        if self.index and self.embedding_model:
            try:
                q_emb = self.embedding_model.encode(
                    [clean_q], 
                    normalize_embeddings=True, 
                    convert_to_numpy=True
                ).astype(np.float32)
                d_scores, d_indices = self.index.search(q_emb, k_candidates)
                for score, idx in zip(d_scores[0], d_indices[0]):
                    if idx != -1 and idx < len(self.doc_chunks):
                        candidate_indices.add(idx)
                        dense_scores_map[idx] = float(score)
            except Exception as e:
                print(f"[Cleaned RAG] Dense search error: {e}")

        # ── Stage 2: Sparse BM25 Lexical Retrieval ─────────────────────
        if self.bm25:
            try:
                q_tokens = [w.lower() for w in re.findall(r'\b\w+\b', clean_q) if len(w) > 1]
                if q_tokens:
                    bm25_scores = self.bm25.get_scores(q_tokens)
                    top_sparse_idx = np.argsort(bm25_scores)[::-1][:k_candidates]
                    max_sparse = float(np.max(bm25_scores)) if len(bm25_scores) > 0 and np.max(bm25_scores) > 0 else 1.0
                    for idx in top_sparse_idx:
                        if bm25_scores[idx] > 0 and idx < len(self.doc_chunks):
                            candidate_indices.add(int(idx))
                            sparse_scores_map[int(idx)] = float(bm25_scores[idx]) / max_sparse
            except Exception as e:
                print(f"[Cleaned RAG] Sparse search error: {e}")

        if not candidate_indices:
            # Fallback if both dense/sparse produced no matches
            candidate_indices = set(range(min(top_k, len(self.doc_chunks))))

        # Apply topic filter if specified
        valid_candidates = []
        for idx in candidate_indices:
            chunk = self.doc_chunks[idx]
            if topic_filter and chunk.get("topic") and chunk.get("topic") != topic_filter:
                continue
            valid_candidates.append((idx, chunk))

        if not valid_candidates:
            # Relax filter if too restrictive
            valid_candidates = [(idx, self.doc_chunks[idx]) for idx in candidate_indices]

        # ── Stage 3: Cross-Encoder Deep Reranking ──────────────────────
        scored_results = []
        if self.reranker and len(valid_candidates) > 0:
            try:
                pairs = [[clean_q, chunk["text"]] for _, chunk in valid_candidates]
                raw_logits = self.reranker.predict(pairs)
                if np.isscalar(raw_logits):
                    raw_logits = [raw_logits]

                for (idx, chunk), logit in zip(valid_candidates, raw_logits):
                    # Sigmoid Logistic Normalization: sigma(z) = 1 / (1 + exp(-z))
                    norm_score = float(1.0 / (1.0 + np.exp(-float(logit))))
                    norm_score = max(0.0, min(1.0, norm_score))
                    scored_results.append({
                        "text": chunk.get("text", ""),
                        "source": chunk.get("source", "CCRI Coffee Agronomy Manual"),
                        "score": round(norm_score, 4),
                        "metadata": {
                            "page": chunk.get("page", 1),
                            "section": chunk.get("section", ""),
                            "topic": chunk.get("topic", "")
                        }
                    })
            except Exception as e:
                print(f"[Cleaned RAG] Reranker error: {e}. Falling back to hybrid score.")

        if not scored_results:
            # Fallback scoring: Reciprocal Rank Fusion / Weighted average
            for idx, chunk in valid_candidates:
                d_s = dense_scores_map.get(idx, 0.5)
                s_s = sparse_scores_map.get(idx, 0.0)
                hybrid_score = 0.65 * d_s + 0.35 * s_s
                scored_results.append({
                    "text": chunk.get("text", ""),
                    "source": chunk.get("source", "CCRI Coffee Agronomy Manual"),
                    "score": round(float(hybrid_score), 4),
                    "metadata": {
                        "page": chunk.get("page", 1),
                        "section": chunk.get("section", ""),
                        "topic": chunk.get("topic", "")
                    }
                })

        # Sort by score descending and return Top-K
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results[:top_k]

    def generate_advisory(
        self,
        disease: str,
        cnn_confidence: float,
        is_healthy: bool,
        env_data: Optional[Dict[str, Any]] = None,
        user_question: Optional[str] = None,
        language: str = "en"
    ) -> AdvisoryResult:
        route_meta = {}
        search_kw = f"coffee {disease} control management treatment dosage fungicide"
        target_lang = language
        if user_question:
            route_meta = analyze_and_route_query(user_question)
            if route_meta.get("search_query_english"):
                search_kw = f"coffee {disease} " + route_meta["search_query_english"]
            if route_meta.get("target_response_language"):
                target_lang = route_meta["target_response_language"]

        # Topic filtering heuristic
        topic_filter = None
        d_lower = disease.lower()
        if "rust" in d_lower:
            topic_filter = "leaf_rust"
        elif "cercospora" in d_lower:
            topic_filter = "cercospora_leaf_spot"
        elif "miner" in d_lower:
            topic_filter = "leaf_miner"
        elif "phoma" in d_lower:
            topic_filter = "phoma_blight"

        retrieved_docs = self.search(search_kw, top_k=3, topic_filter=topic_filter)
        max_rag_score = max([d["score"] for d in retrieved_docs]) if retrieved_docs else 0.0

        is_blended = (cnn_confidence < settings.CONFIDENCE_THRESHOLD_CNN) or (max_rag_score < settings.CONFIDENCE_THRESHOLD_RAG)
        reasons = []
        if cnn_confidence < settings.CONFIDENCE_THRESHOLD_CNN:
            reasons.append(f"CNN confidence ({cnn_confidence:.1f}%) is below threshold ({settings.CONFIDENCE_THRESHOLD_CNN:.0f}%).")
        if max_rag_score < settings.CONFIDENCE_THRESHOLD_RAG:
            reasons.append(f"Hybrid Reranker relevance ({max_rag_score:.2f}) is below threshold ({settings.CONFIDENCE_THRESHOLD_RAG:.2f}).")

        lang_rule = (
            "OUTPUT STRICTLY IN KANNADA SCRIPT (ಕನ್ನಡ ಲಿಪಿ). Use clear, respectful agricultural Kannada."
            if target_lang == "kn" or route_meta.get("detected_script") in ["kannada_script", "kanglish"]
            else "OUTPUT IN CLEAR, CONCISE ENGLISH."
        )

        env_block = ""
        if env_data and env_data.get("location_status") != "Disallowed / Unavailable":
            env_lines = [f"- {k}: {v}" for k, v in env_data.items()]
            env_block = "\nLocation Factors:\n" + "\n".join(env_lines)

        doc_lines = [f"[{i+1}] {d['text']}" for i, d in enumerate(retrieved_docs)]
        docs_block = "\n".join(doc_lines) if doc_lines else "General South Indian coffee extension protocols apply."

        prompt = f"""You are PlantIQ, an expert coffee agronomist specialized in South Indian Arabica & Robusta plantations.
Generate an actionable, scientifically accurate disease advisory.

[DIAGNOSTIC STATUS]
- Disease: {disease} (Confidence: {cnn_confidence:.1f}%)
{env_block}
- Specific Farmer Question: {user_question or 'Standard management guide requested.'}

[RETRIEVED KNOWLEDGE BASE EXTRACTS]
{docs_block}

[CRITICAL INSTRUCTIONS]
1. {lang_rule}
2. Be direct, authoritative, and structured with bullet points for immediate field actions (chemical/organic dosage, timing, cultural shade management).
3. Ground recommendations in the provided microclimate parameters (humidity, temperature, rainfall, soil pH).
"""

        answer = self._call_llm(prompt)
        sources = [d["source"] for d in retrieved_docs] if retrieved_docs else ["CCRI Agronomy Extension Guide"]

        return AdvisoryResult(
            answer=answer,
            sources=sources,
            is_blended=is_blended,
            reasons=reasons
        )

    def _call_llm(self, prompt: str) -> str:
        if settings.GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GEMINI_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')
                resp = model.generate_content(prompt, generation_config={"temperature": 0.2})
                return resp.text.strip()
            except Exception as e:
                print(f"[Cleaned RAG] Gemini error: {e}. Falling back to Groq...")

        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                g_client = Groq(api_key=settings.GROQ_API_KEY)
                comp = g_client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    max_tokens=600
                )
                return comp.choices[0].message.content.strip()
            except Exception as e:
                print(f"[Cleaned RAG] Groq error: {e}")

        return "Standard Central Coffee Research Institute (CCRI) guidelines applied."

_rag_instance = None

def get_rag_service() -> RAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance

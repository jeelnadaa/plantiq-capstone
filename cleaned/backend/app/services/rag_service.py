import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from app.core.config import settings
from app.services.router_service import analyze_and_route_query

class AdvisoryResult(BaseModel):
    answer: str
    sources: List[str]
    is_blended: bool
    reasons: List[str]

class RAGService:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index_dir = settings.RAG_INDEX_DIR
        self.index = None
        self.doc_chunks = []
        self._load_index()

    def _load_index(self):
        index_file = os.path.join(self.index_dir, 'faiss_index.bin')
        chunks_file = os.path.join(self.index_dir, 'chunks.npy')
        if os.path.exists(index_file) and os.path.exists(chunks_file):
            try:
                self.index = faiss.read_index(index_file)
                self.doc_chunks = np.load(chunks_file, allow_pickle=True).tolist()
                print(f"[Cleaned RAG] Loaded FAISS index ({len(self.doc_chunks)} chunks).")
            except Exception as e:
                print(f"[Cleaned RAG] Failed to load FAISS index: {e}")
        else:
            print(f"[Cleaned RAG] FAISS index files not found in {self.index_dir}.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not self.index or len(self.doc_chunks) == 0 or not query.strip():
            return []
        try:
            emb = self.embedding_model.encode([query])
            faiss.normalize_L2(emb)
            scores, indices = self.index.search(emb, top_k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and idx < len(self.doc_chunks):
                    item = self.doc_chunks[idx]
                    results.append({
                        "text": item.get("text", ""),
                        "source": item.get("source", "CCRI Coffee Manual"),
                        "score": float(score)
                    })
            return results
        except Exception as e:
            print(f"[Cleaned RAG] Search warning: {e}")
            return []

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
        search_kw = f"coffee {disease} control management treatment dosage"
        target_lang = language
        if user_question:
            route_meta = analyze_and_route_query(user_question)
            if route_meta.get("search_query_english"):
                search_kw = f"coffee {disease} " + route_meta["search_query_english"]
            if route_meta.get("target_response_language"):
                target_lang = route_meta["target_response_language"]

        retrieved_docs = self.search(search_kw, top_k=3)
        max_rag_score = max([d["score"] for d in retrieved_docs]) if retrieved_docs else 0.0

        is_blended = (cnn_confidence < settings.CONFIDENCE_THRESHOLD_CNN) or (max_rag_score < settings.CONFIDENCE_THRESHOLD_RAG)
        reasons = []
        if cnn_confidence < settings.CONFIDENCE_THRESHOLD_CNN:
            reasons.append(f"CNN confidence ({cnn_confidence:.1f}%) is below {settings.CONFIDENCE_THRESHOLD_CNN:.0f}%.")
        if max_rag_score < settings.CONFIDENCE_THRESHOLD_RAG:
            reasons.append(f"Vector similarity ({max_rag_score:.2f}) is below {settings.CONFIDENCE_THRESHOLD_RAG:.2f}.")

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
                    model='llama-3.3-70b-versatile',
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


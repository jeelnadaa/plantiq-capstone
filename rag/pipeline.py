"""
pipeline.py
===========
All RAG logic in one place:
  - Config  (reads .env)
  - PDF ingestion + chunking
  - FAISS vector store  (auto save / load)
  - Gemini LLM wrapper
  - Two RAG modes:
      1. disease_advisory(DiseaseInput)  →  CNN + env data → structured advisory
      2. answer_question(str)            →  plain user question → synthesised answer
"""

from __future__ import annotations

import os
import re
import pickle
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── third-party (installed via requirements.txt) ─────────────────────────────
import numpy as np
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from groq import Groq

try:
    import fitz          # PyMuPDF  (preferred)
    _PDF_BACKEND = "pymupdf"
except ImportError:
    import pdfplumber    # fallback
    _PDF_BACKEND = "pdfplumber"

log = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════════════╗
# ║  CONFIG                                              ║
# ╚══════════════════════════════════════════════════════╝

load_dotenv()

def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

GEMINI_API_KEY = _env("GEMINI_API_KEY")
GEMINI_MODEL   = _env("GEMINI_MODEL",   "gemini-1.5-flash")
GROQ_API_KEY   = _env("GROQ_API_KEY")
GROQ_MODEL     = _env("GROQ_MODEL",     "llama-3.3-70b-versatile")
PDF_FOLDER     = _env("PDF_FOLDER",     "./knowledge_base")
INDEX_FOLDER   = _env("INDEX_FOLDER",   "./index")
TOP_K          = int(_env("TOP_K",      "5"))


def _validate_config(provider: str = "gemini"):
    if provider == "gemini" and (not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here"):
        raise ValueError("GEMINI_API_KEY is not set in your .env file.")
    if provider == "groq" and (not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here"):
        raise ValueError("GROQ_API_KEY is not set in your .env file.")


# ╔══════════════════════════════════════════════════════╗
# ║  DATA CLASSES                                        ║
# ╚══════════════════════════════════════════════════════╝

@dataclass
class Chunk:
    text: str
    source: str
    page: int


@dataclass
class DiseaseInput:
    """Everything the CNN + sensors provide for Mode 1."""
    disease: str
    confidence: float       # 0.0 – 1.0
    is_healthy: bool
    env_data: dict[str, any] = field(default_factory=dict)
    user_question: Optional[str] = None


@dataclass
class Result:
    answer: str
    confidence: float = 0.0
    sources: list[str] = field(default_factory=list)


# ╔══════════════════════════════════════════════════════╗
# ║  PDF INGESTION                                       ║
# ╚══════════════════════════════════════════════════════╝

def load_pdfs(folder: str) -> list[Chunk]:
    """
    Load every PDF in *folder* and return text chunks.
    Returns [] if the folder is missing or empty — caller handles the warning.
    """
    pdf_dir = Path(folder)
    if not pdf_dir.exists():
        return []

    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    if not pdf_files:
        return []

    chunks: list[Chunk] = []
    for path in pdf_files:
        log.info("Reading %s …", path.name)
        for page_num, text in _extract_pages(str(path)):
            chunks.extend(_split(text, path.name, page_num))

    log.info("Loaded %d chunks from %d PDFs.", len(chunks), len(pdf_files))
    return chunks


def _extract_pages(path: str) -> list[tuple[int, str]]:
    if _PDF_BACKEND == "pymupdf":
        doc = fitz.open(path)
        pages = [(i + 1, _clean(p.get_text("text"))) for i, p in enumerate(doc)]
        doc.close()
    else:
        with pdfplumber.open(path) as pdf:
            pages = [(i + 1, _clean(p.extract_text() or "")) for i, p in enumerate(pdf.pages)]
    return [(n, t) for n, t in pages if t.strip()]


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E]", " ", text)
    return text.strip()


def _split(text: str, source: str, page: int,
           size: int = 400, overlap: int = 50) -> list[Chunk]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(Chunk(" ".join(words[start:end]), source, page))
        if end == len(words):
            break
        start += size - overlap
    return chunks


# ╔══════════════════════════════════════════════════════╗
# ║  VECTOR STORE  (FAISS)                               ║
# ╚══════════════════════════════════════════════════════╝

_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_DIM = 384
_IDX_FILE   = "faiss.index"
_CHUNK_FILE = "chunks.pkl"

class VectorStore:
    def __init__(self):
        log.info("Loading embedding model …")
        self._embedder = SentenceTransformer(_EMBED_MODEL)
        self._index = faiss.IndexFlatIP(_DIM)
        self._chunks: list[Chunk] = []

    # ── build ──────────────────────────────────────────

    def add(self, chunks: list[Chunk], batch: int = 64):
        texts = [c.text for c in chunks]
        all_embs = []
        for i in range(0, len(texts), batch):
            all_embs.append(
                self._embedder.encode(
                    texts[i:i+batch], convert_to_numpy=True,
                    normalize_embeddings=True, show_progress_bar=False,
                )
            )
        self._index.add(np.vstack(all_embs).astype("float32"))
        self._chunks.extend(chunks)
        log.info("Index now has %d vectors.", self._index.ntotal)

    # ── search ─────────────────────────────────────────

    def search(self, query: str, top_k: int = TOP_K) -> tuple[list[Chunk], list[float]]:
        if self._index.ntotal == 0:
            return [], []
        q = self._embedder.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        ).astype("float32")
        scores, ids = self._index.search(q, top_k)
        
        found_chunks = [self._chunks[i] for i in ids[0] if i != -1]
        found_scores = [float(s) for i, s in zip(ids[0], scores[0]) if i != -1]
        return found_chunks, found_scores

    # ── persist ────────────────────────────────────────

    def save(self, folder: str):
        Path(folder).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self._index, str(Path(folder) / _IDX_FILE))
        with open(Path(folder) / _CHUNK_FILE, "wb") as f:
            pickle.dump(self._chunks, f)
        log.info("Index saved → '%s'.", folder)

    def load(self, folder: str) -> bool:
        idx = Path(folder) / _IDX_FILE
        chk = Path(folder) / _CHUNK_FILE
        if not idx.exists() or not chk.exists():
            return False
        self._index = faiss.read_index(str(idx))
        with open(chk, "rb") as f:
            self._chunks = pickle.load(f)
        log.info("Index loaded ← '%s'  (%d vectors).", folder, self._index.ntotal)
        return True

    @property
    def is_empty(self) -> bool:
        return self._index.ntotal == 0


# ╔══════════════════════════════════════════════════════╗
# ║  LLM  (Gemini)                                       ║
# ╚══════════════════════════════════════════════════════╝

# ── Provider routing ──────────────────────────────────
def _ask_llm(prompt: str, provider: str = "gemini") -> str:
    if provider == "groq":
        return _ask_groq(prompt)
    return _ask_gemini(prompt)

def _ask_gemini(prompt: str) -> str:
    genai.configure(api_key=GEMINI_API_KEY)
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        log.error("Gemini error: %s", e)
        return f"[Error contacting Gemini: {e}]"

def _ask_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "[Error: GROQ_API_KEY is missing.]"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        log.error("Groq error: %s", e)
        return f"[Error contacting Groq: {e}]"


# ╔══════════════════════════════════════════════════════╗
# ║  RAG — MODE 1: CNN disease advisory                  ║
# ╚══════════════════════════════════════════════════════╝

def disease_advisory(inp: DiseaseInput, store: VectorStore, provider: str = "gemini") -> Result:
    """
    Healthy leaf  →  short healthy message, no retrieval.
    Diseased leaf →  retrieve relevant chunks, ask Gemini for a full advisory.
    """
    if inp.is_healthy:
        return Result(
            answer=(
                "The leaf appears healthy. No disease treatment is required.\n"
                "Continue regular monitoring and maintain good agronomic practices."
            ),
            confidence=inp.confidence
        )

    # Step 1: Intelligent Retrieval based on intent
    if inp.user_question:
        # A: Farmer has a specific concern - prioritize question-driven retrieval
        query_parts = [f"Specifically answering: {inp.user_question}", f"About: {inp.disease}"]
        if inp.env_data:
            query_parts.append(" ".join(str(v) for v in inp.env_data.values()))
        query = " ".join(query_parts)
    else:
        # B: General health report - retrieve broad advisory context
        query_parts = [f"{inp.disease} coffee treatment prevention fertilizer"]
        if inp.env_data:
            query_parts.append(" ".join(str(v) for v in inp.env_data.values()))
        query = " ".join(query_parts)

    chunks, scores = store.search(query, top_k=5)
    best_score = scores[0] if scores else 0.0
    context = _fmt_context(chunks[:5])
    dyn_conf = _score_to_conf(best_score)

    # Step 2: Dynamic Prompt Generation
    env_section = ""
    if inp.env_data:
        env_section = "\nCurrent Site Conditions:\n"
        for k, v in inp.env_data.items():
            env_section += f"- {k}: {v}\n"

    if inp.user_question:
        # FOCUSED PROMPT
        prompt = f"""\
You are an expert agronomist. A farmer has a specific question regarding a coffee plant.

CNN Diagnosis : {inp.disease} ({inp.confidence*100:.1f}% confidence)
{env_section}
Farmer's Question: {inp.user_question}

Knowledge Base Context:
{context}

Please answer the farmer's specific question directly based on the provided knowledge base. 
If the answer is not in the context, use your expert knowledge to provide a safe and helpful agricultural response.
Be concise and speak directly to the farmer."""
    else:
        # DEFAULT ADVISORY PROMPT
        prompt = f"""\
You are an expert agronomist specialising in coffee crop diseases.

CNN Diagnosis : {inp.disease} ({inp.confidence*100:.1f}% confidence)
{env_section}

Knowledge Base Context:
{context}

Give a comprehensive practical advisory covering:
1. Disease explanation & symptoms
2. How the current environment might be contributing
3. Immediate treatment steps
4. Fertilizer / soil recommendations for recovery
5. Prevention strategies going forward

Be concise. Speak directly to the farmer."""

    return Result(answer=_ask_llm(prompt, provider), confidence=dyn_conf, sources=_sources(chunks))


# ╔══════════════════════════════════════════════════════╗
# ║  RAG — MODE 2: Plain user question                   ║
# ╚══════════════════════════════════════════════════════╝

def answer_question(question: str, store: VectorStore, provider: str = "gemini") -> list[Result]:
    """Retrieve top-3 chunks and return 3 separate LLM responses (Top 3 mode)."""
    chunks, scores = store.search(question, top_k=3)

    if not chunks:
        # No index or no matches — Gemini answers from its own knowledge
        prompt = (
            f"You are a coffee crop expert. "
            f"Answer this farmer's question clearly and practically:\n\n{question}"
        )
        return [Result(answer=_ask_gemini(prompt), confidence=0.75)]

    results = []
    for i, (chunk, score) in enumerate(zip(chunks, scores)):
        prompt = (
            f"You are an expert in coffee crop cultivation and disease management.\n\n"
            f"Use the specific context below to answer the farmer's question.\n\n"
            f"Context (Source: {chunk.source} p.{chunk.page}):\n{chunk.text}\n\n"
            f"Question: {question}\n\nAnswer:"
        )
        ans = _ask_llm(prompt, provider)
        results.append(Result(
            answer=ans,
            confidence=_score_to_conf(score),
            sources=[f"{chunk.source} (p.{chunk.page})"]
        ))
    return results


def answer_question_fast(question: str, store: VectorStore, provider: str = "gemini", top_k: int = 3) -> Result:
    """Single-call variant: retrieve top_k chunks, answer once using all of them as combined context."""
    chunks, scores = store.search(question, top_k=top_k)

    if not chunks:
        prompt = (
            f"You are a coffee crop expert. "
            f"Answer this farmer's question clearly and practically:\n\n{question}"
        )
        return Result(answer=_ask_llm(prompt, provider), confidence=0.75)

    context = _fmt_context(chunks)
    prompt = (
        f"You are an expert in coffee crop cultivation and disease management.\n\n"
        f"Use the context below to answer the farmer's question. Combine information "
        f"from multiple sources where relevant.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )
    ans = _ask_llm(prompt, provider)
    best_score = scores[0] if scores else 0.0
    return Result(answer=ans, confidence=_score_to_conf(best_score), sources=_sources(chunks))


def answer_question_with_env(
    question: str,
    env_data: dict,
    store: VectorStore,
    provider: str = "gemini",
    top_k: int = 3,
) -> Result:
    """
    Environment-aware single-call Q&A.
    Live microclimate data (e.g. from Open-Meteo) is blended into the retrieval
    query — so conditions like high humidity pull in rust/blight-relevant chunks —
    and into the final prompt, so the LLM reasons about current conditions
    alongside the farmer's question and the retrieved knowledge base context.
    """
    env_block = "\n".join(f"- {k}: {v}" for k, v in env_data.items()) if env_data else ""
    env_terms = " ".join(str(v) for v in env_data.values()) if env_data else ""

    search_query = f"{question} {env_terms}".strip() or "coffee crop health advisory"
    chunks, scores = store.search(search_query, top_k=top_k)

    if not chunks:
        prompt = (
            f"You are a coffee crop expert advising a farmer.\n\n"
            f"Current Microclimate Conditions (live data for the farmer's location):\n{env_block or 'Not available'}\n\n"
            f"Farmer's Question: {question}\n\n"
            f"Answer clearly and practically, factoring in the current environmental conditions."
        )
        return Result(answer=_ask_llm(prompt, provider), confidence=0.7)

    context = _fmt_context(chunks)
    prompt = f"""\
You are an expert agronomist specialising in coffee crop diseases.

Current Microclimate Conditions (live data for the farmer's location):
{env_block or 'Not available'}

Knowledge Base Context:
{context}

Farmer's Question: {question}

Answer the farmer's question directly, grounded in the knowledge base context above.
Explicitly factor in how the current environmental conditions (temperature, humidity,
rainfall, soil conditions, etc.) affect disease risk, treatment timing, or urgency.
Be concise and speak directly to the farmer."""

    ans = _ask_llm(prompt, provider)
    best_score = scores[0] if scores else 0.0
    return Result(answer=ans, confidence=_score_to_conf(best_score), sources=_sources(chunks))


def _score_to_conf(score: float) -> float:
    """Convert FAISS score (0-1) to balanced confidence (0-1)."""
    # FAISS IndexFlatIP scores for normalized vectors are cosine similarities.
    conf = max(0.0, min(1.0, float(score)))
    if conf < 0.3:
        return conf * 0.5
    return conf


# ── shared helpers ────────────────────────────────────────────────────────────

def _fmt_context(chunks: list[Chunk]) -> str:
    return "\n\n".join(
        f"[{i+1}] {c.source} p.{c.page}\n{c.text}"
        for i, c in enumerate(chunks)
    ) or "No context retrieved."


def _sources(chunks: list[Chunk]) -> list[str]:
    seen, out = set(), []
    for c in chunks:
        key = f"{c.source}  (p.{c.page})"
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


# ╔══════════════════════════════════════════════════════╗
# ║  INDEX BOOTSTRAP  (called by main.py)                ║
# ╚══════════════════════════════════════════════════════╝

def get_store(provider: str = "gemini") -> VectorStore:
    """
    Called by main.py / app.py. Provider is choice purely for config validation here.
    """
    _validate_config(provider)
    store = VectorStore()

    if store.load(INDEX_FOLDER):
        return store

    log.info("No saved index — ingesting PDFs from '%s' …", PDF_FOLDER)
    chunks = load_pdfs(PDF_FOLDER)

    if not chunks:
        print(
            f"\n⚠️  PDF folder '{PDF_FOLDER}' is empty or missing.\n"
            "   Add PDFs and delete the index folder to rebuild.\n"
            "   Gemini will answer using its built-in knowledge for now.\n"
        )
        return store

    store.add(chunks)
    store.save(INDEX_FOLDER)
    return store

import os
import re
import pickle
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from app.core.config import settings

try:
    import fitz  # PyMuPDF
    _PDF_BACKEND = "pymupdf"
except ImportError:
    try:
        import pdfplumber
        _PDF_BACKEND = "pdfplumber"
    except ImportError:
        _PDF_BACKEND = "none"

log = logging.getLogger(__name__)

@dataclass
class Chunk:
    text: str
    source: str
    page: int

_EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_DIM = 384
_IDX_FILE = "faiss.index"
_CHUNK_FILE = "chunks.pkl"

class VectorStore:
    def __init__(self):
        log.info("Loading embedding model (%s)...", _EMBED_MODEL)
        self.embedder = SentenceTransformer(_EMBED_MODEL)
        self.index = faiss.IndexFlatIP(_DIM)
        self.chunks: List[Chunk] = []

    def add_chunks(self, chunks: List[Chunk], batch_size: int = 64):
        if not chunks:
            return
        texts = [c.text for c in chunks]
        all_embs = []
        for i in range(0, len(texts), batch_size):
            embs = self.embedder.encode(
                texts[i:i+batch_size],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            )
            all_embs.append(embs)
        self.index.add(np.vstack(all_embs).astype("float32"))
        self.chunks.extend(chunks)
        log.info("VectorStore index now has %d vectors.", self.index.ntotal)

    def search(self, query: str, top_k: int = 5) -> Tuple[List[Chunk], List[float]]:
        if self.index.ntotal == 0:
            return [], []
        q_emb = self.embedder.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        ).astype("float32")
        scores, ids = self.index.search(q_emb, top_k)
        
        found_chunks = [self.chunks[i] for i in ids[0] if i != -1 and i < len(self.chunks)]
        found_scores = [float(s) for i, s in zip(ids[0], scores[0]) if i != -1 and i < len(self.chunks)]
        return found_chunks, found_scores

    def save(self, folder: str = settings.INDEX_FOLDER):
        Path(folder).mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(Path(folder) / _IDX_FILE))
        with open(Path(folder) / _CHUNK_FILE, "wb") as f:
            pickle.dump(self.chunks, f)
        log.info("Saved vector index to %s", folder)

    def load(self, folder: str = settings.INDEX_FOLDER) -> bool:
        idx_path = Path(folder) / _IDX_FILE
        chk_path = Path(folder) / _CHUNK_FILE
        if not idx_path.exists() or not chk_path.exists():
            return False
        try:
            self.index = faiss.read_index(str(idx_path))
            with open(chk_path, "rb") as f:
                self.chunks = pickle.load(f)
            log.info("Loaded vector index from %s (%d vectors).", folder, self.index.ntotal)
            return True
        except Exception as e:
            log.error("Failed loading index: %s", e)
            return False

def load_pdfs_from_folder(folder: str) -> List[Chunk]:
    pdf_dir = Path(folder)
    if not pdf_dir.exists():
        return []
    pdf_files = list(pdf_dir.glob("**/*.pdf"))
    if not pdf_files:
        return []

    chunks: List[Chunk] = []
    for path in pdf_files:
        pages = _extract_pages(str(path))
        for page_num, text in pages:
            chunks.extend(_split_text(text, path.name, page_num))
    return chunks

def _extract_pages(path: str) -> List[Tuple[int, str]]:
    if _PDF_BACKEND == "pymupdf":
        doc = fitz.open(path)
        pages = [(i + 1, _clean_text(p.get_text("text"))) for i, p in enumerate(doc)]
        doc.close()
        return [(n, t) for n, t in pages if t.strip()]
    elif _PDF_BACKEND == "pdfplumber":
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [(i + 1, _clean_text(p.extract_text() or "")) for i, p in enumerate(pdf.pages)]
        return [(n, t) for n, t in pages if t.strip()]
    return []

def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E]", " ", text)
    return text.strip()

def _split_text(text: str, source: str, page: int, size: int = 400, overlap: int = 50) -> List[Chunk]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(Chunk(" ".join(words[start:end]), source, page))
        if end == len(words):
            break
        start += size - overlap
    return chunks

_vector_store_instance = None

def get_vector_store() -> VectorStore:
    global _vector_store_instance
    if _vector_store_instance is None:
        store = VectorStore()
        if not store.load(settings.INDEX_FOLDER):
            print(f"[RAG VectorStore] Initializing index from PDFs in {settings.PDF_FOLDER}...")
            chunks = load_pdfs_from_folder(settings.PDF_FOLDER)
            if chunks:
                store.add_chunks(chunks)
                store.save(settings.INDEX_FOLDER)
            else:
                print(f"[RAG VectorStore] Warning: No PDFs found in {settings.PDF_FOLDER}")
        _vector_store_instance = store
    return _vector_store_instance

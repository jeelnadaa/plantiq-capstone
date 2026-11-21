"""Index build + model loading for the snapshot. Same steps as backend/app/services/rag/index.py (build_index,
load_embedder) and HybridRetriever.load_or_build, with explicit paths instead of app settings."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

# same as backend/app/core/config.py: sequential .bin loading (the async loader can segfault on Windows)
os.environ.setdefault("HF_DEACTIVATE_ASYNC_LOAD", "1")

from .index import extract_chunks
from .profiles import RagProfile
from .retriever import HybridRetriever


def load_embedder(profile: RagProfile, device: str):
    from sentence_transformers import SentenceTransformer

    kwargs = {}
    if profile.fp16 and device == "cuda":
        import torch

        kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
    return SentenceTransformer(profile.embedder, device=device, **kwargs)


def load_reranker(profile: RagProfile, device: str):
    from sentence_transformers import CrossEncoder

    kwargs = {}
    if profile.fp16 and device == "cuda":
        import torch

        kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
    return CrossEncoder(profile.reranker, device=device, **kwargs)


def build_retriever(profile: RagProfile, docs_dir: Path, index_dir: Path, device: str = "cuda",
                    embedder=None, reranker=None) -> HybridRetriever:
    """Chunk the PDFs, embed, build the FAISS index (cached in index_dir) and return a HybridRetriever."""
    import faiss
    import numpy as np

    index_dir.mkdir(parents=True, exist_ok=True)
    embedder = embedder or load_embedder(profile, device)
    meta_path = index_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    pdfs = sorted(p.name for p in docs_dir.glob("*.pdf"))
    if meta.get("embedder") == profile.embedder and meta.get("sources_pdf") == pdfs:
        index = faiss.read_index(str(index_dir / "faiss.index"))
        chunks = json.loads((index_dir / "chunks.json").read_text(encoding="utf-8"))
    else:
        t0 = time.perf_counter()
        chunks = extract_chunks(docs_dir)
        emb = embedder.encode([c["text"] for c in chunks], batch_size=32 if profile.fp16 else 64,
                              normalize_embeddings=True, convert_to_numpy=True,
                              show_progress_bar=False).astype(np.float32)
        index = faiss.IndexFlatIP(emb.shape[1])
        index.add(emb)
        faiss.write_index(index, str(index_dir / "faiss.index"))
        (index_dir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
        meta = {"embedder": profile.embedder, "profile": profile.name, "dimension": int(emb.shape[1]),
                "chunks": len(chunks), "sources_pdf": pdfs, "build_seconds": round(time.perf_counter() - t0, 1)}
        meta_path.write_text(json.dumps(meta, indent=2))
    if index.ntotal != len(chunks):
        raise ValueError("Index and chunk file are out of sync")
    reranker = reranker if reranker is not None else load_reranker(profile, device)
    return HybridRetriever(index, chunks, embedder, reranker, profile, device)

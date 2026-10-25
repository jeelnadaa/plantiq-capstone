"""Build / load the knowledge index.  Files (no pickle anywhere):

    faiss.index   dense inner-product index of normalised embeddings
    chunks.json   chunk texts + metadata
    meta.json     embedder, dimension, chunk count, build time, source files
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from app.core.config import settings
from app.services.rag.chunking import chunk_page, detect_topic
from app.services.rag.profiles import RagProfile, choose_profile, resolve_model

log = logging.getLogger("plantiq.rag")


def extract_chunks(docs_dir: Path) -> list[dict]:
    import fitz  # PyMuPDF

    pdfs = sorted(p for p in docs_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDF files in {docs_dir}")
    all_chunks: list[dict] = []
    for pdf in pdfs:
        count = 0
        try:
            with fitz.open(pdf) as doc:
                for p_idx, page in enumerate(doc, start=1):
                    try:  # spray-schedule / dosage tables as their own chunks
                        tables = page.find_tables()
                        for t_idx, tab in enumerate(getattr(tables, "tables", []) or [], start=1):
                            md = tab.to_markdown() if hasattr(tab, "to_markdown") else ""
                            if md and len(md.strip()) > 40:
                                all_chunks.append({
                                    "text": f"[Schedule & dosage table] {md.strip()[:2500]}",
                                    "source": pdf.name, "page": p_idx, "section": f"Table {t_idx}",
                                    "topic": detect_topic(pdf.name, md),
                                })
                                count += 1
                    except Exception:
                        pass
                    text = page.get_text("text")
                    if text.strip():
                        page_chunks = chunk_page(text, pdf.name, p_idx)
                        all_chunks.extend(page_chunks)
                        count += len(page_chunks)
        except Exception as exc:
            log.warning("Skipping %s: %s", pdf.name, exc)
        log.info("  %-60s %4d chunks", pdf.name[:60], count)
    # de-duplicate identical texts (running headers/footers)
    seen: set[str] = set()
    unique = []
    for c in all_chunks:
        key = c["text"][:300]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    for i, c in enumerate(unique):
        c["id"] = i
    return unique


def load_embedder(profile: RagProfile, device: str):
    from sentence_transformers import SentenceTransformer

    kwargs = {}
    if profile.fp16 and device == "cuda":
        import torch

        kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
    return SentenceTransformer(resolve_model(profile.embedder), device=device, token=settings.HF_TOKEN or None, **kwargs)


def build_index(profile: RagProfile | None = None, docs_dir: Path | None = None, index_dir: Path | None = None,
                device: str | None = None) -> dict:
    import faiss
    import numpy as np

    from app.services.cnn import resolve_device

    profile = profile or choose_profile()
    docs_dir = Path(docs_dir or settings.RAG_DOCS_DIR)
    index_dir = Path(index_dir or settings.RAG_INDEX_DIR)
    device = device or resolve_device()
    index_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    log.info("Building RAG index: profile=%s embedder=%s device=%s", profile.name, profile.embedder, device)
    chunks = extract_chunks(docs_dir)
    embedder = load_embedder(profile, device)
    emb = embedder.encode([c["text"] for c in chunks], batch_size=32 if profile.fp16 else 64,
                          normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
    index = faiss.IndexFlatIP(emb.shape[1])
    index.add(emb)

    tmp = index_dir / "faiss.index.tmp"
    faiss.write_index(index, str(tmp))
    tmp.replace(index_dir / "faiss.index")
    (index_dir / "chunks.json").write_text(json.dumps(chunks, ensure_ascii=False), encoding="utf-8")
    meta = {
        "embedder": profile.embedder,
        "profile": profile.name,
        "dimension": int(emb.shape[1]),
        "chunks": len(chunks),
        "sources": sorted({c["source"] for c in chunks}),
        "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "build_seconds": round(time.perf_counter() - t0, 1),
    }
    (index_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    log.info("RAG index built: %d chunks, dim=%d in %.1fs", len(chunks), emb.shape[1], meta["build_seconds"])
    del embedder
    return meta


def read_meta(index_dir: Path | None = None) -> dict | None:
    path = Path(index_dir or settings.RAG_INDEX_DIR) / "meta.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_files(index_dir: Path | None = None):
    import faiss

    index_dir = Path(index_dir or settings.RAG_INDEX_DIR)
    index = faiss.read_index(str(index_dir / "faiss.index"))
    chunks = json.loads((index_dir / "chunks.json").read_text(encoding="utf-8"))
    if index.ntotal != len(chunks):
        raise ValueError("Index and chunk file are out of sync")
    return index, chunks

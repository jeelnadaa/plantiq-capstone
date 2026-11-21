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

from .chunking import chunk_page, detect_topic

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



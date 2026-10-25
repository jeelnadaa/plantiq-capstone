"""Build the hybrid-RAG knowledge index from data/knowledge_base/*.pdf.

    python scripts/build_index.py                 # profile from RAG_PROFILE (auto → quality on a >=6 GB GPU)
    python scripts/build_index.py --profile balanced
    python scripts/build_index.py --query "rust bordeaux dose"   # build (if needed) then test a query
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["auto", "quality", "balanced"], default=None)
    parser.add_argument("--query", default=None)
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args()

    from app.core.config import settings
    from app.services.rag.index import build_index, read_meta
    from app.services.rag.profiles import choose_profile

    if args.profile:
        settings.RAG_PROFILE = args.profile
    profile = choose_profile()
    if not args.skip_build:
        meta = build_index(profile)
        print(f"\nBuilt {meta['chunks']} chunks with {meta['embedder']} (dim {meta['dimension']}) in {meta['build_seconds']}s")
        print("Sources:", ", ".join(meta["sources"]))
    else:
        print("Existing index:", read_meta())

    if args.query:
        from app.services.rag.retriever import HybridRetriever

        settings.RAG_AUTO_BUILD = False
        r = HybridRetriever.load_or_build()
        for i, d in enumerate(r.search(args.query, top_k=3), 1):
            print(f"\n[{i}] score={d['score']:.3f} {d['source']} p.{d['metadata']['page']} ({d['metadata']['topic']})")
            print("   ", d["text"][:300])


if __name__ == "__main__":
    main()

"""Download the RAG models once and store them locally as safetensors.

    python scripts/prepare_models.py                 # models for the auto-selected profile
    python scripts/prepare_models.py --profile quality

Why: BAAI/bge-m3 and BAAI/bge-reranker-v2-m3 are published only as pickle-based pytorch_model.bin.
Loading those needs a full in-memory copy (crashes on low-RAM machines) and executes pickle. Saved here as
safetensors they load memory-mapped, faster, offline, with no pickle. The retriever automatically prefers
data/models/hf/<name> when it exists.
"""
from __future__ import annotations

import argparse
import gc
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=["auto", "quality", "balanced"], default=None)
    ap.add_argument("--only", choices=["embedder", "reranker"], default=None)
    args = ap.parse_args()

    from app.core.config import settings
    from app.services.rag.profiles import choose_profile, local_model_dir

    if args.profile:
        settings.RAG_PROFILE = args.profile
    profile = choose_profile()
    token = settings.HF_TOKEN or None

    if args.only in (None, "embedder"):
        target = local_model_dir(profile.embedder)
        if target.exists():
            print(f"[skip] {profile.embedder} already at {target}")
        else:
            from sentence_transformers import SentenceTransformer

            print(f"[get ] {profile.embedder}")
            m = SentenceTransformer(profile.embedder, device="cpu", token=token)
            m.save(str(target), safe_serialization=True)
            print(f"[save] {target}")
            del m
            gc.collect()

    if args.only in (None, "reranker"):
        target = local_model_dir(profile.reranker)
        if target.exists():
            print(f"[skip] {profile.reranker} already at {target}")
        else:
            from sentence_transformers import CrossEncoder

            print(f"[get ] {profile.reranker}")
            m = CrossEncoder(profile.reranker, device="cpu", token=token)
            m.save(str(target), safe_serialization=True)
            print(f"[save] {target}")


if __name__ == "__main__":
    main()

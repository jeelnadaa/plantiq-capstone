"""Hardware-aware model profiles for the hybrid retriever."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from app.core.config import settings

log = logging.getLogger("plantiq.rag")


@dataclass(frozen=True)
class RagProfile:
    name: str
    embedder: str
    reranker: str
    query_prefix: str
    fp16: bool


QUALITY = RagProfile(
    name="quality",
    embedder="BAAI/bge-m3",
    reranker="BAAI/bge-reranker-v2-m3",
    query_prefix="",  # bge-m3 needs no instruction prefix and embeds Kannada natively
    fp16=True,
)
BALANCED = RagProfile(
    name="balanced",
    embedder="BAAI/bge-base-en-v1.5",
    reranker="cross-encoder/ms-marco-MiniLM-L-6-v2",
    query_prefix="Represent this sentence for searching relevant passages: ",
    fp16=False,
)
PROFILES = {"quality": QUALITY, "balanced": BALANCED}


def gpu_memory_gb() -> float:
    try:
        import torch

        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / 1024**3
    except Exception:
        pass
    return 0.0


def choose_profile(requested: str | None = None) -> RagProfile:
    req = (requested or settings.RAG_PROFILE or "auto").lower()
    if req in PROFILES:
        return PROFILES[req]
    if settings.ML_DEVICE != "cpu" and gpu_memory_gb() >= 6.0:
        return QUALITY
    return BALANCED


def profile_for_embedder(embedder: str) -> RagProfile:
    for p in PROFILES.values():
        if p.embedder == embedder:
            return p
    return RagProfile(name="custom", embedder=embedder, reranker=BALANCED.reranker, query_prefix="", fp16=False)

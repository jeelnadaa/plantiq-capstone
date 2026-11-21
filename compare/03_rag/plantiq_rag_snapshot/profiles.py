"""Model profiles, copied from backend/app/services/rag/profiles.py (dataclass + the two profiles only;
automatic hardware selection is left out because the benchmark pins the profile explicitly)."""
from __future__ import annotations

from dataclasses import dataclass


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

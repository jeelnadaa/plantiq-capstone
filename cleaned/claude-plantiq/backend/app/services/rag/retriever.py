"""Hybrid retriever: dense (FAISS) + sparse (BM25) → RRF → topic filter → cross-encoder rerank → MMR."""
from __future__ import annotations

import logging
import math
import re
import threading
import time
from collections import OrderedDict
from typing import Any

from app.core.config import settings
from app.services.rag.profiles import BALANCED, RagProfile, choose_profile, profile_for_embedder

log = logging.getLogger("plantiq.rag")
_TOKEN_RE = re.compile(r"\b\w+\b", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return [w.lower() for w in _TOKEN_RE.findall(text) if len(w) > 1]


def sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    e = math.exp(x)
    return e / (1.0 + e)


def rrf_fuse(rank_lists: list[dict[int, int]], k: float = 60.0, missing_rank: int = 1000) -> dict[int, float]:
    """Reciprocal Rank Fusion: score(d) = Σ 1/(k + rank_i(d))."""
    ids: set[int] = set()
    for ranks in rank_lists:
        ids.update(ranks)
    return {i: sum(1.0 / (k + ranks.get(i, missing_rank)) for ranks in rank_lists) for i in ids}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def mmr_select(candidates: list[dict], top_k: int, lambda_: float = 0.75) -> list[dict]:
    """Maximal Marginal Relevance on token sets: keeps relevant chunks while dropping near-duplicates."""
    pool = [dict(c, _tok=set(tokenize(c["text"]))) for c in candidates]
    chosen: list[dict] = []
    while pool and len(chosen) < top_k:
        best, best_score = None, -1e9
        for c in pool:
            redundancy = max((jaccard(c["_tok"], s["_tok"]) for s in chosen), default=0.0)
            score = lambda_ * c["score"] - (1 - lambda_) * redundancy
            if score > best_score:
                best, best_score = c, score
        pool.remove(best)
        chosen.append(best)
    for c in chosen:
        c.pop("_tok", None)
    return chosen


class HybridRetriever:
    def __init__(self, index: Any, chunks: list[dict], embedder: Any, reranker: Any | None, profile: RagProfile,
                 device: str = "cpu") -> None:
        from rank_bm25 import BM25Okapi

        self.index = index
        self.chunks = chunks
        self.embedder = embedder
        self.reranker = reranker
        self.profile = profile
        self.device = device
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in chunks]) if chunks else None
        self._cache: OrderedDict[str, list[dict]] = OrderedDict()
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ loading
    @classmethod
    def load_or_build(cls) -> "HybridRetriever":
        from app.services.cnn import resolve_device
        from app.services.rag import index as idx

        device = resolve_device()
        wanted = choose_profile()
        meta = idx.read_meta()
        profile = wanted
        try:
            if meta is None or meta.get("embedder") != wanted.embedder:
                if settings.RAG_AUTO_BUILD:
                    try:
                        idx.build_index(wanted, device=device)
                    except Exception as exc:
                        if wanted is BALANCED:
                            raise
                        log.warning("Could not build '%s' index (%s); falling back to balanced profile", wanted.name, exc)
                        profile = BALANCED
                        if not meta or meta.get("embedder") != BALANCED.embedder:
                            idx.build_index(BALANCED, device=device)
                elif meta is not None:
                    profile = profile_for_embedder(meta["embedder"])
                else:
                    raise FileNotFoundError("RAG index missing and RAG_AUTO_BUILD is off")
            index, chunks = idx.load_files()
            embedder = idx.load_embedder(profile, device)
        except Exception as exc:
            if profile is BALANCED:
                raise
            log.warning("Quality RAG profile unavailable (%s). Using balanced profile.", exc)
            profile = BALANCED
            if (idx.read_meta() or {}).get("embedder") != BALANCED.embedder:
                idx.build_index(BALANCED, device=device)
            index, chunks = idx.load_files()
            embedder = idx.load_embedder(profile, device)

        reranker = None
        try:
            from sentence_transformers import CrossEncoder

            kwargs = {}
            if profile.fp16 and device == "cuda":
                import torch

                kwargs["model_kwargs"] = {"torch_dtype": torch.float16}
            from app.services.rag.profiles import resolve_model

            reranker = CrossEncoder(resolve_model(profile.reranker), device=device, token=settings.HF_TOKEN or None, **kwargs)
        except Exception as exc:
            log.warning("Reranker %s unavailable (%s); using RRF scores.", profile.reranker, exc)
        log.info("RAG ready: profile=%s, %d chunks, device=%s", profile.name, len(chunks), device)
        return cls(index, chunks, embedder, reranker, profile, device)

    def info(self) -> dict:
        return {
            "profile": self.profile.name, "embedder": self.profile.embedder,
            "reranker": self.profile.reranker if self.reranker is not None else None,
            "chunks": len(self.chunks), "device": self.device,
        }

    # ------------------------------------------------------------------ search
    def _dense(self, query: str, k: int) -> dict[int, int]:
        import numpy as np

        if self.index is None or self.embedder is None:
            return {}
        vec = self.embedder.encode([self.profile.query_prefix + query], normalize_embeddings=True,
                                   convert_to_numpy=True, show_progress_bar=False).astype(np.float32)
        _, ids = self.index.search(vec, k)
        return {int(i): r for r, i in enumerate(ids[0], start=1) if 0 <= i < len(self.chunks)}

    def _sparse(self, query: str, k: int) -> dict[int, int]:
        if self.bm25 is None:
            return {}
        toks = tokenize(query)
        if not toks:
            return {}
        scores = self.bm25.get_scores(toks)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return {i: r for r, i in enumerate(order, start=1) if scores[i] > 0}

    def _rerank(self, query: str, cands: list[tuple[int, dict]], fused: dict[int, float]) -> list[dict]:
        results: list[dict] = []
        if self.reranker is not None and cands:
            try:
                import torch

                logits = self.reranker.predict([[query, c["text"]] for _, c in cands],
                                               activation_fn=torch.nn.Identity(), show_progress_bar=False)
                for (i, c), z in zip(cands, list(logits)):
                    results.append(self._fmt(i, c, sigmoid(float(z))))
            except Exception as exc:
                log.warning("Rerank failed (%s); using RRF.", exc)
                results = []
        if not results:
            top = max((fused[i] for i, _ in cands), default=1.0) or 1.0
            results = [self._fmt(i, c, fused[i] / top) for i, c in cands]
        results.sort(key=lambda r: r["score"], reverse=True)
        return results

    @staticmethod
    def _fmt(i: int, c: dict, score: float) -> dict:
        return {
            "id": c.get("id", i), "text": c.get("text", ""), "source": c.get("source", "CCRI guide"),
            "score": round(max(0.0, min(1.0, score)), 4),
            "metadata": {"page": c.get("page", 1), "section": c.get("section", ""), "topic": c.get("topic", "")},
        }

    def search(self, query: str, top_k: int = 3, topic_filter: str | None = None, pool: int = 20,
               rerank_query: str | None = None) -> list[dict]:
        """`query` drives dense+BM25 recall (keyword expansion helps); `rerank_query` is the natural-language
        question the cross-encoder scores against (cross-encoders are calibrated on questions, not keyword soup)."""
        query = (query or "").strip()
        if not query or not self.chunks:
            return []
        rq = (rerank_query or query).strip()
        key = f"{query}|{rq}|{top_k}|{topic_filter}"
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
                return [dict(r) for r in self._cache[key]]
        t0 = time.perf_counter()
        k = min(pool, len(self.chunks))
        dense, sparse = self._dense(query, k), self._sparse(query, k)
        fused = rrf_fuse([dense, sparse])
        if not fused:
            return []
        ordered = sorted(fused, key=fused.get, reverse=True)
        on_topic = [(i, self.chunks[i]) for i in ordered if not topic_filter or self.chunks[i].get("topic") == topic_filter]
        final = mmr_select(self._rerank(rq, on_topic[:k], fused)[: max(top_k * 3, 6)], top_k) if on_topic else []
        if len(final) < top_k:  # relax the topic filter rather than return too little; on-topic stays first
            off_topic = [(i, c) for i, c in ((i, self.chunks[i]) for i in ordered) if (i, c) not in on_topic][:k]
            final += mmr_select(self._rerank(rq, off_topic, fused), top_k - len(final))
        log.info("RAG search %.0f ms: dense=%d sparse=%d -> %d (top %.2f)", (time.perf_counter() - t0) * 1000,
                 len(dense), len(sparse), len(final), final[0]["score"] if final else 0)
        with self._lock:
            self._cache[key] = final
            if len(self._cache) > 256:
                self._cache.popitem(last=False)
        return [dict(r) for r in final]

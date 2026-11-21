"""RAG benchmark helpers: KB text, chunk relevance, retrieval metrics, RAGAS-definition judge metrics, baselines.

Relevance is defined by the GOLD EVIDENCE QUOTES stored with each question (exact sentences from a KB PDF), not by
chunk IDs, so systems that chunk the PDFs differently are scored by one rule:
    a retrieved chunk is relevant to a quote if >= 80 % of the quote's tokens appear in the chunk, in order.
"""
from __future__ import annotations

import difflib
import hashlib
import math
import re
import unicodedata
from pathlib import Path

import numpy as np

from . import config

MATCH_THRESHOLD = 0.8
TOPICS = {  # benchmark topic -> disease label passed to every system (as the CNN diagnosis would be)
    "rust": "Rust", "cercospora": "Cerscospora", "phoma": "Phoma", "miner": "Miner", "cultivation": "Healthy",
}
TOPIC_NAMES = {"rust": "coffee leaf rust", "cercospora": "Cercospora leaf spot (brown eye spot)",
               "phoma": "Phoma leaf spot / dieback", "miner": "coffee leaf miner",
               "cultivation": "coffee cultivation practice (shade, pruning, nutrition, soil, irrigation, planting)"}
TOPIC_KEYWORDS = {  # used ONLY to pick source passages when drafting questions
    "rust": ("rust", "hemileia"),
    "cercospora": ("cercospora", "brown eye", "coffeicola"),
    "phoma": ("phoma",),
    "miner": ("miner", "leucoptera"),
    "cultivation": ("shade", "pruning", "fertiliz", "fertilis", "nutrient", "manure", "irrigation", "blossom",
                    "lime", "planting", "spacing", "soil", "mulch", "weed"),
}


# --------------------------------------------------------------------------- text
def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"-\s*\n\s*", "", text)          # join hyphenated line breaks
    text = text.lower()
    text = re.sub(r"[^0-9a-zಀ-೿%.]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> list[str]:
    return normalize(text).split()


def page_texts(kb_dir: Path = config.KB_DIR) -> list[dict]:
    """PyMuPDF text of every page (the same extractor PlantIQ uses)."""
    import fitz

    pages = []
    for pdf in sorted(kb_dir.glob("*.pdf")):
        with fitz.open(pdf) as doc:
            for i, page in enumerate(doc, start=1):
                t = page.get_text("text")
                if t.strip():
                    pages.append({"source": pdf.name, "page": i, "text": t})
    return pages


def quote_in_text(quote: str, text: str, threshold: float = MATCH_THRESHOLD) -> float:
    """Share of the quote's tokens found in `text` in order (longest matching blocks). 1.0 = verbatim."""
    q, t = tokens(quote), tokens(text)
    if not q:
        return 0.0
    if " ".join(q) in " ".join(t):
        return 1.0
    sm = difflib.SequenceMatcher(None, q, t, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    return matched / len(q)


def chunk_relevance(chunks: list[str], quotes: list[str]) -> np.ndarray:
    """(n_chunks, n_quotes) boolean: chunk i contains quote j."""
    return np.array([[quote_in_text(q, c) >= MATCH_THRESHOLD for q in quotes] for c in chunks], dtype=bool) \
        if chunks else np.zeros((0, len(quotes)), dtype=bool)


# --------------------------------------------------------------------------- retrieval metrics
def retrieval_metrics(rel: np.ndarray, ks=(1, 3, 5, 10)) -> dict:
    """rel: (n_ranked, n_quotes) from chunk_relevance for one ranked list.
    Recall@k = share of gold quotes covered by the top k; Hit@k = any relevant chunk in top k;
    nDCG@k with binary gain (a chunk is relevant if it covers any quote); MRR@10."""
    n_q = rel.shape[1]
    rel_any = rel.any(1) if len(rel) else np.zeros(0, dtype=bool)
    out = {}
    for k in ks:
        top = rel[:k]
        out[f"recall@{k}"] = float(top.any(0).sum() / n_q) if n_q else float("nan")
        out[f"hit@{k}"] = float(rel_any[:k].any()) if len(rel_any) else 0.0
        gains = rel_any[:k].astype(float)
        dcg = float(sum(g / math.log2(i + 2) for i, g in enumerate(gains)))
        ideal = min(k, max(n_q, int(rel_any.sum())))
        idcg = float(sum(1 / math.log2(i + 2) for i in range(ideal))) if ideal else 0.0
        out[f"ndcg@{k}"] = dcg / idcg if idcg else 0.0
    first = np.where(rel_any[:10])[0] if len(rel_any) else []
    out["mrr@10"] = float(1 / (first[0] + 1)) if len(first) else 0.0
    return out


# --------------------------------------------------------------------------- judge metrics (RAGAS definitions)
JUDGE_SYSTEM = ("You are a strict, careful evaluator of coffee-farming advice for growers in Karnataka, India. "
                "Answer only with the requested JSON.")

JUDGE_PROMPT = """Evaluate one answer given to a coffee grower. Do ALL of the following and return ONE JSON object.

QUESTION: {question}
REFERENCE ANSWER (from the agronomy documents; may be empty for questions outside the documents): {gold}
ANSWER TO EVALUATE:
<answer>
{answer}
</answer>
RETRIEVED CONTEXT given to the system ({n_ctx} chunks; none means the system had no documents):
{chunks}

1. "claims": split the ANSWER into short, self-contained factual claims (ignore headings, greetings and generic
   advice such as "consult an expert"; at most 20). For each claim give "supported": 1 if it can be directly
   inferred from the RETRIEVED CONTEXT, else 0 (always 0 when there is no context).
2. "generated_questions": write 3 different questions that the ANSWER answers, in the same language as the answer.
   "noncommittal": 1 if the answer is evasive or vague, else 0.
3. "context_verdicts": for each retrieved chunk, in order, 1 if it is useful for arriving at the REFERENCE ANSWER,
   else 0 (an empty list when there is no context).
4. Compare the ANSWER with the REFERENCE ANSWER as short statements: "tp" = answer statements supported by the
   reference, "fp" = answer statements not supported by the reference, "fn" = reference statements missing from
   the answer (empty lists when the reference is empty).
5. "abstained": 1 if the answer clearly says it does not know or that the information is not in its sources,
   instead of answering; else 0.

Return JSON: {{"claims": [{{"text": "...", "supported": 0}}], "generated_questions": ["..."], "noncommittal": 0,
"context_verdicts": [0], "tp": ["..."], "fp": ["..."], "fn": ["..."], "abstained": 0}}"""


def judge_answer(judge, embedder, question: str, gold_answer: str, answer: str, contexts: list[str],
                 has_context: bool = True) -> dict:
    """All judge metrics from ONE judge call (keeps free-tier usage low), computed with the RAGAS definitions:
    faithfulness       = supported claims / claims (0 without context)
    answer_relevancy   = mean cosine similarity between the question and 3 questions generated from the answer
                         (0 if noncommittal); embeddings from the local multilingual embedder
    context_precision  = mean over relevant ranks k of precision@k of the context verdicts (NaN without context)
    answer_correctness = 0.75 x factual F1 (tp / (tp + 0.5 (fp + fn))) + 0.25 x answer-reference similarity
    abstained          = 1 if the answer declines to answer"""
    chunks = "\n".join(f"<chunk {i + 1}>{c}</chunk>" for i, c in enumerate(contexts)) if contexts else "(none)"
    d, _ = judge.generate_json(JUDGE_PROMPT.format(question=question, gold=gold_answer or "(empty)", answer=answer,
                                                   n_ctx=len(contexts), chunks=chunks), JUDGE_SYSTEM,
                               max_tokens=2500)
    out = {}
    claims = [c for c in d.get("claims", []) if isinstance(c, dict) and str(c.get("text", "")).strip()][:20]
    if claims:
        sup = [int(bool(c.get("supported", 0))) if has_context and contexts else 0 for c in claims]
        out["faithfulness"], out["claims"] = float(np.mean(sup)), len(claims)
    else:
        out["faithfulness"], out["claims"] = float("nan"), 0
    qs = [q for q in d.get("generated_questions", []) if isinstance(q, str) and q.strip()][:3]
    if qs and not int(d.get("noncommittal", 0) or 0):
        e = embedder.encode([question] + qs, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)
        out["answer_relevancy"] = float(np.clip((e[1:] @ e[0]).mean(), 0, 1))
    else:
        out["answer_relevancy"] = 0.0
    if contexts:
        v = [int(bool(x)) for x in (d.get("context_verdicts") or [])][:len(contexts)]
        v += [0] * (len(contexts) - len(v))
        prec = [sum(v[:k + 1]) / (k + 1) for k in range(len(v)) if v[k]]
        out["context_precision"] = float(np.mean(prec)) if prec else 0.0
    else:
        out["context_precision"] = float("nan")
    if gold_answer:
        tp, fp, fn = (len(d.get(k) or []) for k in ("tp", "fp", "fn"))
        f1 = tp / (tp + 0.5 * (fp + fn)) if tp else 0.0
        e = embedder.encode([gold_answer, answer], normalize_embeddings=True, convert_to_numpy=True,
                            show_progress_bar=False)
        out["answer_correctness"] = 0.75 * f1 + 0.25 * float(np.clip(e[0] @ e[1], 0, 1))
    else:
        out["answer_correctness"] = float("nan")
    out["abstained"] = int(bool(d.get("abstained", 0)))
    return out


# --------------------------------------------------------------------------- Selva Kumar et al. baseline
SK_PROMPT = ("Use the following pieces of context to answer the question at the end. If you don't know the answer, "
             "just say that you don't know, don't try to make up an answer.\n\n{context}\n\nQuestion: {question}\n"
             "Helpful Answer:")  # LangChain's default "stuff" QA prompt, used by its conversational retrieval chain


class SKRetriever:
    """LangChain pipeline as described by Selva Kumar et al.: PDF text -> RecursiveCharacterTextSplitter
    (1000/200, LangChain defaults) -> embeddings -> FAISS -> top-4 similarity search.
    Page text comes from PyMuPDF (same extractor as PlantIQ) so both systems see identical text."""

    def __init__(self, embedding_spec: str, kb_dir: Path, cache_dir: Path, device: str = "cuda"):
        from langchain_community.document_loaders import PyMuPDFLoader
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        self.embedding_spec = embedding_spec
        emb = self._embeddings(embedding_spec, device)
        docs = []
        for pdf in sorted(kb_dir.glob("*.pdf")):
            docs += PyMuPDFLoader(str(pdf)).load()
        self.chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200).split_documents(docs)
        key = hashlib.sha256((embedding_spec + "|" + "|".join(sorted(p.name for p in kb_dir.glob("*.pdf"))))
                             .encode()).hexdigest()[:12]
        store_dir = cache_dir / f"sk_faiss_{key}"
        if (store_dir / "index.faiss").exists():
            self.store = FAISS.load_local(str(store_dir), emb, allow_dangerous_deserialization=True)
        else:
            self.store = FAISS.from_documents(self.chunks, emb)
            self.store.save_local(str(store_dir))

    @staticmethod
    def _embeddings(spec: str, device: str):
        provider, model = spec.split(":", 1)
        if provider == "openai":
            from langchain_openai import OpenAIEmbeddings

            return OpenAIEmbeddings(model=model)
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=model, model_kwargs={"device": device},
                                     encode_kwargs={"normalize_embeddings": True})

    def search(self, query: str, k: int = 4) -> list[dict]:
        hits = self.store.similarity_search(query, k=k)
        return [{"text": h.page_content, "source": Path(h.metadata.get("source", "")).name,
                 "page": int(h.metadata.get("page", 0)) + 1} for h in hits]


# --------------------------------------------------------------------------- stats
def bootstrap_mean_ci(x, n_boot=2000, seed=config.SEED) -> dict:
    x = np.asarray([v for v in x if v == v], dtype=float)
    if not len(x):
        return {"mean": float("nan"), "lo": float("nan"), "hi": float("nan"), "n": 0}
    rng = np.random.default_rng(seed)
    means = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(n_boot)]
    lo, hi = np.percentile(means, [2.5, 97.5])
    return {"mean": float(x.mean()), "lo": float(lo), "hi": float(hi), "n": int(len(x))}


def wilcoxon_paired(a, b) -> float:
    from scipy.stats import wilcoxon

    a, b = np.asarray(a, float), np.asarray(b, float)
    m = ~(np.isnan(a) | np.isnan(b))
    if m.sum() < 5 or np.allclose(a[m], b[m]):
        return float("nan")
    return float(wilcoxon(a[m], b[m]).pvalue)

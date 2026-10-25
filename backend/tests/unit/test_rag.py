import numpy as np
import pytest

from app.services.fakes import FAKE_CHUNKS
from app.services.rag.chunking import chunk_page, detect_topic, pretty_source, split_sentences
from app.services.rag.profiles import BALANCED, QUALITY, choose_profile, profile_for_embedder
from app.services.rag.query import audit_dosages, expand_query
from app.services.rag.retriever import HybridRetriever, jaccard, mmr_select, rrf_fuse, sigmoid, tokenize

pytestmark = pytest.mark.unit


def test_rrf_formula_and_missing_rank():
    fused = rrf_fuse([{1: 1, 2: 2}, {2: 1, 3: 2}])
    assert fused[2] == pytest.approx(1 / 62 + 1 / 61)
    assert fused[1] == pytest.approx(1 / 61 + 1 / 1060)
    assert max(fused, key=fused.get) == 2


def test_sigmoid_bounds_and_stability():
    assert sigmoid(0) == 0.5
    assert 0 <= sigmoid(-1000) < 1e-10 and sigmoid(1000) == 1.0  # no OverflowError


def test_mmr_drops_near_duplicates():
    cands = [
        {"text": "bordeaux mixture rust spray 200 l", "score": 0.95},
        {"text": "bordeaux mixture rust spray 200 l barrel", "score": 0.94},
        {"text": "shade lopping canopy drainage", "score": 0.80},
    ]
    picked = mmr_select(cands, 2, lambda_=0.5)
    assert [p["score"] for p in picked] == [0.95, 0.80]
    assert "_tok" not in picked[0]


def test_tokenize_and_jaccard():
    assert tokenize("Coffee rust, a 0.5% spray!") == ["coffee", "rust", "spray"]
    assert jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
    assert jaccard(set(), {"a"}) == 0


def test_sentence_split_protects_abbreviations_and_decimals():
    s = split_sentences("Use 0.5% Bordeaux, e.g. copper 50 WP. at 2 g per litre. Spray in May. Repeat in Sep.")
    assert s[0].startswith("Use 0.5% Bordeaux, e.g. copper 50 WP. at 2 g per litre.")
    assert s[-1] == "Repeat in Sep."


@pytest.mark.parametrize("text,topic", [
    ("Hemileia vastatrix pustules", "leaf_rust"), ("brown eye spot coffeicola", "cercospora_leaf_spot"),
    ("Leucoptera serpentine mines", "leaf_miner"), ("phoma tip blight", "phoma_blight"),
    ("apply urea and potash", "nutrition_fertilizer"), ("silver oak shade lopping", "cultural_shade_management"),
    ("history of coffee in india", "coffee_agronomy"),
])
def test_topic_detection(text, topic):
    assert detect_topic("doc.pdf", text) == topic


def test_chunk_page_sections_and_overlap():
    words = " ".join(f"Sentence {i} talks about coffee rust control with copper sprays." for i in range(80))
    page = f"LEAF RUST MANAGEMENT\n{words}\nShade Regulation:\nRegulate shade before monsoon. " * 1
    chunks = chunk_page(page, "Coffee_Diseases.pdf", 4)
    assert len(chunks) >= 3
    assert chunks[0]["section"] == "LEAF RUST MANAGEMENT" and chunks[0]["topic"] == "leaf_rust"
    assert all(c["text"].startswith("[") for c in chunks)
    first_tail = chunks[0]["text"].split()[-5:]
    assert " ".join(first_tail) in chunks[1]["text"]  # overlap carried over


def test_pretty_source():
    assert pretty_source("Coffee_Diseases.pdf") == "Coffee Diseases"


def test_expand_query_intents():
    q = expand_query("how much copper per barrel and when to spray?", "Rust", "rust dosage")
    assert q.startswith("coffee Rust rust dosage") and "200L" in q and "monsoon" in q
    assert "control management" in expand_query(None, "Phoma")
    assert "organic" in expand_query("ಸಾವಯವ ಔಷಧಿ ಇದೆಯೇ", "Rust")


def test_dosage_audit():
    docs = [{"text": "Bordeaux mixture 0.5% with 1 kg lime in 200 L water"}]
    ok = audit_dosages("Use 0.5% Bordeaux, 1 kg lime, 200 litres water", docs)
    assert ok["verified"] and not ok["unverified_dosages"]
    bad = audit_dosages("Use 2% Bordeaux and 500 ml", docs)
    assert not bad["verified"] and set(bad["unverified_dosages"]) == {"2%", "500 ml"}
    assert "label" in bad["safety_note"]


def test_profiles(monkeypatch):
    assert choose_profile("balanced") is BALANCED and choose_profile("quality") is QUALITY
    monkeypatch.setattr("app.services.rag.profiles.gpu_memory_gb", lambda: 2.0)
    assert choose_profile("auto") is BALANCED
    monkeypatch.setattr("app.services.rag.profiles.gpu_memory_gb", lambda: 8.0)
    monkeypatch.setattr("app.services.rag.profiles.settings.ML_DEVICE", "auto")
    assert choose_profile("auto") is QUALITY
    assert profile_for_embedder("BAAI/bge-m3") is QUALITY and profile_for_embedder("x").name == "custom"


class BagOfWordsEmbedder:
    """Deterministic toy embedder so the real HybridRetriever code path can be tested without models."""

    def __init__(self, vocab):
        self.vocab = {w: i for i, w in enumerate(sorted(vocab))}

    def encode(self, texts, **_):
        out = np.zeros((len(texts), len(self.vocab)), dtype=np.float32)
        for r, t in enumerate(texts):
            for w in tokenize(t):
                if w in self.vocab:
                    out[r, self.vocab[w]] += 1
        norms = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.where(norms == 0, 1, norms)


@pytest.fixture
def retriever():
    import faiss

    vocab = {w for c in FAKE_CHUNKS for w in tokenize(c["text"])}
    emb = BagOfWordsEmbedder(vocab)
    vecs = emb.encode([c["text"] for c in FAKE_CHUNKS])
    index = faiss.IndexFlatIP(vecs.shape[1])
    index.add(vecs)
    return HybridRetriever(index, FAKE_CHUNKS, emb, None, BALANCED)


def test_hybrid_search_finds_relevant_chunk(retriever):
    res = retriever.search("bordeaux mixture copper sulphate rust", top_k=2)
    assert res[0]["source"] == "Coffee_Diseases.pdf"
    assert 0 <= res[0]["score"] <= 1 and res[0]["metadata"]["page"] == 4


def test_topic_filter_and_relaxation(retriever):
    res = retriever.search("shade and nutrition", top_k=2, topic_filter="leaf_miner")
    assert res[0]["metadata"]["topic"] == "leaf_miner"
    assert len(res) == 2  # relaxed to fill top_k


def test_search_cache_and_empty(retriever):
    a = retriever.search("leaf miner dry weather", top_k=1)
    b = retriever.search("leaf miner dry weather", top_k=1)
    assert a == b and a is not b
    assert retriever.search("   ") == []
    assert retriever.info()["chunks"] == len(FAKE_CHUNKS)

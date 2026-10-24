"""Semantic section chunking for agronomy PDFs (port of the original ingestion with fixes).

- headings detected per line (caps, numbered, "Title Case:", agronomy keywords)
- ~225-word chunks with ~38-word sentence overlap
- abbreviation-safe sentence splitting (a.i., e.g., WP., pH. ...)
- each chunk tagged with a topic and prefixed with a contextual header for better retrieval
"""
from __future__ import annotations

import re

AGRI_ABBREVIATIONS = [
    "e.g.", "i.e.", "a.i.", "sp.", "spp.", "var.", "cf.", "wp.", "ec.", "sc.", "sl.", "wg.", "ph.", "approx.",
    "vs.", "fig.", "tab.", "no.", "vol.", "ha.", "kg.", "gm.", "ml.", "ppm.", "wt.", "etc.", "dr.", "viz.",
]
_ABBR_RE = re.compile(r"\b(" + "|".join(re.escape(a) for a in AGRI_ABBREVIATIONS) + r")", re.IGNORECASE)
_HEADING_KEYWORDS = (
    "management", "control", "symptoms", "dosage", "fungicide", "treatment", "biology", "distribution",
    "epidemiology", "chemical", "organic", "shade", "spray schedule", "cultural practices", "introduction",
    "conclusion", "nutrition", "fertilizer",
)
TOPIC_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("leaf_rust", ("rust", "hemileia", "pustule", "clr")),
    ("cercospora_leaf_spot", ("cercospora", "leaf spot", "brown eye", "berry blotch", "coffeicola")),
    ("leaf_miner", ("miner", "leucoptera", "serpentine", "blotch mine")),
    ("phoma_blight", ("phoma", "costaricensis", "costarricensis", "dieback", "tip blight", "stem blight")),
    ("anthracnose_black_rot", ("anthracnose", "colletotrichum", "black rot", "koleroga", "pellicularia")),
    ("nutrition_fertilizer", ("fertilizer", "fertiliser", "nutrient", "organomineral", "npk", "urea", "potash", "zinc",
                              "boron", "dolomite", "acidity")),
    ("pest_management", ("borer", "white stem borer", "shot hole", "mealybug", "scale insect", "arthropod", "pest")),
    ("cultural_shade_management", ("cultivation", "shade", "pruning", "dadap", "silver oak", "lopping", "two-tier",
                                   "drainage")),
]
DISEASE_TOPIC = {"Rust": "leaf_rust", "Cerscospora": "cercospora_leaf_spot", "Miner": "leaf_miner", "Phoma": "phoma_blight"}


def detect_topic(source: str, text: str) -> str:
    combined = f"{source} {text[:800]}".lower()
    for topic, keys in TOPIC_RULES:
        if any(k in combined for k in keys):
            return topic
    return "coffee_agronomy"


def clean_text(text: str) -> str:
    text = re.sub(r"[^\x20-\x7Eಀ-೿]", " ", text)  # keep printable ASCII + Kannada
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    protected = _ABBR_RE.sub(lambda m: m.group(0).replace(".", "§"), text)
    # protect decimals such as 0.5% or 6.2
    protected = re.sub(r"(\d)\.(\d)", r"\1§\2", protected)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9ಀ-೿(\"'])", protected)
    return [p.replace("§", ".").strip() for p in parts if p.strip()]


def _is_heading(line: str) -> bool:
    if len(line) >= 80 or len(line) < 3:
        return False
    letters = [c for c in line if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.8 and len(letters) > 3:
        return True
    if re.match(r"^(\d+(\.\d+)*[.)]?\s+[A-Z]|#+\s|[A-Z][a-z]+(\s+[A-Z][a-z]+)*:$)", line):
        return True
    low = line.lower()
    return len(line.split()) <= 8 and any(k in low for k in _HEADING_KEYWORDS) and not line.endswith(".")


def chunk_page(text: str, source: str, page: int, target_words: int = 225, overlap_words: int = 38) -> list[dict]:
    sections: list[tuple[str, list[str]]] = []
    current_title, buffer = "General", []
    for raw in text.split("\n"):
        line = raw.strip()
        if not line:
            continue
        if _is_heading(line) and buffer:
            sections.append((current_title, buffer))
            current_title, buffer = line[:80], []
        elif _is_heading(line):
            current_title = line[:80]
        else:
            buffer.append(line)
    if buffer:
        sections.append((current_title, buffer))

    chunks: list[dict] = []
    for title, lines in sections:
        body = clean_text(" ".join(lines))
        if len(body) < 60:
            continue
        sentences = split_sentences(body)
        current: list[str] = []
        count = 0
        for sent in sentences:
            words = len(sent.split())
            if current and count + words > target_words:
                chunks.append(_make_chunk(current, title, source, page))
                keep: list[str] = []
                kept = 0
                for s in reversed(current):
                    w = len(s.split())
                    if kept + w > overlap_words:
                        break
                    keep.insert(0, s)
                    kept += w
                current, count = keep + [sent], kept + words
            else:
                current.append(sent)
                count += words
        if current:
            chunks.append(_make_chunk(current, title, source, page))
    return chunks


def _make_chunk(sentences: list[str], title: str, source: str, page: int) -> dict:
    body = " ".join(sentences)
    return {
        "text": f"[{title}] {body}",
        "source": source,
        "page": page,
        "section": title,
        "topic": detect_topic(source, f"{title} {body}"),
    }


def pretty_source(filename: str) -> str:
    name = re.sub(r"\.pdf$", "", filename, flags=re.IGNORECASE)
    name = re.sub(r"[_]+", " ", name).strip()
    return name[:80]

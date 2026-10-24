"""Query intent expansion and post-generation dosage safety audit (ported from the original RAG service)."""
from __future__ import annotations

import re

_INTENTS: list[tuple[tuple[str, ...], str]] = [
    (("when", "month", "schedule", "monsoon", "timing", "calendar", "time", "season", "stage", "ಯಾವಾಗ", "ಸಮಯ"),
     "spray schedule calendar timing pre-monsoon post-monsoon application stage"),
    (("how much", "dose", "dosage", "quantity", "ratio", "barrel", "concentration", "liter", "litre", "gram", "mix",
      "copper", "bordeaux", "fungicide", "chemical", "ಎಷ್ಟು", "ಔಷಧ"),
     "chemical fungicide dosage concentration per barrel 200L grams active ingredient dilution"),
    (("organic", "natural", "bio", "neem", "trichoderma", "herbal", "ಸಾವಯವ"),
     "organic biological control bio-agents cultural practices trichoderma neem pseudomonas"),
    (("shade", "tree", "lopping", "pruning", "canopy", "spacing", "drainage", "sunlight", "ನೆರಳು"),
     "shade regulation lopping canopy pruning spacing drainage aeration"),
    (("fertilizer", "fertiliser", "nutrition", "deficiency", "npk", "urea", "zinc", "boron", "manure", "ಗೊಬ್ಬರ"),
     "fertilizer nutrient foliar spray urea potash zinc boron dolomite soil"),
]
_DEFAULT_EXPANSION = "control management treatment dosage fungicide spray schedule"


def expand_query(question: str | None, disease: str, routed: str = "") -> str:
    q = (question or "").lower()
    parts = [f"coffee {disease}"]
    if routed:
        parts.append(routed)
    matched = [exp for keys, exp in _INTENTS if any(k in q for k in keys)]
    parts.extend(matched or [_DEFAULT_EXPANSION])
    return " ".join(parts)


_DOSE_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:%|(?:kg|g|gm|grams?|ml|l|liters?|litres?|ppm)\b)", re.IGNORECASE)


def _norm(d: str) -> str:
    d = d.lower().replace(" ", "")
    return re.sub(r"(grams?|gm)$", "g", re.sub(r"(liters?|litres?)$", "l", d))


def audit_dosages(text: str, docs: list[dict]) -> dict:
    found = list(dict.fromkeys(m.group(0).strip() for m in _DOSE_RE.finditer(text or "")))
    corpus = re.sub(r"\s+", "", " ".join(d.get("text", "") for d in docs).lower())
    corpus = re.sub(r"(liters?|litres?)", "l", re.sub(r"(grams?|gm)\b", "g", corpus))
    unverified = [d for d in found if _norm(d) not in corpus]
    ok = not unverified
    return {
        "verified": ok,
        "detected_dosages": found,
        "unverified_dosages": unverified,
        "safety_note": "All doses match the reference documents." if ok
        else f"Check the label or your extension officer before mixing: {', '.join(unverified)}.",
    }

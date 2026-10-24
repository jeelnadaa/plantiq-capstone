"""Deterministic stand-ins for the ML services (PLANTIQ_FAKE_ML=1 and tests)."""
from __future__ import annotations

import hashlib
import json

from app.services.cnn import CLASSES
from app.services.llm import LLMResult
from app.services.rag.retriever import mmr_select, tokenize

FAKE_CHUNKS = [
    {"id": 0, "text": "[Leaf rust management] Spray Bordeaux mixture 0.5% (1 kg copper sulphate and 1 kg lime in 200 L water) "
     "before and after the monsoon. Cover the underside of leaves.", "source": "Coffee_Diseases.pdf", "page": 4,
     "section": "Leaf rust management", "topic": "leaf_rust"},
    {"id": 1, "text": "[Cercospora] Brown eye spot is severe on plants under stress and poor shade. Maintain shade and "
     "balanced nutrition; Bordeaux mixture 0.5% gives protection.", "source": "cercospora.pdf", "page": 2,
     "section": "Cercospora", "topic": "cercospora_leaf_spot"},
    {"id": 2, "text": "[Leaf miner] Leucoptera mines are common in dry weather. Regulate shade and conserve parasitoids.",
     "source": "A_Comprehensive_Review_of_the_Coffee_Leaf_Miner_Le.pdf", "page": 6, "section": "Leaf miner",
     "topic": "leaf_miner"},
    {"id": 3, "text": "[Phoma] Phoma leaf spot and tip blight occur in cool wet windy weather at high elevations; "
     "protect young flush with copper fungicide.", "source": "Coffee.pdf", "page": 11, "section": "Phoma",
     "topic": "phoma_blight"},
    {"id": 4, "text": "[Nutrition] Apply NPK in split doses before and after the monsoon; correct soil acidity with dolomite.",
     "source": "Nutrients_Status_in_Arabica_Coffee_Coffea_Arabica_.pdf", "page": 3, "section": "Nutrition",
     "topic": "nutrition_fertilizer"},
    {"id": 5, "text": "[Weather and disease] High humidity above 80% with temperatures of 20-28 C favour rust spore "
     "germination; spray in dry windows.", "source": "Strategies_for_Coffee_Leaf_Rust_Management_in_Orga.pdf",
     "page": 7, "section": "Weather and disease", "topic": "leaf_rust"},
]


class FakeCNN:
    device = "cpu"

    def predict(self, image_bytes: bytes) -> dict:
        h = hashlib.sha256(image_bytes).digest()
        top = h[0] % len(CLASSES)
        conf = 70.0 + (h[1] % 30)  # 70..99
        rest = (100.0 - conf) / (len(CLASSES) - 1)
        dist = {c: round(conf if i == top else rest, 2) for i, c in enumerate(CLASSES)}
        return {"class": CLASSES[top], "confidence": round(conf, 2), "distribution": dist}


class FakeRetriever:
    device = "cpu"
    chunks = FAKE_CHUNKS

    def info(self) -> dict:
        return {"profile": "fake", "embedder": "fake", "reranker": None, "chunks": len(FAKE_CHUNKS), "device": "cpu"}

    def search(self, query: str, top_k: int = 3, topic_filter: str | None = None) -> list[dict]:
        q = set(tokenize(query))
        if not q:
            return []
        scored = []
        for c in FAKE_CHUNKS:
            overlap = len(q & set(tokenize(c["text"])))
            score = min(0.99, 0.35 + 0.08 * overlap + (0.2 if topic_filter and c["topic"] == topic_filter else 0))
            scored.append({"id": c["id"], "text": c["text"], "source": c["source"], "score": round(score, 4),
                           "metadata": {"page": c["page"], "section": c["section"], "topic": c["topic"]}})
        scored.sort(key=lambda r: r["score"], reverse=True)
        return mmr_select(scored, top_k)


class FakeLLM:
    available = True

    def __init__(self) -> None:
        self.calls: list[str] = []

    def providers(self) -> list[str]:
        return ["fake"]

    def generate(self, prompt: str, *, system: str = "", temperature: float = 0.2, max_tokens: int = 900,
                 json_mode: bool = False) -> LLMResult:
        self.calls.append(prompt)
        if json_mode:
            kannada = any("ಀ" <= ch <= "೿" for ch in prompt)
            return LLMResult(json.dumps({
                "detected_script": "kannada_script" if kannada else "english",
                "search_query_english": "coffee rust spray timing",
                "is_greeting_or_location_only": False,
                "target_response_language": "kn" if kannada else "en",
            }), "fake", "fake-llm")
        kn = "Kannada script" in prompt
        body = ("## ಇಂದು ಮಾಡಿ\n- ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆಯಿರಿ.\n## ಸಿಂಪಡಣೆ\n- 0.5% ಬೋರ್ಡೋ ಮಿಶ್ರಣ, 200 L ನೀರಿಗೆ 1 kg ಮೈಲುತುತ್ತ.\n"
                if kn else
                "## Do today\n- Remove badly infected leaves.\n## Spray\n- Bordeaux mixture 0.5% (1 kg copper sulphate "
                "and 1 kg lime in 200 L water).\n## Timing\n- Spray in the next dry window.\n## Prevent\n- Keep shade balanced.\n")
        return LLMResult(body + "\nSource: Coffee_Diseases.pdf", "fake", "fake-llm")

    def transcribe_groq(self, audio: bytes, filename: str, lang: str) -> str:
        return "ಕಾಫಿ ತುಕ್ಕು ರೋಗ" if lang == "kn" else "when should I spray for rust"

    def transcribe_gemini(self, audio: bytes, mime: str, lang: str) -> str:
        return self.transcribe_groq(audio, "x", lang)


class FakeSTT:
    def status(self) -> dict:
        return {"local_kannada": False, "local_english": False, "groq": False, "gemini": False, "ffmpeg": False, "fake": True}

    def transcribe(self, audio: bytes, filename: str, lang: str, kind: str = "webm") -> dict:
        lang = "kn" if lang == "kn" else "en"
        text = "ಕಾಫಿ ಎಲೆಗೆ ಯಾವ ಔಷಧಿ ಸಿಂಪಡಿಸಬೇಕು?" if lang == "kn" else "When should I spray for leaf rust?"
        return {"text": text, "language": lang, "provider": "fake", "model": "fake", "device": "cpu"}

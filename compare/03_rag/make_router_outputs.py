"""Writes 03_rag/answers/router_outputs.jsonl: PlantIQ's language-router output for every benchmark question.

The router (plantiq_rag_snapshot/lang_router.py, backend commit b421009) asks an LLM to rewrite the farmer's text as
ONE short, self-contained English question (translate the meaning; keep crop, disease, pest, negations, quantities,
timing and question type). In this benchmark the LLM steps are performed by Claude Opus 5.5 (see README), so these
outputs are the answers to that router prompt, one per question. English questions are already self-contained English
questions and are passed through unchanged. The notebooks read this file through `rag_eval.FileRouter`, so retrieval
needs no API.

Run:  .venv\\Scripts\\python 03_rag\\make_router_outputs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import config  # noqa: E402

KANNADA_TO_ENGLISH = {
    "r01_kn": "When and at what concentration should the pre-monsoon Bordeaux mixture be sprayed against coffee leaf rust?",
    "r02_kn": "For controlling coffee leaf rust, should Bordeaux mixture be sprayed on the upper side or the lower side of the leaf?",
    "r06_kn": "If the blossom shower came late and there are no new shoots, what should be sprayed against coffee leaf rust instead of Bordeaux mixture?",
    "r09_kn": "My coffee estate is above 3500 feet; should I worry about coffee leaf rust in February-March?",
    "c01_kn": "How can coffee nursery seedlings be protected from Cercospora (brown eye spot) disease?",
    "c02_kn": "Which coffee plants are more likely to get Cercospora leaf spot disease?",
    "c05_kn": "Which eco-friendly treatment is most effective against Cercospora leaf spot of coffee?",
    "m01_kn": "How does the coffee leaf miner damage coffee leaves?",
    "m03_kn": "What does the larva of the coffee leaf miner look like?",
    "m06_kn": "What sustainable methods are there to control the coffee leaf miner?",
    "p01_kn": "When do coffee white stem borer beetles come out?",
    "p02_kn": "What should be done with coffee plants infested by white stem borer?",
    "p05_kn": "Which shade tree increases black rot disease and white stem borer in coffee?",
    "p08_kn": "Is there a biological control method for the coffee berry borer?",
    "k01_kn": "What should the pH of coffee soil be?",
    "k03_kn": "What is the best time to apply lime to coffee soil?",
    "k06_kn": "When should coffee plants be pruned after the harvest?",
    "k07_kn": "What is the basic fertilizer dose for grown-up coffee plants?",
    "k09_kn": "When should the branches of shade trees be lopped in a coffee estate?",
    "k12_kn": "How should young coffee plants be watered after the monsoon ends?",
    "k15_kn": "What soil mixture should be filled in coffee nursery bags?",
}

if __name__ == "__main__":
    qs = json.loads((config.RAG_DIR / "questions_curated.json").read_text(encoding="utf-8"))
    out_dir = config.RAG_DIR / "answers"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for q in qs:
        kn = q["lang"] == "kn"
        if kn and q["id"] not in KANNADA_TO_ENGLISH:
            raise SystemExit(f"no router output for {q['id']}")
        rows.append({"id": q["id"], "question": q["question"],
                     "router_output": {"detected_script": "kannada_script" if kn else "english",
                                       "search_query_english": KANNADA_TO_ENGLISH[q["id"]] if kn else q["question"],
                                       "is_greeting_or_location_only": False,
                                       "target_response_language": "kn" if kn else "en"},
                     "router": "claude-opus-5-5"})
    with (out_dir / "router_outputs.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote router_outputs.jsonl ({len(rows)} questions, {sum(q['lang'] == 'kn' for q in qs)} Kannada)")

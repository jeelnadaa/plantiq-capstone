"""Print one batch of generation prompts (as each system's LLM sees them) or, with --gold, the material for judging.

    python 03_rag/show_batch.py 0          # prompts of questions 0-5 (no gold answers shown)
    python 03_rag/show_batch.py 0 --gold   # gold answer + evidence + saved answers + contexts, for scoring
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent
SIZE = 6
inp = [json.loads(l) for l in (D / "answers" / "generation_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l]
qs = {q["id"]: q for q in json.loads((D / "questions_curated.json").read_text(encoding="utf-8")) if q["lang"] == "en"}
ids = list(dict.fromkeys(r["id"] for r in inp))
b = int(sys.argv[1])
gold = "--gold" in sys.argv
ans = {}
if gold and (D / "answers" / "answers.jsonl").exists():
    ans = {json.loads(l)["key"]: json.loads(l)["answer"] for l in (D / "answers" / "answers.jsonl").read_text(encoding="utf-8").splitlines() if l}
for qid in ids[b * SIZE:(b + 1) * SIZE]:
    q = qs[qid]
    print(f"\n################ {qid} [{q['topic']}] {q['question']}")
    if gold:
        print(f"GOLD: {q['gold_answer']}\nEVIDENCE: {' | '.join(q['evidence'])}")
    for r in (x for x in inp if x["id"] == qid):
        print(f"\n--- {r['system']}" + (f" (blended={r.get('blended')})" if r["system"] == "PQ" else ""))
        if gold:
            print("ANSWER:", ans.get(r["key"], "<missing>"))
        for i, c in enumerate(r["contexts"], 1):
            print(f"  [{i}] {' '.join(c.split())}")
print(f"\n(batch {b}: questions {b * SIZE}-{min(len(ids), (b + 1) * SIZE) - 1} of {len(ids)})")

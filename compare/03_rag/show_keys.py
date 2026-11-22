"""Print given prompts (question + retrieved passages) without gold answers: python 03_rag/show_keys.py r02|PQ r03|PQ ..."""
import json, sys
from pathlib import Path
D = Path(__file__).resolve().parent
inp = {json.loads(l)["key"]: json.loads(l) for l in (D / "answers" / "generation_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l}
qs = {q["id"]: q for q in json.loads((D / "questions_curated.json").read_text(encoding="utf-8")) if q["lang"] == "en"}
for k in sys.argv[1:]:
    r = inp[k]
    print(f"\n######## {k} [{qs[r['id']]['topic']}] {qs[r['id']]['question']}" + (f" (blended={r.get('blended')})" if r["system"] == "PQ" else ""))
    for i, c in enumerate(r["contexts"], 1):
        print(f"  [{i}] {' '.join(c.split())}")

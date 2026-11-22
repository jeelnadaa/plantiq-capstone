"""Append answers or judgments to 03_rag/answers/{answers,judgments}.jsonl (replacing existing keys).

    python 03_rag/add_answers.py answers   path/to/batch.json    # {"r01|L0": "answer text", ...}
    python 03_rag/add_answers.py judgments path/to/batch.json    # {"r01|L0": {"claims":4,"supported":3,"correct":1,"relevant":1,"note":""}}
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent / "answers"
MODEL = "claude-opus-5-5"
kind, src = sys.argv[1], Path(sys.argv[2])
out = D / f"{kind}.jsonl"
rows = {}
if out.exists():
    for line in out.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r["key"]] = r
for key, val in json.loads(src.read_text(encoding="utf-8")).items():
    if kind == "answers":
        rows[key] = {"key": key, "answer": val, "generator": MODEL}
    else:
        rows[key] = {"key": key, **val, "judge": MODEL}
inp = [json.loads(l)["key"] for l in (D / "generation_inputs.jsonl").read_text(encoding="utf-8").splitlines() if l]
order = {k: i for i, k in enumerate(inp)}
with out.open("w", encoding="utf-8") as f:
    for k in sorted(rows, key=lambda k: order.get(k, 1e9)):
        f.write(json.dumps(rows[k], ensure_ascii=False) + "\n")
print(f"{out.name}: {len(rows)} of {len(inp)} prompts")

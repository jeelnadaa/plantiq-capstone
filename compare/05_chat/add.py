"""Add LLM-step outputs to 05_chat/answers/ (replacing existing keys).

    python 05_chat/add.py answers   batch.json   # {"mem01|t0|PQ": "answer text", ...}
    python 05_chat/add.py condensed batch.json   # {"mem01|t1": "standalone question", ...}
    python 05_chat/add.py judgments batch.json   # {"mem01|t1|PQ": {"claims":3,"supported":3,"correct":1,"task_ok":1,"note":""}}
"""
import json
import sys
from pathlib import Path

D = Path(__file__).resolve().parent / "answers"
MODEL = "claude-opus-5-5"
kind, src = sys.argv[1], Path(sys.argv[2])
name = {"answers": "answers.jsonl", "condensed": "sk_condensed.jsonl", "judgments": "judgments.jsonl"}[kind]
out = D / name
rows = {}
if out.exists():
    for line in out.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r["key"]] = r
for key, val in json.loads(src.read_text(encoding="utf-8")).items():
    if kind == "answers":
        rows[key] = {"key": key, "answer": val, "generator": MODEL}
    elif kind == "condensed":
        rows[key] = {"key": key, "standalone_question": val, "generator": MODEL}
    else:
        rows[key] = {"key": key, **val, "judge": MODEL}
with out.open("w", encoding="utf-8") as f:
    for k in sorted(rows):
        f.write(json.dumps(rows[k], ensure_ascii=False) + "\n")
print(f"{out.name}: {len(rows)} rows")

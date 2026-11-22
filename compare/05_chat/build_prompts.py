"""Builds every chat turn whose history is available -> answers/chat_inputs.jsonl, and lists the LangChain condense
steps the Selva Kumar chatbot still needs -> answers/sk_condense_requests.jsonl. Run again after adding answers for the
earlier turns (05a does this). Needs the GPU (retrievers, CNN, YOLO)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chat_bench as B  # noqa: E402


def main(models=None):
    m = models or B.Models()
    rows, need = [], []
    for depth in range(max(len(c["turns"]) for c in B.load_cases())):
        r, n = B.build_rows(m, depth)
        rows += r
        need += n
    with (B.ANS / "chat_inputs.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (B.ANS / "sk_condense_requests.jsonl").open("w", encoding="utf-8") as f:
        for r in need:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    have = B.answers()
    todo = [r["key"] for r in rows if r["system"] in ("PQ", "SK") and r["key"] not in have]
    print(f"{len(rows)} turn rows ({sum(r['system'] == 'PQ' for r in rows)} PQ, {sum(r['system'] == 'SK' for r in rows)} SK), "
          f"{len(need)} condense steps pending, {len(todo)} answers missing")
    return m


if __name__ == "__main__":
    main()

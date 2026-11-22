"""Print pending prompts (as each chatbot's LLM sees them) or, with --judge, the material for scoring.

    python 05_chat/show.py prompts 0          # batch 0 of prompts that have no answer yet
    python 05_chat/show.py condense           # pending LangChain condense steps (Selva Kumar chatbot)
    python 05_chat/show.py judge 0            # batch 0 of scored turns: expectation, gold, answers, contexts
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chat_bench as B  # noqa: E402

SIZE = 8
mode = sys.argv[1]
b = int(sys.argv[2]) if len(sys.argv) > 2 else 0
rows = B.read_jsonl(B.ANS / "chat_inputs.jsonl")
ans = B.answers()
cases = {c["id"]: c for c in B.load_cases()}
if mode == "condense":
    for r in B.read_jsonl(B.ANS / "sk_condense_requests.jsonl"):
        print(f"\n######## {r['key']}\n{r['prompt']}")
elif mode == "prompts":
    todo = [r for r in rows if r["system"] in ("PQ", "SK") and r["key"] not in ans]
    for r in todo[b * SIZE:(b + 1) * SIZE]:
        print(f"\n######## {r['key']}")
        if r["system_prompt"]:
            print("[system prompt: PlantIQ SYSTEM_PROMPT]")
        if r["system"] == "PQ":
            body = r["prompt"].split(chr(10) + "Rules:")[0]
            rule6 = [l for l in r["prompt"].splitlines() if l.startswith("6. ")]
            print(body + (chr(10) + "[+ " + rule6[0] + "]" if rule6 else ""))
        else:
            for i, c in enumerate(r["contexts"], 1):
                junk = sum(ch.isalnum() for ch in c) / max(1, len(c)) < 0.5
                print(f"  ctx{i}: " + ("[unreadable PDF text]" if junk else " ".join(c.split())[:900]))
            print("  Q: " + r["prompt"].rsplit("Question: ", 1)[1].replace(chr(10) + "Helpful Answer:", ""))
    print(f"\n(batch {b}: {min(len(todo), (b + 1) * SIZE) - b * SIZE} of {len(todo)} pending)")
else:
    scored = [r for r in rows if r["scored"] and r["system"] in ("PQ", "SK")]
    ids = list(dict.fromkeys(r["case"] for r in scored))
    for cid in ids[b * SIZE:(b + 1) * SIZE]:
        c = cases[cid]
        print(f"\n################ {cid} [{c['group']}] EXPECT: {c['expect']}\nGOLD: {c['gold'] or '-'}")
        if len(c["turns"]) > 1:
            print("EARLIER TURN:", c["turns"][0]["message"])
        print("MESSAGE:", c["turns"][-1]["message"])
        for r in (x for x in scored if x["case"] == cid):
            extra = ""
            if r["system"] == "PQ":
                extra = f" env={r['env'] if r['env_available'] else 'n/a'} diag={r['diagnosis']} disease={r['disease']}"
            else:
                extra = f" standalone_q={r.get('standalone_question')!r}"
            print(f"\n--- {r['system']}{extra}\nANSWER: {ans.get(r['key'], '<missing>')}")
            for i, ctx in enumerate(r["contexts"], 1):
                print(f"  [{i}] {' '.join(ctx.split())[:700]}")
    print(f"\n(batch {b}: cases {b * SIZE}-{min(len(ids), (b + 1) * SIZE) - 1} of {len(ids)})")

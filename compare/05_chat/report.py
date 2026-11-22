"""Module 3 results: scores every scored turn and writes results/chat/{chat.json, chat_rows.csv}.

Judge-based (05_chat/answers/judgments.jsonl, one record per scored answer):
    task_ok      the conversation's expected behaviour (cases.json "expect") was met (0/1). Per group:
                 memory = answers the follow-up about the right subject; kannada = answers in Kannada script;
                 photo = uses the diagnosis and gives management; weather = reports the live readings, risk and spray
                 suitability (or says weather is unavailable and asks for a location, inventing nothing);
                 routing = short friendly reply; safety = no leak, no off-topic role.
    correct      0 / 0.5 / 1 against the gold answer (only conversations that have one)
    faithfulness supported claims / claims; supported = stated in what the system was given (passages, and for
                 PlantIQ also the live weather, the photo diagnosis, the past scan and the history)
Automatic (no judge):
    evidence_in_context  a passage given to the LLM contains a gold evidence quote (80 % token rule, as in Module 2)
    kannada_reply        >= 50 % of the reply's letters are Kannada script (cases that need a Kannada reply)
    weather_numbers_ok   the live temperature and humidity appear in the reply (turns with a location; turns without
                         one are judged: say unavailable, ask for a location, invent nothing)
    retrieval_skipped    greeting and place-name turns run no retrieval
    weather_false_pos    non-weather turns that PlantIQ's keyword detector flags as weather questions
    offline_*            PlantIQ with no LLM: reply language, disease named, weather numbers, evidence in the reply
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import chat_bench as B  # noqa: E402
from common import config, env  # noqa: E402
from common import rag_eval as R  # noqa: E402

OUT = config.RESULTS_DIR / "chat"
GROUPS = ["memory", "kannada", "photo", "weather", "routing", "safety"]


def _evidence_hit(contexts: list[str], quotes: list[str]) -> float:
    if not quotes:
        return float("nan")
    return float(R.chunk_relevance(contexts, quotes).any()) if contexts else 0.0


def _wants_kannada(case: dict) -> bool:
    t = case["turns"][-1]
    return t["ui_language"] == "kn" or case["id"].endswith("_lat") or bool(re.search("[ಀ-೿]", t["message"]))


def _weather_ok(reply: str, row: dict, available: bool = True) -> float:
    if available:
        nums = B.numbers(reply)
        env_ = row["env"]
        return float(any(abs(n - env_["temperature"]) < 0.05 for n in nums)
                     and any(abs(n - env_["humidity"]) < 0.05 for n in nums))
    return float(not re.search(r"\d+(?:\.\d+)?\s*(?:°|%|mm\b|km/h)", reply or ""))


def build() -> tuple[pd.DataFrame, dict]:
    cases = {c["id"]: c for c in B.load_cases()}
    rows = B.read_jsonl(B.ANS / "chat_inputs.jsonl")
    ans = B.answers()
    jud = {r["key"]: r for r in B.read_jsonl(B.ANS / "judgments.jsonl")}
    by_key = {r["key"]: r for r in rows}
    recs = []
    for r in rows:
        if not r["scored"]:
            continue
        c = cases[r["case"]]
        reply = ans.get(r["key"]) if r["system"] != "PQoff" else r["offline_reply"]
        pq = by_key[f"{r['case']}|t{r['turn']}|PQ"]
        rec = {"case": r["case"], "group": r["group"], "system": r["system"], "reply": reply,
               "evidence_in_context": _evidence_hit(r["contexts"], c.get("evidence") or []),
               "n_passages": len(r["contexts"])}
        if _wants_kannada(c):
            rec["kannada_reply"] = float(B.kannada_share(reply) >= 0.5)
        if c["group"] == "weather" and pq["env_available"]:
            rec["weather_numbers_ok"] = _weather_ok(reply, pq, True)
        if c["group"] == "photo":
            true = c["true_class"]
            d = r.get("diagnosis") or pq.get("diagnosis")
            if r["system"] != "SK" or r.get("diagnosis"):
                rec["diagnosis_correct"] = float(d["class"] == true) if d else float("nan")
            word = {"Rust": "rust", "Cerscospora": "cercospora", "Miner": "miner", "Phoma": "phoma",
                    "Healthy": "healthy"}[true]
            kn_word = {"Rust": "ತುಕ್ಕು", "Cerscospora": "ಸೆರ್ಕೋಸ್ಪೊರಾ", "Miner": "ಸುರಂಗ", "Phoma": "ಫೋಮಾ",
                       "Healthy": "ಆರೋಗ್ಯ"}[true]
            rec["disease_named"] = float(word in (reply or "").lower() or kn_word in (reply or ""))
        if r["system"] in ("PQ", "PQoff"):
            rec["retrieval_skipped"] = float(not r["contexts"]) if c["group"] == "routing" else float("nan")
            rec["weather_flag"] = float(r["weather_query"])
            rec["latency_s"] = r["latency_s"]
        if r["system"] == "PQoff":
            rec["evidence_in_reply"] = _evidence_hit([reply], c.get("evidence") or [])
        j = jud.get(r["key"])
        if j:
            rec.update(task_ok=float(j["task_ok"]),
                       correct=float(j["correct"]) if j.get("correct") is not None and c.get("gold") else float("nan"),
                       claims=j["claims"], supported=j["supported"],
                       faithfulness=j["supported"] / j["claims"] if j["claims"] else float("nan"),
                       answered=float(j["claims"] > 0) if c.get("gold") else float("nan"), note=j.get("note", ""))
        recs.append(rec)
    df = pd.DataFrame(recs)

    def agg(sub: pd.DataFrame) -> dict:
        out = {"n": int(len(sub))}
        for col in ("task_ok", "correct", "faithfulness", "answered", "evidence_in_context", "kannada_reply",
                    "weather_numbers_ok", "diagnosis_correct", "disease_named", "retrieval_skipped",
                    "evidence_in_reply"):
            if col in sub and sub[col].notna().any():
                out[col] = R.bootstrap_mean_ci(sub[col].dropna().tolist())
        return out

    summary = {"systems": {}, "by_group": {}, "notes": {}}
    for s in ("PQ", "SK", "PQoff"):
        sub = df[df.system == s]
        summary["systems"][s] = agg(sub)
        summary["by_group"][s] = {g: agg(sub[sub.group == g]) for g in GROUPS}
    pq, sk = df[df.system == "PQ"].set_index("case"), df[df.system == "SK"].set_index("case")
    summary["wilcoxon_pq_vs_sk"] = {m: R.wilcoxon_paired(pq[m], sk.loc[pq.index, m])
                                    for m in ("task_ok", "correct", "evidence_in_context")}
    lat = pq["latency_s"]
    summary["latency_without_llm_s"] = {"median": float(lat.median()), "p95": float(lat.quantile(0.95)),
                                        "n": int(len(lat))}
    fp = pq[(pq.group != "weather") & (pq.weather_flag == 1)]
    summary["weather_false_positives"] = {"n": int(len(fp)), "of": int((pq.group != "weather").sum()),
                                          "cases": fp.index.tolist()}
    mem = df[(df.group == "memory")]
    summary["memory"] = {s: {"evidence_in_context": float(mem[mem.system == s].evidence_in_context.mean()),
                             "correct": float(mem[mem.system == s].correct.mean()),
                             "correct_en": float(mem[(mem.system == s) & ~mem.case.isin(["mem08", "mem09", "mem10"])].correct.mean()),
                             "correct_kn": float(mem[(mem.system == s) & mem.case.isin(["mem08", "mem09", "mem10"])].correct.mean())}
                         for s in ("PQ", "SK")}
    summary["meta"] = {"cases": int(len(pq)), "turns": int(sum(len(c["turns"]) for c in cases.values())),
                       "generator_and_judge": "claude-opus-5-5", "weather_recorded":
                           [json.loads(p.read_text(encoding="utf-8"))["_recorded"] for p in
                            sorted((HERE / "data").glob("weather_*.json"))],
                       "run": env.run_meta()}
    return df, summary


if __name__ == "__main__":
    df, summary = build()
    OUT.mkdir(parents=True, exist_ok=True)
    df.drop(columns=["reply"]).to_csv(OUT / "chat_rows.csv", index=False)
    env.write_json(OUT / "chat.json", summary)
    for s in ("PQ", "SK", "PQoff"):
        m = summary["systems"][s]
        print(s, {k: round(v["mean"], 3) for k, v in m.items() if isinstance(v, dict)})
    print("by group task_ok:", {s: {g: round(summary["by_group"][s][g].get("task_ok", {}).get("mean", float("nan")), 2)
                                    for g in GROUPS} for s in ("PQ", "SK")})
    print("wilcoxon", summary["wilcoxon_pq_vs_sk"], "latency", summary["latency_without_llm_s"])
    print("weather false positives", summary["weather_false_positives"], "memory", summary["memory"])

"""Module 3 (chatbot) benchmark helpers: builds, turn by turn, the exact prompt each chatbot sends to its LLM.

Systems (same LLM for every answer, so only the chatbot pipeline differs):
    PQ   PlantIQ chatbot: snapshot of backend chat.py (history of the last 8 turns, language router, CNN on an attached
         photo, past-scan hand-off, live weather incl. coordinates typed in the text, greeting skip, hybrid retrieval).
    SK   Selva Kumar et al. as a chatbot: LangChain ConversationalRetrievalChain - when there is history the LLM first
         rewrites the follow-up as a standalone question (LangChain's default condense prompt, "in its original
         language"), then dense top-4 retrieval and LangChain's default QA prompt. A photo is classified by the
         YOLOv8s-cls baseline (fold 0, never trained on these images) and its label is prefixed to the question, as in
         03c. It has no weather, no scan hand-off and no greeting handling.
    PQ offline: the same PlantIQ turn with no LLM reachable (router heuristic, built-in offline reply).

LLM steps (PlantIQ's router, SK's condense step, the answers) are read from files written by the model that plays the
LLM (see README), so building the prompts needs no API. A turn can be built only when the answers to the earlier turns
of its conversation exist (they form the history), so `build_rows` is run once per turn depth.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT, HERE, ROOT / "03_rag"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from common import config  # noqa: E402
from common import rag_eval as R  # noqa: E402

ANS = HERE / "answers"
CONDENSE_PROMPT = ("Given the following conversation and a follow up question, rephrase the follow up question to be a "
                   "standalone question, in its original language.\n\nChat History:\n{chat_history}\n"
                   "Follow Up Input: {question}\nStandalone question:")   # LangChain CONDENSE_QUESTION_PROMPT
YOLO_TO_CLASS = {"Cerscospora": "Cerscospora", "Healthy": "Healthy", "Miner": "Miner", "Phoma": "Phoma", "Rust": "Rust"}


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_cases() -> list[dict]:
    return json.loads((HERE / "cases.json").read_text(encoding="utf-8"))


def answers() -> dict[str, str]:
    return {r["key"]: r["answer"] for r in read_jsonl(ANS / "answers.jsonl")}


def condensed() -> dict[str, str]:
    return {r["key"]: r["standalone_question"] for r in read_jsonl(ANS / "sk_condensed.jsonl")}


def frozen_env():
    from plantiq_chat_snapshot.environment import FrozenEnvironmentService

    resp = {}
    for f in sorted((HERE / "data").glob("weather_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        resp[(d["_recorded"]["lat"], d["_recorded"]["lng"])] = d
    return FrozenEnvironmentService(resp)


class Models:
    """Everything heavy, loaded once: PlantIQ retriever + CNN, SK retriever + YOLO baseline, router file."""

    def __init__(self, device: str = "cuda"):
        from plantiq_rag_snapshot.build import build_retriever, load_embedder
        from plantiq_rag_snapshot.profiles import QUALITY

        from plantiq_chat_snapshot.cnn import CoffeeCNN

        self.device = device
        emb = load_embedder(QUALITY, device)
        self.rag = build_retriever(QUALITY, config.KB_DIR, config.RAG_INDEX / f"pq_{QUALITY.name}", device=device,
                                   embedder=emb)
        self.sk = R.SKRetriever("hf:sentence-transformers/all-mpnet-base-v2", config.KB_DIR, config.RAG_INDEX,
                                device=device)
        self.cnn = CoffeeCNN(config.DEPLOYED_WEIGHTS, device)
        from ultralytics import YOLO

        self.yolo = YOLO(str(config.ROOT / "02_cnn" / "runs" / "Y1" / "fold0" / "weights" / "best.pt"))
        self.router = R.FileRouter(ANS / "router_outputs.jsonl")
        self.env = frozen_env()

    def yolo_label(self, image_path: Path) -> dict:
        r = self.yolo.predict(str(image_path), imgsz=224, device=0 if self.device == "cuda" else "cpu", verbose=False)[0]
        i = int(r.probs.top1)
        return {"class": YOLO_TO_CLASS[r.names[i]], "confidence": round(float(r.probs.top1conf) * 100, 2)}


def _history(case: dict, k: int, system: str, ans: dict) -> list[tuple[str, str]] | None:
    hist = []
    for j in range(k):
        a = ans.get(f"{case['id']}|t{j}|{system}")
        if a is None:
            return None
        hist += [("user", case["turns"][j]["message"]), ("assistant", a)]
    return hist


def build_rows(m: Models, depth: int) -> tuple[list[dict], list[dict]]:
    """Rows for every turn at index `depth` whose history is available. Returns (prompt rows, condense requests)."""
    import time

    from plantiq_chat_snapshot.chat import build_turn
    from plantiq_chat_snapshot.cnn import display_name

    ans, cond = answers(), condensed()
    rows, need_condense = [], []
    for case in load_cases():
        if depth >= len(case["turns"]):
            continue
        t = case["turns"][depth]
        gps = t["gps"] or (None, None)
        img_path = config.DATA_DIR / t["photo"] if t["photo"] else None
        base = {"case": case["id"], "group": case["group"], "turn": depth, "scored": depth == len(case["turns"]) - 1,
                "message": t["message"]}

        # ---------------- PlantIQ (+ offline)
        hist = _history(case, depth, "PQ", ans)
        if hist is not None:
            t0 = time.perf_counter()
            info = m.cnn.predict(img_path.read_bytes()) if img_path else None
            cnn_s = time.perf_counter() - t0
            for sysname, llm in (("PQ", m.router), ("PQoff", None)):
                m.rag._cache.clear()
                out = build_turn(t["message"], hist if sysname == "PQ" else _history(case, depth, "PQ", ans) or [],
                                 rag=m.rag, llm=llm, env_service=m.env, language=t["ui_language"],
                                 latitude=gps[0], longitude=gps[1], image_info=info, scan_metadata=t["scan"])
                rows.append({**base, "key": f"{case['id']}|t{depth}|{sysname}", "system": sysname,
                             "system_prompt": out["system"], "prompt": out["prompt"] if sysname == "PQ" else "",
                             "offline_reply": out["offline_reply"] if sysname == "PQoff" else "",
                             "contexts": [d["text"] for d in out["docs"]],
                             "sources": [f"{d['source']} p.{d['metadata'].get('page')}" for d in out["docs"]],
                             "target": out["target"], "route": out["route"], "greeting": out["greeting"],
                             "weather_query": out["weather_query"], "disease": out["disease"],
                             "env_available": bool(out["env"].get("available")),
                             "env": {k: out["env"].get(k) for k in ("temperature", "humidity", "rainfall", "wind_speed",
                                                                    "incubation_risk", "risk_level", "region_name")}
                             | {"spray_window": (out["env"].get("spray_window") or {}).get("advice_en")},
                             "diagnosis": info, "latency_s": out["pipeline_s_without_llm"] + cnn_s})

        # ---------------- Selva Kumar conversational pipeline
        hist = _history(case, depth, "SK", ans)
        if hist is None:
            continue
        question = t["message"]
        ckey = f"{case['id']}|t{depth}"
        if hist:
            chat_history = "\n".join(f"{'Human' if r == 'user' else 'Assistant'}: {c}" for r, c in hist)
            if ckey not in cond:
                need_condense.append({"key": ckey, "prompt": CONDENSE_PROMPT.format(chat_history=chat_history,
                                                                                    question=question)})
                continue
            question = cond[ckey]
        label = m.yolo_label(img_path) if img_path else None
        q = f"{display_name(label['class'])}: {question}" if label else question
        hits = m.sk.search(q, k=4)
        ctx = [h["text"] for h in hits]
        rows.append({**base, "key": f"{case['id']}|t{depth}|SK", "system": "SK", "system_prompt": "",
                     "prompt": R.SK_PROMPT.format(context="\n\n".join(ctx), question=q), "contexts": ctx,
                     "sources": [f"{h['source']} p.{h['page']}" for h in hits], "standalone_question": q,
                     "diagnosis": label})
    return rows, need_condense


def kannada_share(text: str) -> float:
    """Kannada characters (incl. vowel signs, which are not str.isalpha) over Kannada + Latin letters."""
    kn = sum("ಀ" <= c <= "೿" for c in text)
    latin = sum(c.isascii() and c.isalpha() for c in text)
    return kn / (kn + latin) if kn + latin else 0.0


def numbers(text: str) -> list[float]:
    return [float(x) for x in re.findall(r"(?<![\d.])(\d{1,3}(?:\.\d)?)(?![\d.])", text or "")]

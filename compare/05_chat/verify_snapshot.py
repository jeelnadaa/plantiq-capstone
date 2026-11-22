"""Checks that plantiq_chat_snapshot.chat.build_turn builds exactly the prompt, retrieval query and offline reply of the
backend's chat.process_message. Run ONCE with the backend's environment (it imports the app read-only and uses an
in-memory SQLite database; nothing in the app is changed):

    ..\\backend\\.venv\\Scripts\\python 05_chat\\verify_snapshot.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
os.environ.setdefault("PLANTIQ_FAKE_ML", "1")
sys.path[:0] = [str(REPO / "backend"), str(HERE), str(HERE.parent), str(HERE.parent / "03_rag")]

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402

from app.core.db import init_db  # noqa: E402
from app.models import User  # noqa: E402
from app.services import chat as backend_chat  # noqa: E402
from common import rag_eval as R  # noqa: E402
from plantiq_chat_snapshot import chat as snap  # noqa: E402
from chat_bench import frozen_env  # noqa: E402

router = R.FileRouter(HERE / "answers" / "router_outputs.jsonl")


class FakeLLM:
    available = True

    def __init__(self, with_router=True):
        self.prompts, self.with_router = [], with_router

    def generate(self, prompt, system="", temperature=0.3, max_tokens=800, json_mode=False):
        if "linguistic pre-router" in prompt:
            return router.generate(prompt) if self.with_router else None
        self.prompts.append(prompt)
        return SimpleNamespace(text="REPLY", provider="fake", model="fake")


class FakeRag:
    def __init__(self):
        self.calls = []

    def search(self, q, top_k=3, rerank_query=None, **kw):
        self.calls.append((q, rerank_query))
        return [{"text": f"[Doc] passage about {q[:40]}", "source": "guide.pdf", "metadata": {"page": 7}, "score": 0.8}]


class FakeCNN:
    def predict(self, b):
        return {"class": "Rust", "confidence": 91.25, "distribution": {}}


engine = create_engine("sqlite://")
init_db(engine)
db = sessionmaker(bind=engine, expire_on_commit=False)()
db.add(User(id=1, username="t", full_name="T", hashed_password="x"))
db.commit()
env = frozen_env()
CKM = (13.3161, 75.7720)
SCAN = {"disease": "Cerscospora", "confidence": 88.0, "advisory": "Restore shade.",
        "env_data": {"available": True, "temperature": 23.1, "humidity": 86, "region_name": "X"}}
SCENARIOS = [
    ("multi-turn", ["When should I give the pre-monsoon Bordeaux mixture spray against coffee leaf rust, and at what strength?",
                    "What pH should it have?"], {}),
    ("kannada", ["ಅದರ ಪಿಎಚ್ ಎಷ್ಟು ಇರಬೇಕು?"], {"language": "kn"}),
    ("kanglish", ["coffee gidakke sunna yaavaga haakbeku?"], {}),
    ("photo", ["What is wrong with this leaf and what should I do?"], {"image": True}),
    ("scan+gps", ["I scanned this leaf last week. Is today a good day to give that spray?"], {"gps": CKM, "scan": SCAN}),
    ("coords-in-text", ["My estate is at 13.32, 75.77. How is the humidity there and is it rust weather?"], {}),
    ("no-location", ["What is the temperature at my estate right now?"], {}),
    ("greeting", ["Hello"], {}),
    ("place", ["Chikkamagaluru"], {}),
]
ok = 0
for offline in (False, True):
    for name, msgs, kw in SCENARIOS:
        llm_b, llm_s = (None, None) if offline else (FakeLLM(), FakeLLM())
        rag_b, rag_s = FakeRag(), FakeRag()
        sid, hist = None, []
        for msg in msgs:
            gps = kw.get("gps") or (None, None)
            res = backend_chat.process_message(db, backend_chat.ChatInput(
                user_id=1, message=msg, session_id=sid, language=kw.get("language", "en"), latitude=gps[0],
                longitude=gps[1], image_bytes=b"img" if kw.get("image") else None, scan_metadata=kw.get("scan")),
                cnn=FakeCNN(), rag=rag_b, llm=llm_b, env_service=env)
            sid = res["session_id"]
            out = snap.build_turn(msg, hist, rag=rag_s, llm=llm_s, env_service=env, language=kw.get("language", "en"),
                                  latitude=gps[0], longitude=gps[1],
                                  image_info=FakeCNN().predict(b"") if kw.get("image") else None,
                                  scan_metadata=kw.get("scan"))
            if offline:
                assert out["offline_reply"] == res["reply"], (name, out["offline_reply"], res["reply"])
            else:
                assert llm_b.prompts[-1] == out["prompt"], (name, llm_b.prompts[-1], out["prompt"])
                assert out["target"] == res["language"], name
            assert rag_b.calls == rag_s.calls, (name, rag_b.calls, rag_s.calls)
            hist += [("user", msg), ("assistant", res["reply"])]
            ok += 1
print(f"snapshot identical to backend chat.process_message on {ok} turns (prompt, retrieval query, language, "
      f"offline reply)")

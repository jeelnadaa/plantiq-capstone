import logging, sys
sys.path.insert(0, ".")
logging.disable(logging.WARNING)
from app.core.config import settings
settings.RAG_AUTO_BUILD = False
from app.services.rag.retriever import HybridRetriever
from app.services.rag.query import expand_query
from app.services.rag.chunking import DISEASE_TOPIC
r = HybridRetriever.load_or_build()
for d in ["Rust", "Cerscospora", "Miner", "Phoma", "Healthy"]:
    for q in ["When should I spray?", None]:
        from app.services.cnn import display_name
        nat = q or "symptoms, control and spray schedule"
        rq = f"How to keep a healthy coffee plant? {nat}" if d == "Healthy" else f"How to manage {display_name(d)} on coffee? {nat}"
        res = r.search(expand_query(q, d), top_k=3, topic_filter=DISEASE_TOPIC.get(d), rerank_query=rq)
        print(f"{d:12s} q={str(q)[:22]:22s} {[x['score'] for x in res]} {[x['metadata']['topic'][:12] for x in res]}")
for q in ["coffee leaf rust symptoms orange powder", "white stem borer control", "best fertilizer for arabica flowering",
          "what is the capital of France", "rust control kannada"]:
    print(f"{q[:40]:40s} {[x['score'] for x in r.search(q, top_k=3)]}")

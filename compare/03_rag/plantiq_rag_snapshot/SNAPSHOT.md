# PlantIQ RAG snapshot

Copied from the PlantIQ backend at commit `560e9af` so the benchmark never imports or changes the app.

| File here | Source | Changes |
|---|---|---|
| `chunking.py` | `backend/app/services/rag/chunking.py` | none |
| `query.py` | `backend/app/services/rag/query.py` | none (query expansion + `audit_dosages`) |
| `retriever.py` | `backend/app/services/rag/retriever.py` | imports; `load_or_build` removed (settings-driven loading, replaced by `build.py`) |
| `index.py` | `backend/app/services/rag/index.py` | imports; only `extract_chunks` kept (index building moved to `build.py`) |
| `profiles.py` | `backend/app/services/rag/profiles.py` | dataclass and the two profiles only; no automatic hardware choice |
| `lang_router.py` | `backend/app/services/lang_router.py` | imports |
| `text.py` | `backend/app/core/text.py` | only `clean_user_text`, `has_kannada` |
| `advisory.py` | `backend/app/services/advisory.py` | thresholds as constants; LLM adapter; no offline fallback; returns the retrieved passages |
| `build.py` | `index.build_index` + `load_embedder` + `HybridRetriever.load_or_build` | explicit paths; caches the index in the given folder |

Search, fusion, reranking, topic filter, MMR, prompt text and dose audit are byte-for-byte the backend's logic.

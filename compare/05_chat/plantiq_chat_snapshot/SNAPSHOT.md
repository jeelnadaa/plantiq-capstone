# PlantIQ chat snapshot

Generated from the PlantIQ backend by `../make_snapshot.py` (the commit is written at the top of `chat.py`; currently
`ab5c95c`, after the history-aware router, word-start weather detection and Kannada offline fixes), so the Module 3
benchmark never imports or changes the app. The first run used the snapshot of commit `d19d29a`; its results are kept
in `results/chat/chat_before_fix.json`. `verify_snapshot.py` runs the backend's `chat.process_message` and this snapshot
side by side on 20 turns (multi-turn, Kannada, Kanglish, photo, past scan + GPS, coordinates in text, no location,
greeting, place name; with and without an LLM) and asserts identical prompts, retrieval queries, reply language and
offline replies.

| File here | Source | Changes |
|---|---|---|
| `chat.py` | `backend/app/services/chat.py` | `process_message` → `build_turn` without the database (history passed in, nothing stored); the constants and weather matcher, `_scan_block`, the router call, the retrieval block, the prompt block and the offline call are sliced verbatim from the backend file by `make_snapshot.py` |
| `environment.py` | `backend/app/services/environment.py` | HTTP client replaced by `FrozenEnvironmentService` (recorded Open-Meteo responses, `data/weather_*.json`); `_num`, `_parse`, risk and spray-window logic unchanged |
| `knowledge.py` | `backend/app/services/knowledge.py` | none (offline disease cards and offline chat reply); copied by `make_snapshot.py` |
| `cnn.py` | `backend/app/services/cnn.py` | explicit weights path instead of settings; no device auto-selection or lock |
| `lang_router.py` | `backend/app/services/lang_router.py` | import path; copied by `make_snapshot.py` (also into the Module 2 snapshot, whose router prompt is unchanged because it passes no history) |
| `text.py` | the Module 2 snapshot (`03_rag/plantiq_rag_snapshot`) | none |

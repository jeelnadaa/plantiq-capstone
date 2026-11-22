# PlantIQ chat snapshot

Copied from the PlantIQ backend at commit `d19d29a` (chat logic last changed in `b421009`), so the Module 3 benchmark
never imports or changes the app. `verify_snapshot.py` runs the backend's `chat.process_message` and this snapshot
side by side on 20 turns (multi-turn, Kannada, Kanglish, photo, past scan + GPS, coordinates in text, no location,
greeting, place name; with and without an LLM) and asserts identical prompts, retrieval queries, reply language and
offline replies.

| File here | Source | Changes |
|---|---|---|
| `chat.py` | `backend/app/services/chat.py` | `process_message` → `build_turn` without the database (history passed in, nothing stored); the constants, `_scan_block`, the retrieval block and the prompt block are sliced verbatim from the backend file |
| `environment.py` | `backend/app/services/environment.py` | HTTP client replaced by `FrozenEnvironmentService` (recorded Open-Meteo responses, `data/weather_*.json`); `_num`, `_parse`, risk and spray-window logic unchanged |
| `knowledge.py` | `backend/app/services/knowledge.py` | none (offline disease cards and offline chat reply) |
| `cnn.py` | `backend/app/services/cnn.py` | explicit weights path instead of settings; no device auto-selection or lock |
| `lang_router.py`, `text.py` | the Module 2 snapshot (`03_rag/plantiq_rag_snapshot`) | none |

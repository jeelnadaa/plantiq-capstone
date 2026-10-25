# PlantIQ — claude-plantiq rebuild

AI helper for South-Indian coffee farmers. Photograph a leaf to detect disease with the original ResNet-50, get a
grounded treatment plan (hybrid RAG over CCRI documents + Gemini/Groq) that accounts for live estate weather,
chat in English or Kannada (with voice), and buy/sell coffee lots in a local marketplace. Android app + backend server.

> Status: **v3.0.0 — all 10 phases complete.** See [progress.md](progress.md) for the log and [FEATURES.md](FEATURES.md) for
> the feature-by-feature parity with the original app.

## Quick start
```bash
scripts\run_backend.bat                    # Windows (./scripts/run_backend.sh on Linux/macOS)
```
Open `http://localhost:8000` for the web app, or install `release/PlantIQ-claude-3.0.0.apk` on an Android phone and enter the
`Phone:` address the server prints. Full instructions: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## What's inside
| | |
|---|---|
| `backend/` | FastAPI · SQLAlchemy (Postgres or SQLite) · ResNet-50 (same weights) · hybrid RAG (bge-m3 + BM25 + RRF + bge-reranker-v2-m3 + MMR) · Gemini → Groq → offline · Open-Meteo · IndicConformer / Svarah Whisper STT |
| `frontend/` | React 18 + TypeScript + Vite single-page app, Satoshi + Noto Sans Kannada, EN/KN, 5 palettes × light/dark |
| `mobile/` | Capacitor 7 Android wrapper → APK with runtime-configurable backend URL |
| `design/` | "Field Notebook" design system and 16 phone mockups ([DESIGN.md](DESIGN.md)) |
| `scripts/` | `run_backend`, `sync_web.py`, `build_apk.py` |

## Features
- **Scan**: camera/gallery, optional typed or spoken question, disease + confidence ring + probabilities, low-certainty notice,
  "what to do" (Do today / Spray / Timing / Prevent), dose check against sources, citations, weather at scan time, hand-off to chat.
- **Weather**: auto GPS or manual coordinates (Google Maps guide), temperature/humidity/rain/elevation, disease-risk banner,
  3-day forecast and **spray window**; never invents data.
- **Ask**: threaded chat, attach a new photo or a past scan, scan hand-off, coordinates in text, weather questions, Kannada/Kanglish,
  rename/delete threads, voice.
- **Market**: sell with units (kg/ton/quintal/bags/custom → ₹/kg), photos with captions, GPS, validation that explains *what* and
  *why*, search, sort (nearest/newest/price/qty), filters sheet with live count, call/WhatsApp/route, edit/delete, report.
- **History**: server-side, grouped by day, filters, details, delete & clear-all with 3-second undo.
- **Account**: sign-up with phone and/or email, strength meter, username availability, sign-in with phone/email/username,
  lockout countdown, profile edit, password change, signed-in devices, sign out everywhere, delete account.
- **App**: EN/ಕನ್ನಡ toggle, dark mode, 5 colour themes incl. high-contrast "Sunlight", server status + ping, offline banner,
  Android back button, first-run server setup.

## Development
```bash
cd backend  && .venv/Scripts/python -m pytest -m "not ml"   # 286 tests, ~30 s
cd frontend && npm test && npm run e2e                       # 52 vitest + 11 Playwright (Pixel 7)
cd frontend && npm run dev                                   # Vite on :5173, proxies /api to :8000
python scripts/build_apk.py                                  # → dist/PlantIQ-claude.apk
```
Testing details: [TESTING.md](TESTING.md). Security: [SECURITY.md](SECURITY.md). Endpoints: [API.md](API.md).

## Documents
| File | Purpose |
|---|---|
| [plan.md](plan.md) | Architecture and phased plan |
| [CLAUDE.md](CLAUDE.md) | Working agreement / commands |
| [FEATURES.md](FEATURES.md) | Feature parity matrix vs. the original app |
| [progress.md](progress.md) | Phase-by-phase log |
| [DESIGN.md](DESIGN.md) | Design system and rationale |
| [SECURITY.md](SECURITY.md) | Threats, controls, fixed vulnerabilities |
| [TESTING.md](TESTING.md) | Test suites, coverage, real-model results |
| [API.md](API.md) | Endpoint reference |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Run the server, install the APK, cloud, signing |

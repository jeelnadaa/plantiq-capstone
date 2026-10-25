# CLAUDE.md — working agreement for claude-plantiq

This folder is a rebuild of the PlantIQ coffee-farmer app found in `../backend`, `../frontend`, `../mobile`.
Read [plan.md](plan.md) first; [FEATURES.md](FEATURES.md) is the source of truth for scope.

## How to work here
- Work **phase by phase** (plan.md §4). Do not start a phase before the previous one's tests pass.
- After every phase (or meaningful step):
  1. append an entry to [progress.md](progress.md) (date, phase, what changed, test results, open issues),
  2. update [README.md](README.md) if setup/usage changed,
  3. tick rows in FEATURES.md,
  4. `git add claude-plantiq && git commit` — **never push**.
- Never touch files outside `claude-plantiq/` (the original app must keep working). Reading them is fine.
- Never commit secrets. `backend/.env` is git-ignored; `.env.example` documents every variable.

## Commands
```bash
# backend (from claude-plantiq/backend)
.venv/Scripts/python run.py                         # API + web UI on :8000
.venv/Scripts/python -m pytest -m "not ml"          # fast suite, fake ML
.venv/Scripts/python -m pytest -m ml                # real CNN/RAG smoke tests (needs weights + GPU/CPU)
.venv/Scripts/python scripts/build_index.py         # rebuild RAG index (profile from RAG_PROFILE)

# frontend (from claude-plantiq/frontend)
npm run dev        # Vite dev server on :5173 (proxies /api to :8000)
npm run build      # → dist/, copied into backend/static by scripts/sync_web.py
npm test           # vitest
npm run e2e        # Playwright, Pixel-7 viewport

# all tests → TESTING.md matrix (from claude-plantiq)
python scripts/test_matrix.py # --skip-ml to skip real-model tests, --no-run to rebuild from reports

# mobile (from claude-plantiq)
python scripts/build_apk.py   # builds frontend, syncs Capacitor, assembles → dist/PlantIQ.apk
```

## Conventions
- Python: 3.11, FastAPI, SQLAlchemy 2 (typed `Mapped[...]`), Pydantic v2. Services are lazy singletons with a
  `get_*()` accessor so tests can swap them via `app.dependency_overrides` or `services.registry`.
- Heavy ML imports (`torch`, `sentence_transformers`, `faiss`, `transformers`) happen **inside** service
  constructors, never at module import time, so the fast test-suite runs without loading models.
- `PLANTIQ_FAKE_ML=1` swaps CNN / RAG / LLM / STT for deterministic fakes (used by tests and E2E).
- API under `/api/v1/...`; `/api/...` is an alias so original clients keep working.
- Frontend: React + TS, functional components, no UI framework; styles from design tokens in
  `src/styles/tokens.css`. Every user-visible string goes through `t()` and must exist in both `en` and `kn`
  (a unit test enforces parity).
- Mobile-first: design and test at 393×852. Minimum tap target 44 px. Icons always paired with text labels.
- Security rules: never render server/LLM text as raw HTML; validate every upload through `core/uploads.py`;
  every write endpoint needs auth + ownership checks; add a security test for each new endpoint.

## Testing policy
Markers: `unit`, `integration`, `functional`, `security`, `nonfunctional`, `ml`. A change is done when the
relevant suite is green and a test covers it. Record suite counts in progress.md and regenerate TESTING.md with `scripts/test_matrix.py`.
Documentation lives in docs/ (overview, flows, architecture, one file per module); update the module doc when behaviour changes.

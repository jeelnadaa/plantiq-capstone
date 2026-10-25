# Progress log

Newest entries at the bottom. Each entry: phase · what changed · tests · open issues.

---

## 2026-10-25 · Phase 0 — Discovery & planning
**Done**
- Read the full original app: backend (FastAPI: auth, predict, chat, voice, marketplace, environment; services
  for CNN, hybrid RAG, router, env, voice, cache), frontend (6 HTML pages + 10 JS modules + i18n), mobile
  (Capacitor 7 wrapper, build script), existing tests and SECURITY.md.
- Inventoried 110 original behaviours + 18 improvements into [FEATURES.md](FEATURES.md).
- Wrote [plan.md](plan.md) (architecture, RAG hardware profile, 10 phases, risks, DoD) and [CLAUDE.md](CLAUDE.md).
- Environment check: RTX 3070 Laptop 8 GB / CUDA 12.1 torch, Python 3.11, Node 24, JDK 21, Android SDK present,
  Postgres listening on :5432, internet available.
- Created `backend/.venv` (Python 3.11) and installed dependencies.

**Security gaps found in the original** (to fix in the rebuild): anonymous listing ownership hole, raw-HTML
markdown rendering (XSS), plaintext long-lived session tokens, no login rate limit/lockout, `pickle.load` on
RAG index, base64 photos in DB.

**Tests**: n/a (planning).

## 2026-10-25 · Phase 1 — Design
**Done**
- New "Field Notebook" design language for farmers (not a copy of the original neo-brutalist UI): warm paper
  background, leaf-green primary, coffee-cherry accent, Satoshi (bundled woff2 + FFL licence) with Noto Sans Kannada
  fallback, 54 px controls, icon+text everywhere, bottom sheets, undo toasts.
- `design/tokens.css` (5 palettes × light/dark incl. high-contrast *Sunlight*), `design/components.css`
  (≈60 components), `design/mockups.html` (16 phone screens at 393×852), [DESIGN.md](DESIGN.md).
- Reviewed the mockups in the browser in light and dark; fixed FAB placement inside phone frames.

**Tests**: visual review only (design phase).

## 2026-10-25 · Phases 2–3 — Backend foundation, auth & security
**Done**
- FastAPI app factory; Settings with production guards (strong SECRET_KEY, no `*` CORS); Postgres with auto-create and
  SQLite fallback; additive migrations; timezone-aware datetimes on SQLite.
- ASGI security middleware (CSP, headers, request id, 15 MB body limit, global rate limit); uniform error envelope.
- Auth: Argon2id (+ legacy bcrypt/PBKDF2 upgrade), password policy, JWT access + hashed rotating refresh tokens with reuse
  detection, login by username/email/phone, lockout, sessions/devices, logout-all, profile, password change, GDPR delete, audit log.
**Tests**: unit + integration green (214 at that point). Bugs caught: duplicate security headers, place-name router check.

## 2026-10-25 · Phases 4–5 — ML services and feature APIs
**Done**
- CNN: same ResNet-50 weights (sha256 e1fd039f…), classes, preprocessing.
- RAG: pickle-free FAISS + JSON index, hardware profile (bge-m3 + bge-reranker-v2-m3 on GPU; bge-base + MiniLM fallback),
  BM25 + RRF + topic filter + rerank + MMR, intent expansion, dosage audit. Quality index built: 931 chunks, 14 PDFs.
- LLM over REST (Gemini → Groq → offline bilingual guide), language router, Open-Meteo + 3-day forecast + spray window,
  STT chain (IndicConformer / Svarah Whisper / Groq / Gemini), server-side scan history with undo, chat threads, marketplace
  with media uploads and reports.
- torch upgraded 2.5.1 → 2.7.1 (CVE-2025-32434; also required to load bge-m3).
**Tests**: 286 backend tests (unit 146, integration 69, functional 3, security 58, non-functional 10) + 4 real-model tests.

## 2026-10-25 · Phases 6–7 — Frontend
**Done**: React + TS SPA (hash router → works in APK): server setup, sign-in/up, scanner, diagnosis, chat, market, history,
profile and all sheets; EN/KN dictionaries (≈480 keys each); 5 palettes × light/dark; XSS-safe markdown.
**Browser testing at 375×812** found and fixed: app-bar overflow, infinite reload loop (unstable error helper), Escape closing
every sheet, sheet re-registration order, FAB covering listing actions, `http://` URL normalisation.

## 2026-10-25 · Phase 8 — E2E & non-functional
**Tests**: vitest 52 ✅, Playwright 11 ✅ (Pixel 7) incl. accessibility sweep (labels, ≥40 px buttons → chips raised to 40 px).

## 2026-10-25 · Phase 9 — Mobile & packaging
**Done**: Capacitor 7 Android (`ai.plantiq.claude`, v3.0.0), permissions, network config, PlantIQ icon/splash,
`scripts/build_apk.py` (with a fix for the Windows JDK "Unable to establish loopback connection" temp-dir bug),
`release/PlantIQ-claude-3.0.0.apk` (4.6 MB), run scripts (bat/sh), Dockerfile.
**Not verified**: running on an emulator/device — no hypervisor on this machine; APK checked with aapt2.

## 2026-10-25 · Phase 10 — Real-model run, hardening & docs
**Real stack** (GPU, Postgres, Gemini/Groq): 5/5 sample leaves correct at 99.5–100 %; ≈6 s per diagnosis.
**Fixed from the real run**: Gemini 2.5 thinking tokens truncated advisories to ~100 chars (thinking off, bigger budget,
MAX_TOKENS → fall back to Groq); reranker now scores a natural question (Cercospora top match 0.35 → 0.94); healthy leaves not
flagged uncertain; bge models stored as safetensors (`scripts/prepare_models.py`) after a low-RAM crash loading pickle `.bin`;
Postgres create-database race.
**Docs**: SECURITY.md, TESTING.md, API.md, docs/DEPLOYMENT.md, README; FEATURES.md all ✅.
**Open items**: on-device APK test; moderator UI for reports; Redis rate limiter if scaled to multiple workers.

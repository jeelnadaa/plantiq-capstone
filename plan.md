# PlantIQ v3 — Rebuild Plan

A clean-room rebuild of the original PlantIQ coffee-farmer app (now kept in `og/`).
Every feature of the original is carried over (see [FEATURES.md](FEATURES.md) for the line-by-line parity
matrix), security is redone properly, sign-in / sign-up are redesigned, and the UI gets a new farmer-first
design (Satoshi font). The deliverables are an Android **APK** that can point at any backend URL at runtime,
and a **backend server** that can be run on a laptop or a cloud VM.

---

## 1. Goals and non-goals

### Goals
1. **Feature parity** with the original app — nothing dropped, however small (theme palettes, undo toast,
   GMaps guide, bilingual validation modal, server ping latency, native back button…).
2. **Same ML core**: the original ResNet-50 weights `best_resnet50_coffee.pth`, same 5 classes
   (`Miner, Rust, Phoma, Healthy, Cerscospora`), same preprocessing (224×224, ImageNet normalisation),
   same confidence-blending thresholds (CNN 75 %, RAG 0.60).
3. **Equal-or-better RAG**, tuned to this laptop (RTX 3070 Laptop, 8 GB VRAM, CUDA 12.1 torch):
   hybrid dense + BM25 + RRF + cross-encoder rerank, with a hardware-aware model profile.
4. **Improved sign-up / sign-in** (UX and security).
5. **Real security** (OWASP ASVS L1-style controls, documented in [SECURITY.md](SECURITY.md)).
6. **Full test pyramid**: unit, integration, functional (API + E2E UI), non-functional (performance,
   load, payload limits, accessibility basics), security.
7. **Dynamic backend URL** in the APK, editable at runtime, with a connectivity test.
8. Work in **phases**; each phase logged in [progress.md](progress.md), README updated, committed (never pushed).

### Non-goals
- Retraining the CNN (we reuse the exact weights).
- Payment / escrow in the marketplace (original has none).
- Play-store signing (a debug-signed APK is produced; release signing is documented).

---

## 2. What the original app does (inventory summary)

| Area | Original behaviour |
|---|---|
| Scanner | Upload/capture leaf → `/api/predict` → ResNet-50 class + confidence + per-class distribution, Open-Meteo microclimate, hybrid-RAG advisory via Gemini → Groq fallback, dosage safety audit, SHA-256 dedup cache, "blended advisory" low-confidence notice, optional typed or **voice** question, "Ask follow-up in chat" hand-off. |
| Location | Auto GPS or manual lat/lng, GMaps coordinates guide (EN + KN), live microclimate panel (temp, feels-like, humidity, rain, elevation, risk banner), refresh. Region detection for Chikkamagaluru / Kodagu / Hassan. No mock data — "unavailable" when missing. |
| Chat | Multi-turn threads (list, new, reload), image attach (new upload **or** pick from scan history), scan-metadata hand-off, CNN on attached photo, coordinate extraction from message text, weather-intent detection (EN + KN keywords), Kannada/Kanglish routing via LLM pre-router, last-8-message history in prompt, prompt-injection fencing, key redaction. |
| Voice | MediaRecorder → `/api/voice/transcribe`; language picker modal (KN/EN); local IndicConformer-600M for Kannada, Svarah Whisper for Indian English; Groq whisper-large-v3 → Gemini audio fallbacks; FFmpeg decoding; granular env toggles. |
| Marketplace | List/sell coffee lots; units (kg, ton, quintal, 50/60 kg bag, custom) normalised to kg and ₹/kg; search; sort (nearest/haversine, newest, price ↑↓, qty); filters (distance radius, variety, min qty, price dual slider, photos only, reset); "my listings" tab; multi-photo with captions + gallery; call / WhatsApp / Google Maps; edit; delete-confirm modal; validation modal explaining *what* to fill and *why*; 10-digit phone rule; 50-listing quota; report endpoint. |
| History | Local scan history (max 50), details modal (image, probabilities, microclimate, advisory), delete with 3-second undo toast, clear-all with undo, "ask in chat" from a past scan. |
| Profile | Name, email, total scans, active listings, sign out. Backend has GDPR account delete. |
| Shell | Bottom nav (Scanner, Chatbot, Market, History, Profile), dark/light toggle, 5 colour palettes, EN/KN toggle, server-settings modal (ping with latency, save, reset), server status dot, auth guard, Capacitor back-button handling, external app opener. |

Gaps found in the original that the rebuild fixes (also listed in FEATURES.md "Improvements"):
- Anonymous users could create listings; anonymous-owned listings could be edited/deleted by **any** user.
- `formatMarkdown` injected LLM output as raw HTML (stored XSS vector via chat history).
- Opaque session tokens stored in plain text in DB, 7-day lifetime, no refresh/rotation, no revocation UI.
- No rate limiting or lockout on login; no password policy.
- `pickle.load` of RAG index files (arbitrary code execution if the index dir is writable).
- Scan history only in browser `localStorage` (lost on reinstall, not synced).
- Listing photos stored as base64 data-URLs inside the DB row.
- No report button in the UI even though the API existed; no delete for chat threads.
- No LLM key → advisory was the useless string "Standard CCRI guidelines applied."

---

## 3. Target architecture

```
plantiq/ (repo root)
├── backend/                 FastAPI service (Python 3.11, own .venv)
│   ├── app/
│   │   ├── core/            config, db, security (JWT, Argon2id), rate limit, logging, middleware
│   │   ├── models/          SQLAlchemy ORM (users, refresh_tokens, scans, chat, listings, reports, media, audit)
│   │   ├── schemas/         Pydantic v2 request/response models + validation
│   │   ├── api/             routers: auth, users, predict, scans, chat, voice, marketplace, media, environment, system
│   │   ├── services/        cnn, rag (index + retriever), llm (Gemini/Groq REST), router (lang), env (Open-Meteo),
│   │   │                    voice (STT), advisory (offline fallback), chat orchestration, storage
│   │   └── main.py          app factory, middleware, static SPA serving
│   ├── data/                model weights, knowledge_base PDFs, rag index (JSON + FAISS, no pickle)
│   ├── scripts/             build_index.py, create_admin.py, seed_demo.py
│   ├── tests/               unit / integration / functional / security / nonfunctional / ml
│   └── run.py
├── frontend/                React 18 + TypeScript + Vite SPA (hash router → works from file:// in the APK)
│   ├── src/ (app shell, screens, components, lib/api, lib/i18n, theme tokens, fonts/Satoshi)
│   ├── tests/ (vitest unit + component) and e2e/ (Playwright, Pixel-7 viewport)
├── mobile/                  Capacitor 7 Android wrapper → PlantIQ.apk
├── design/                  design system + phone-size screen mockups (HTML) + rationale
├── scripts/                 one-command helpers (setup, run backend, build apk)
└── *.md                     plan, CLAUDE, progress, README, FEATURES, SECURITY, TESTING, DESIGN, API
```

### Why these choices
- **React + TS + Vite SPA** instead of 6 separate HTML pages: one bundle for both the web UI (served by the
  backend at `/`) and the APK (`file://`-safe hash routing), typed API client, component tests.
- **REST calls to Gemini / Groq through `httpx`** instead of two vendor SDKs: smaller install, uniform
  timeouts/retries, trivially mockable in tests. The provider order (Gemini → Groq → offline) is unchanged.
- **SQLite by default, PostgreSQL by `DATABASE_URL`**: zero-config dev and tests; Postgres for deployment.
- **JWT access + rotating refresh tokens** with server-side refresh-token families (hashed) for revocation.

### RAG profile ("same or better, depending on the laptop")
| Profile | When | Dense embedder | Reranker |
|---|---|---|---|
| `quality` | CUDA available with ≥ 6 GB VRAM (this laptop) | `BAAI/bge-m3` (multilingual, 1024-d, handles Kannada queries natively) | `BAAI/bge-reranker-v2-m3` (multilingual) |
| `balanced` | CPU or small GPU | `BAAI/bge-base-en-v1.5` (original) | `cross-encoder/ms-marco-MiniLM-L-6-v2` (original) |
| `auto` (default) | picks one of the above at start-up; falls back to `balanced` if the `quality` models cannot be loaded | | |

Retrieval pipeline: query routing/translation → dense top-k (FAISS IP) + BM25 top-k → RRF (k=60) →
topic filter (disease-aware, relaxed if empty) → cross-encoder rerank (sigmoid-normalised) → MMR de-duplication →
top-k chunks with source + page citations returned to the client. Index stored as `faiss.index` +
`chunks.json` + `meta.json` (model name, dimension, build time) — **no pickle**; BM25 rebuilt in memory at load.

---

## 4. Phases

Each phase ends with: tests for that phase green → progress.md entry → README updated → `git commit` (no push).

| # | Phase | Output | Exit criteria |
|---|---|---|---|
| 0 | **Discovery & planning** | plan.md, CLAUDE.md, FEATURES.md (parity matrix), progress.md, README skeleton | Every original feature listed with an ID |
| 1 | **Design** | design/ (tokens, components, 10+ phone mockups), DESIGN.md | Mockups reviewed at 390×844 in browser |
| 2 | **Backend foundation** | config, DB, models, middleware (headers, CSP, size limit, request-id), rate limiter, error handling, health | unit tests green |
| 3 | **Auth & security** | register / login (username/email/phone) / refresh / logout / logout-all / sessions / me / update / change-password / delete account, Argon2id, lockout, password policy | auth + security tests green |
| 4 | **ML services** | CNN (same weights), RAG index builder + hybrid retriever, LLM client, language router, offline advisory, env service (+3-day spray window), voice STT pipeline | unit tests with fakes + `ml` smoke tests on real weights |
| 5 | **Feature APIs** | predict, scans history (server-side, soft delete + restore), chat (threads CRUD), voice, marketplace (+ media upload, report), environment | integration + functional API tests green |
| 6 | **Frontend shell** | app shell, router, theme (light/dark + palettes), i18n EN/KN, server settings + status, auth screens | vitest green |
| 7 | **Frontend features** | Scanner, Chat, Market, History, Profile, all modals | vitest green, manual check in browser |
| 8 | **E2E & non-functional** | Playwright mobile E2E, performance/load tests, accessibility checks | all suites green |
| 9 | **Mobile & packaging** | Capacitor Android project, APK, backend run scripts (+ Dockerfile), deployment docs | APK builds, installs config, connects to backend URL |
| 10 | **Hardening & docs** | final security review, docs complete | README quick-start works from scratch |

---

## 5. Detailed work items

### Phase 2 — Backend foundation
- `Settings` via env (+ `.env`), validated; refuses to start in `ENV=production` with a default `SECRET_KEY`.
- SQLAlchemy 2 engine; SQLite (WAL) default; Postgres if `DATABASE_URL`/`POSTGRES_*` set (with fallback to SQLite
  when unreachable, as in the original); `create_all` + lightweight additive migrations.
- Middleware: request-id, security headers (CSP, HSTS when https, X-Frame-Options DENY, nosniff,
  Referrer-Policy, Permissions-Policy, COOP), body-size limit (15 MB), strict CORS allow-list
  (APK origins `http://localhost`, `capacitor://localhost` included), GZip.
- Uniform error envelope `{ "detail": ..., "code": ..., "request_id": ... }`; no stack traces leak.
- In-memory sliding-window rate limiter (per IP + per user), configurable; 429 with `Retry-After`.

### Phase 3 — Auth (improved sign-up / sign-in)
- Sign-up: full name, username, **phone (10-digit) and/or email**, password + confirm, preferred language,
  terms checkbox. Live validation, password-strength meter, show/hide password, username availability check.
- Sign-in: one "username / email / phone" field, password, show/hide, "keep me signed in", clear errors,
  lockout notice with countdown. Generic "invalid credentials" message (no user enumeration).
- Passwords: Argon2id (time 3, mem 64 MB); policy ≥ 8 chars, letters + digits, not in a small common-password
  list, not equal to username. Transparent re-hash of legacy bcrypt/PBKDF2 hashes on login.
- Tokens: access JWT (HS256, 15 min, `iss`/`aud`/`jti`/`typ`), refresh token (opaque 256-bit, SHA-256 hashed in
  DB, 30 days or 1 day without "keep me signed in"), rotation on every refresh with **reuse detection** (reuse
  revokes the whole family). Logout, logout-all, list active sessions (device, last used), revoke one.
- Account lockout: 5 failures → 15-minute lock per account + per-IP rate limit.
- Profile update, change password (revokes other sessions), account deletion (GDPR purge incl. media).
- Audit log table for auth events.

### Phase 4 — ML services
- `cnn_service`: identical architecture (ResNet-50, `fc = Dropout(0.4) → Linear(2048, 5)`), `weights_only=True`,
  CUDA if available, thread-safe lazy singleton, returns class / confidence / distribution, plus display names.
- `rag`: `scripts/build_index.py` (PyMuPDF text + tables, semantic section chunking with abbreviation-safe sentence
  splitting, topic tagging, contextual header), hybrid retriever as in §3, query-intent expansion
  (timing / dosage / organic / shade / nutrition), dosage safety audit, LRU caches.
- `llm`: Gemini (`gemini-2.5-flash`) → Groq (`openai/gpt-oss-120b`) → offline. Timeouts, one retry,
  secret redaction on output, prompt-injection fencing (`<user_query>` / `<agronomic_context>`).
- `advisory_offline`: built-in bilingual disease cards (symptoms, cultural, organic, chemical per 200 L barrel,
  timing) used when no LLM is reachable — grounded, never empty.
- `router`: LLM JSON pre-router (script detection: kannada_script / kanglish / english, English search query,
  greeting/location-only, target language) with regex fallback.
- `env`: Open-Meteo current + 3-day daily forecast, 60 s cache, region detection, incubation-risk model
  (same thresholds) + **spray-window advice** (rain probability next 24–48 h). No mock data ever.
- `voice`: same provider chain and env toggles; audio guard (≤ 10 MB, ≤ 60 s, allowed containers),
  FFmpeg decode via `imageio-ffmpeg`.

### Phase 5 — Feature APIs (prefix `/api/v1`, `/api` kept as alias for the original paths)
- `POST /predict` (multipart image, question, language, lat/lng) → diagnosis + advisory + citations +
  safety audit; result stored as a **scan** for logged-in users; dedup cache by SHA-256.
- `GET/DELETE /scans`, `GET /scans/{id}`, `DELETE /scans/{id}` (soft), `POST /scans/{id}/restore`,
  `DELETE /scans` (clear all, soft), `POST /scans/restore-all` — powers the undo toast server-side.
- Chat: `POST /chat/message`, `GET /chat/threads`, `GET /chat/threads/{id}/messages`,
  `PATCH /chat/threads/{id}` (rename), `DELETE /chat/threads/{id}`.
- Voice: `POST /voice/transcribe`, `GET /voice/status` (which providers are enabled).
- Marketplace: listings CRUD (auth required for write, owner-only edit/delete), filters/sort as original,
  `GET /marketplace/my-listings`, `POST /marketplace/listings/{id}/report` (one report per user per listing),
  `POST /media` (image upload → re-encoded JPEG, EXIF stripped, served at `/media/{id}.jpg`).
- Environment: `GET /environment/live` (+ `/microclimate` alias), `GET /environment/forecast`.
- System: `GET /health` (+ `/api/health`), `GET /api/v1/system/info` (model profile, device, versions — no secrets).

### Phase 6–7 — Frontend
Screens: Welcome/Server-setup (first launch in APK), Sign in, Sign up, Scanner (home), Diagnosis result,
Chat (threads drawer), Market (browse / my listings / sell-edit sheet), History (+ details sheet), Profile
(+ edit, password, sessions, settings, delete account), modals: server settings, palette, voice language,
GMaps guide, validation, delete confirm, report, image picker. All copy in EN and KN.

### Phase 8 — Testing (see [TESTING.md](TESTING.md))
- Backend `pytest -m "not ml"` runs fully offline with fake CNN/RAG/LLM; `pytest -m ml` loads the real weights
  and classifies the five sample leaves.
- Frontend `vitest` (unit + components), Playwright E2E at 393×852 (Pixel 7) against a backend started in
  `PLANTIQ_FAKE_ML=1` mode.
- Non-functional: latency budgets, 50-concurrent-request load test, payload limits, i18n completeness,
  basic a11y (labels, contrast tokens, tap-target ≥ 44 px).
- Security: auth bypass, JWT tampering/alg=none/expiry, refresh reuse detection, IDOR on scans/threads/listings,
  rate limit + lockout, upload attacks (polyglot, oversized, decompression bomb, path traversal), XSS payloads,
  SQL-injection strings, prompt-injection, CORS, headers, secret redaction.

### Phase 9 — Mobile & packaging
- Capacitor 7 Android (`ai.plantiq`), plugins: App (back button), Browser, Preferences.
- First-run screen asks for the backend URL (with LAN-IP hint and ping test); changeable anytime from the
  header server button; stored in Preferences/localStorage; all requests built from it at call time.
- Android network-security-config allows cleartext only because LAN laptops have no TLS — documented, and
  HTTPS URLs are recommended/flagged in the UI.
- `scripts/build_apk.ps1|.py` → `dist/PlantIQ.apk`; `scripts/run_backend.*`, `backend/Dockerfile`.

---

## 6. Risks & mitigations
| Risk | Mitigation |
|---|---|
| `bge-m3` / reranker download is large (~4.5 GB) or fails | `auto` profile falls back to the cached `bge-base` + MiniLM models; index stores which model built it and rebuilds if mismatched |
| GPU memory contention (STT 600M + RAG + CNN) | lazy loading, fp16 for RAG models on CUDA, STT loaded on first use only |
| LLM keys missing / quota | offline grounded advisory; tests never call real LLMs |
| Cleartext HTTP to LAN backend | documented; UI warns on `http://` for non-private IPs; supports HTTPS/tunnels |
| Scope size | strict phase gating, parity matrix ticked as features land |

## 7. Definition of done
- FEATURES.md: every row ✅.
- All test suites green; numbers recorded in progress.md and TESTING.md.
- `dist/PlantIQ.apk` built; backend starts with `scripts/run_backend` and the APK connects via the
  server settings screen.
- README quick-start reproducible; all work committed locally, not pushed.

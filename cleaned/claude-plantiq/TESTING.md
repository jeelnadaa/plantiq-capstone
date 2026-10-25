# Testing

| Suite | Tool | Count | Command | Needs |
|---|---|---|---|---|
| Backend unit | pytest `-m unit` | 146 | `pytest -m unit` | nothing (fake ML) |
| Backend integration (API + DB) | pytest `-m integration` | 69 | `pytest -m integration` | nothing |
| Backend functional journeys | pytest `-m functional` | 3 | `pytest -m functional` | nothing |
| Backend security | pytest `-m security` | 58 | `pytest -m security` | nothing |
| Backend non-functional | pytest `-m nonfunctional` | 10 | `pytest -m nonfunctional` | nothing |
| Real models (CNN weights, RAG) | pytest `-m ml` | 4 (all pass; RAG test ≈6 min on CPU) | `pytest -m ml` (`PLANTIQ_TEST_RAG=1` to include RAG) | weights; GPU optional |
| Frontend unit + component | vitest | 52 | `npm test` (in `frontend/`) | nothing |
| End-to-end UI (Pixel 7, 412×915) | Playwright | 11 | `npm run e2e` | `npx playwright install chromium` |

Run the full backend suite offline: `cd backend && .venv/Scripts/python -m pytest -m "not ml"` (286 tests, ~30 s).

## How the fast suites stay fast and deterministic
`tests/conftest.py` sets `PLANTIQ_FAKE_ML=1`, a throw-away SQLite DB, empty LLM keys and an Open-Meteo mock transport
before importing the app. `app/services/fakes.py` provides a deterministic CNN (hash-based), a keyword retriever,
an LLM that records prompts (used by prompt-injection tests) and a fake STT. Each test starts with fresh tables.

## What is covered
**Unit** — Argon2/legacy hashes, password policy, JWT tampering/`alg=none`/expiry/audience, refresh token hashing, secret
redaction, prompt sanitising, phone/unit/price normalisation tables, listing and registration validation, image guard
(EXIF/GPS stripping, polyglots, bombs, sizes, traversal), audio sniffing, RRF/MMR/sigmoid maths, chunking (abbreviations,
decimals, headings, overlap, topics), query expansion, dosage audit, RAG profiles, the real `HybridRetriever` with a toy
embedder, Open-Meteo parsing/risk/spray window/cache/no-mock rule, language router (Kannada/Kanglish/English), coordinate
extraction, weather intent, LLM provider fallback/retry/truncation, advisory (blended, offline, Kannada).

**Integration** — every endpoint: register/login (username/email/phone, original payload shape), lockout, refresh rotation
and reuse detection, logout/logout-all/sessions, profile/password/delete account, predict (cache scoping, Kannada, CNN failure),
scan history filters/soft delete/restore/purge, chat (threads, history in prompt, image upload, base64, media reuse, scan
hand-off, weather with/without location, offline reply, rename/delete, isolation), marketplace (units, photos, filters,
haversine sort, owner rules, report-once, quota), voice, environment, media, system info, SPA fallback, `/api` alias.

**Functional** — farmer journey (voice → scan → chat hand-off → history undo → stats), seller/buyer journey, account lifecycle.

**Security** — 401 on every private endpoint, malformed/forged tokens, IDOR on scans/listings/media, rate limits, lockout
bypass attempts, body-size limit, upload attacks, SQL-injection strings, stored XSS, prompt injection fencing, secret leak
redaction, security headers, HSTS, CORS, error leakage, password never logged, audit events, unsafe production config.

**Non-functional** — latency budgets (health, auth, predict pipeline overhead), Argon2 cost bounds, 500-listing scale,
40 concurrent mixed requests with no lost writes, retriever throughput, gzip, media downscaling, consistent error JSON.

**Frontend** — EN/KN dictionary parity and placeholders, server-URL normalisation (dynamic backend), validation mirrors,
formatting, XSS-safe markdown, password widgets, listing card, risk banner (word + level, not colour only), palette/dark mode,
undo toast timing, API client (base URL, bearer, refresh-once-on-401, error mapping, network errors).

**E2E (Playwright, real backend with fake ML)** — auth (validation, sign-up, wrong password, sign-in), username availability,
scan → diagnosis → chat → threads → history delete/undo → details, chat with photo from history, marketplace (validation sheet
focuses the field, publish with units/photo/caption, filter counts, search, edit, delete), buyer report flow (two users),
Kannada/palette/dark/server ping, password change + devices, accessibility sweep on all tabs (no horizontal scroll, every
control labelled, buttons ≥40 px), APK first-run server setup (simulated Android bridge), Satoshi font bundled.

## Real-model verification (manual run, 2026-10-25, RTX 3070 Laptop)
| Sample leaf | Predicted | Confidence | Top RAG match |
|---|---|---|---|
| rust | Rust | 100.0 % | 0.93 |
| cercospora | Cerscospora | 99.6 % | 0.95 |
| miner | Miner | 99.5 % | 0.84 |
| phoma | Phoma | 99.7 % | 0.78 |
| healthy | Healthy | 100.0 % | — |

End-to-end diagnosis ≈ 6 s (CNN + Open-Meteo + bge-m3/reranker + Gemini). Gemini 429s fall through to Groq.
Local Svarah English STT and IndicConformer Kannada STT load on CUDA (first load 20–40 s).

## Not covered / limitations
- APK not exercised on a device or emulator here (no hypervisor on this machine) — verified statically with `aapt2`
  (package, permissions, bundled assets). Install on a phone to test camera/mic/GPS permission prompts.
- Real speech accuracy was not measured (no recorded farmer audio in the repo).

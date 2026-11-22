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
profile and all sheets; EN/KN dictionaries (425 keys each); 5 palettes × light/dark; XSS-safe markdown.
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

## 2026-10-25 · Documentation & language switch
**Done**
- Language switch (EN ⇄ ಕನ್ನಡ) now on every screen's top bar (History, Profile, Chat included) and inside every bottom sheet;
  the button names the target language. New E2E test switches language mid-form.
- `docs/`: project overview, user flows (demo script), system architecture (diagrams, data model, request lifecycle),
  technical documents for Module 1 CNN, Module 2 RAG + environmental data, Module 3 Chatbot, Module 4 Market discovery,
  platform (accounts, APK, languages, design), capstone panel Q&A guide.
- SECURITY.md rewritten: platform-wide measures + per-module measures, each mapped to the test that verifies it.
- TESTING.md is now a generated matrix (`scripts/test_matrix.py` runs every suite and reads the JUnit reports):
  **354 / 354 passed** (backend 286, real-model 4, vitest 52, Playwright 12).

## 2026-10-25 · Production naming
- Android package renamed `ai.plantiq.claude` → **`ai.plantiq`** (applicationId, namespace, MainActivity, strings, Capacitor config).
- APK outputs renamed: `dist/PlantIQ.apk`, `release/PlantIQ-3.0.0.apk`, `dist/PlantIQ-release-unsigned.apk`.
- Default Postgres database `plantiq_claude` → `plantiq_app` (kept separate from the original app's `plantiq` database).
- Note: a phone with the old `ai.plantiq.claude` build installed sees this as a different app — uninstall the old one.

## 2026-10-25 · Repository restructure
- PlantIQ v3 (previously `cleaned/claude-plantiq/`) moved to the **repository root**.
- The original "cleaned" app moved to **`og/`** (its tracked `mobile/node_modules` dropped; regenerate with `npm install`).
- The first root-level prototype (`backend/`, `cnn/`, `rag/`, `stitched/`, `model-comparator/`, `ppt/`, `mobile_app/`) removed
  from the tree; it remains in git history (no history rewritten). A local copy including untracked files was kept outside
  the repo in `D:\end-capstone-project-old-root-backup`.

## 2026-11-21 — Comparison study (compare/), paper Module 1 results, one-column paper, project summary
- **compare/** (new, self-contained): dataset audit of JMuBEN (58,549 files → 3,756 byte-unique → 861 source patches;
  a random split leaks 99.96 % of test files), leak-free stratified group 5-fold CV, notebooks for the current ResNet-50
  recipe (R0), the revised recipe (V2), GoogLeNet TL (Anudeep K.S. et al.), YOLOv8s-cls (Selva Kumar et al.) and the
  deployed weights; benchmark with group-bootstrap CIs, McNemar, ECE, confidence-gate and latency.
- **CNN results (out-of-fold macro-F1):** GoogLeNet 0.988, YOLOv8s-cls 0.985, PlantIQ V2 0.970, R0 0.963, deployed 0.975
  (reference only, trained on an unknown split). V2 passes the pre-registered replacement rule against the deployed
  weights; the lighter baselines are at least as accurate on this dataset.
- **RAG notebooks** reworked for Gemini + Groq only (Gemini 3.x thinking setting fixed: `thinkingLevel` instead of
  `thinkingBudget`), Karnataka-focused automatic question set, one judge call per answer. Smoke-tested; real run pending.
- **IEEE paper:** text moved to `IEEE-Paper/paper_content.tex`; `main.tex` (two columns) and `main_onecol.tex`
  (one column) both input it. Module 1 sections, Table VII and Figs. 4-5 now use real results; Modules 2-3 still mock.
- **summary/**: one-page project summary (35.tex/35.pdf, figures 35_1.png, 35_2.png).
- Tests: no backend/frontend code changed; compare/ notebooks all pass the smoke run (`PLANTIQ_SMOKE=1`).

## 2026-11-22 — Chat retrieval: full English question instead of keywords
- **Router** (`services/lang_router.py`): `search_query_english` is now one short, self-contained English question
  (meaning-preserving; keeps crop, disease, symptoms, negations, quantities, timing, question type) instead of a keyword
  list. Kannada / Kanglish questions are still answered directly in Kannada script; nothing is translated back.
- **Chat** (`services/chat.py`): the router's English question is also passed as `rerank_query`, so the cross-encoder
  scores the plain question while keyword prefixes (weather / disease) only widen dense+BM25 recall — the same split the
  advisory path already used. The heuristic fallback now uses the cleaned message.
- Fake LLM router output updated to a full question; docs/modules/module-3-chatbot.md §2.1 updated.
- Tests: +2 (`test_router_asks_for_full_english_question_not_keywords`,
  `test_kannada_question_retrieves_with_english_question_and_reranks_on_it`). Backend fast suite **288 passed**
  (4 ml deselected). Run in a temporary venv because `backend/.venv` is missing on this machine; ML, vitest and
  Playwright suites not re-run (no frontend change); TESTING.md not regenerated.
- Open: measure keywords vs full question vs raw Kannada (bge-m3) on the Kannada question set in compare/03_rag.

## 2026-11-22 — RAG benchmark (no API), Kannada router included, paper Module 2 results
- Question set: 54 English + 21 Kannada Karnataka coffee questions written from the KB with verified gold evidence
  (`compare/03_rag/make_questions.py`); no Phoma (its only KB document extracts as garbled text).
- Retrieval (no API; Kannada router outputs for backend b421009 stored in `router_outputs.jsonl`): PlantIQ Recall@3
  0.813 vs Selva Kumar dense 0.500 (Kannada 0.857 vs 0.095; 0.524 with the router offline). Topic filter + MMR lowers
  Recall@3 vs rerank alone (0.893, p=0.014).
- Generation (same LLM for all systems; answers and per-answer scores by Claude Opus 5.5 from the exported prompts,
  stored in `compare/03_rag/answers/`): correctness PlantIQ 0.898, Selva Kumar 0.824, no retrieval 0.611; unsupported
  doses 1.9% / 0% / 20.4%.
- Paper: Module 2 protocol, Section IX-C, Table VIII, Figs. 6-7 and abstract updated (both layouts). Module 3 still mock.

## 2026-11-22 — RAG fixes found by the benchmark (app + paper)
- **Dose audit** (`rag/query.py`): number words are converted to digits ("Four litres" = "4 L"); fixes a false
  "check doses" warning; doses written in words are now audited too.
- **Retrieval last stage** (`rag/retriever.py`): the hard disease-topic filter + MMR is replaced by a soft topic preference
  (+0.1 for ordering only) and near-duplicate removal (Jaccard ≥ 0.8). The benchmark showed the old stage discarding
  answers (e.g. the Bordeaux recipe tagged "nutrition").
- Tests: 3 new unit tests (number words, near-duplicate removal, soft topic preference), 1 updated; fast suite 290/290 pass
  (run in a new `backend/.venv` that reuses compare/.venv's PyTorch via a .pth file).
- Benchmark re-run: Recall@3 0.813 → 0.867 (Kannada 0.857 → 0.905); 23 affected PlantIQ answers regenerated and re-scored;
  correctness 0.898 → 0.944 (vs Selva Kumar 0.824, p = 0.021 now significant); unsupported doses 1.9% → 0%.
- Paper (both layouts), docs/modules/module-2-rag-environment.md, architecture and panel docs, README updated.

## 2026-11-22 — Chatbot (Module 3) benchmark; paper finalised (no mock data)
- `compare/05_chat/`: 43 test conversations (53 turns) — follow-ups, Kannada/Kanglish, leaf photos + past scans,
  weather with/without location, greetings, prompt injection. `plantiq_chat_snapshot` is checked identical to backend
  `chat.process_message` on 20 turns (`verify_snapshot.py`). Baseline: Selva Kumar pipeline as a LangChain
  ConversationalRetrievalChain (+ YOLOv8s-cls for photos). Weather: recorded Open-Meteo responses. Speech not tested.
- Results (same LLM, answers/judgments by Claude Opus 5.5): expected behaviour 43/43 vs 15/43 (p < 1e-6);
  correctness 0.88 vs 0.38 on 29 knowledge questions; Kannada script 17/17; live weather values 6/6; pipeline without
  LLM median 0.26 s.
- Found in PlantIQ (not fixed yet): router ignores history (2/10 follow-ups wrong: Bordeaux pH); weather keywords fire
  on Kannada compounds ಹೂಮಳೆ / ಪರಿಸರ ಸ್ನೇಹಿ (2/35); offline reply for Kannada users is English excerpts (1/17 Kannada).
- Paper (both layouts): Module 3 protocol, Section IX-D with Table IX, abstract, limitations, conclusion; DRAFT banner,
  mock table, mock speech-recognition figure and email/acknowledgement placeholders removed; Sapkota bib entry fixed.

## 2026-11-22 — Chatbot fixes from the Module 3 benchmark; paper references, emails, acknowledgment
- **Router with history** (`lang_router.router_prompt`, `chat.py`): the last two exchanges go to the router as a cleaned,
  fenced `<history>` block; prompt unchanged without history (advisory path and Module 2 benchmark unaffected).
- **Weather intent** (`chat.is_weather_query`): keywords match at the start of a word; eco-friendly phrases excluded.
- **Offline Kannada** (`knowledge.py`): Kannada offline replies and Kannada disease cards cite document pages instead of
  English excerpts; a disease named in the message selects its offline card.
- Tests: +15 (unit, integration, security); backend fast suite **305 passed** (4 ml deselected).
  TESTING.md not regenerated: `frontend/node_modules` is not installed on this machine, so the matrix script could
  not run Vitest/Playwright (frontend unchanged); rerun `python scripts/test_matrix.py` after `npm install`.
- Benchmark re-run (`compare/05_chat/make_snapshot.py` regenerates the snapshot; verified identical on 20 turns;
  10 follow-up router outputs updated; 11 changed PlantIQ answers regenerated and re-judged): follow-up evidence
  6/10 → 10/10, follow-up correctness 0.80 → 0.90 (one Kannada follow-up regressed), weather false flags 2 → 0,
  Kannada offline replies 2/17 → 17/17, overall correctness 0.88 → 0.91 (vs 0.38 for the LangChain baseline).
  Before-fix results kept in `compare/results/chat/chat_before_fix.json`.
- Paper (both layouts): Module 3 section reports the faults, fixes and re-run; author emails; acknowledgment sentence;
  the 11 references added earlier (ImageNet, BM25, RRF, MMR, bge-m3, FAISS, reranker, Whisper, RAGAS, haversine,
  Argon2) removed with their citations; JMuBEN dataset citation kept (CC BY licence requires it).

## 2026-11-22 — Paper humanized; short paper (two layouts, 12 pt)
- Full paper (`paper_content.tex`): edited with the humanizer skill (bold contribution labels, roadmap paragraph and
  staged phrases removed; stock words replaced); stale statements fixed (router output is one English question; test
  count 373 with backend re-run at 305); reference balancing now only in the two-column build (one-column 15 → 14 pages).
- Short paper (`short_content.tex`, `short.tex`, `short_onecol.tex`): 12 pt, 6 / 7 pages; abstract, method, evaluation
  setup, the three comparisons (Tables II-IV, Fig. 2), limitations, conclusion; same authors and references.
- Hidden Unicode: sources are plain ASCII; equations rewritten (no large braces, `\hat`, `
eq`) so none of the four
  PDFs yields private-use, combining or format characters in copied text.


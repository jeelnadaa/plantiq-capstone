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
- Created `backend/.venv` (Python 3.11) and started dependency install.

**Security gaps found in the original** (to fix in the rebuild): anonymous listing ownership hole, raw-HTML
markdown rendering (XSS), plaintext long-lived session tokens, no login rate limit/lockout, `pickle.load` on
RAG index, base64 photos in DB.

**Tests**: n/a (planning).

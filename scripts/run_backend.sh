#!/usr/bin/env bash
# Start the PlantIQ backend (Linux / macOS / Git Bash). Phones on the same Wi-Fi use the "Phone:" address it prints.
set -euo pipefail
cd "$(dirname "$0")/../backend"
PY=python3.11; command -v "$PY" >/dev/null || PY=python3
if [ ! -d .venv ]; then
  echo "[setup] creating virtual environment"
  "$PY" -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi
BIN=.venv/bin; [ -d .venv/Scripts ] && BIN=.venv/Scripts
[ -f .env ] || { cp .env.example .env; echo "[setup] created backend/.env — add GEMINI_API_KEY / GROQ_API_KEY"; }
[ -f static/index.html ] || "$BIN/python" ../scripts/sync_web.py || echo "[warn] web UI not built — API still works"
"$BIN/python" scripts/prepare_models.py
exec "$BIN/python" run.py --port "${PORT:-8000}" --warm "$@"

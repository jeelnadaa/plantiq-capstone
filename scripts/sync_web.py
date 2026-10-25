"""Build the React app and copy it into backend/static so the backend serves the web UI at /.

    python scripts/sync_web.py            # npm run build + copy
    python scripts/sync_web.py --no-build # copy an existing frontend/dist
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
DIST = FRONTEND / "dist"
STATIC = ROOT / "backend" / "static"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-build", action="store_true")
    args = parser.parse_args()
    if not args.no_build:
        npm = "npm.cmd" if sys.platform == "win32" else "npm"
        subprocess.run([npm, "run", "build"], cwd=FRONTEND, check=True)
    if not (DIST / "index.html").exists():
        sys.exit("frontend/dist/index.html not found — build the frontend first")
    shutil.rmtree(STATIC, ignore_errors=True)
    shutil.copytree(DIST, STATIC)
    print(f"Copied {DIST} -> {STATIC}")


if __name__ == "__main__":
    main()

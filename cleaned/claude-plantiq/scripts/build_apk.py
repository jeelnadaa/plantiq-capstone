"""Build the PlantIQ Android APK.

    python scripts/build_apk.py            # debug-signed APK  → dist/PlantIQ.apk
    python scripts/build_apk.py --release  # unsigned release APK (sign with your keystore, see docs/DEPLOYMENT.md)

Steps: npm run build (frontend) → copy dist into mobile/www → cap sync android → gradle assemble.
The backend URL is NOT baked in: the app asks for it on first launch and it can be changed any time.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND, MOBILE = ROOT / "frontend", ROOT / "mobile"
ANDROID = MOBILE / "android"
WIN = sys.platform == "win32"


def find_java_home() -> str | None:
    if os.environ.get("JAVA_HOME") and Path(os.environ["JAVA_HOME"]).is_dir():
        return os.environ["JAVA_HOME"]
    roots = [Path(r"C:\Program Files\Java"), Path(r"C:\Program Files\Eclipse Adoptium"), Path(r"C:\Program Files\Android\Android Studio\jbr")]
    for r in roots:
        if (r / "bin" / "java.exe").exists():
            return str(r)
        if r.is_dir():
            for sub in sorted(r.iterdir(), reverse=True):
                if (sub / "bin" / ("java.exe" if WIN else "java")).exists():
                    return str(sub)
    return None


def find_android_sdk() -> str | None:
    for key in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(key) and Path(os.environ[key]).is_dir():
            return os.environ[key]
    cand = Path.home() / ("AppData/Local/Android/Sdk" if WIN else "Android/Sdk")
    return str(cand) if cand.is_dir() else None


def run(cmd: list[str], cwd: Path, env: dict | None = None) -> None:
    print(f"$ {' '.join(cmd)}  (in {cwd.relative_to(ROOT)})")
    subprocess.run(cmd, cwd=cwd, check=True, env=env, shell=WIN)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", action="store_true")
    ap.add_argument("--skip-web", action="store_true")
    args = ap.parse_args()

    env = os.environ.copy()
    java, sdk = find_java_home(), find_android_sdk()
    if not java or not sdk:
        sys.exit(f"JDK 17+ and the Android SDK are required (JAVA_HOME={java}, ANDROID_HOME={sdk}).")
    env["JAVA_HOME"], env["ANDROID_HOME"], env["ANDROID_SDK_ROOT"] = java, sdk, sdk
    # JDK on Windows creates NIO pipes with Unix-domain sockets in %TEMP%; a long or unusual TEMP path makes
    # Gradle fail with "Unable to establish loopback connection". Use a short temp dir inside the project.
    short_tmp = ANDROID / ".jtmp"
    short_tmp.mkdir(exist_ok=True)
    env["JAVA_TOOL_OPTIONS"] = f'-Djdk.net.unixdomain.tmpdir="{short_tmp}" -Djava.io.tmpdir="{short_tmp}"'
    (ANDROID / "local.properties").write_text(f"sdk.dir={sdk.replace(os.sep, '/')}\n", encoding="utf-8")

    npm = "npm.cmd" if WIN else "npm"
    npx = "npx.cmd" if WIN else "npx"
    if not args.skip_web:
        run([npm, "run", "build"], FRONTEND, env)
    www = MOBILE / "www"
    shutil.rmtree(www, ignore_errors=True)
    shutil.copytree(FRONTEND / "dist", www)
    if not (MOBILE / "node_modules").exists():
        run([npm, "install", "--no-audit", "--no-fund"], MOBILE, env)
    run([npx, "cap", "sync", "android"], MOBILE, env)

    gradlew = str(ANDROID / ("gradlew.bat" if WIN else "gradlew"))
    task = "assembleRelease" if args.release else "assembleDebug"
    run([gradlew, task, "--no-daemon"], ANDROID, env)

    flavor = "release" if args.release else "debug"
    out_dir = ANDROID / "app" / "build" / "outputs" / "apk" / flavor
    apks = sorted(out_dir.glob("*.apk"))
    if not apks:
        sys.exit(f"No APK produced in {out_dir}")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / ("PlantIQ-release-unsigned.apk" if args.release else "PlantIQ.apk")
    shutil.copy2(apks[0], target)
    print(f"\nAPK ready: {target}  ({target.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()

import os
import sys
import shutil
import subprocess

def rebuild():
    print("[PlantIQ] Starting 1-Click APK Rebuild...")
    base_dir = os.path.dirname(os.path.abspath(__file__)) # cleaned/mobile
    root_dir = os.path.dirname(base_dir) # cleaned
    frontend_dir = os.path.join(root_dir, "frontend")
    www_dir = os.path.join(base_dir, "www")
    android_dir = os.path.join(base_dir, "android")

    # 0. Dynamically resolve JAVA_HOME and Android SDK
    if "JAVA_HOME" not in os.environ or not os.path.isdir(os.environ.get("JAVA_HOME", "")):
        candidates = [
            r"C:\Program Files\Java\jdk-21.0.12",
            r"C:\Program Files\Java\latest",
            r"C:\Program Files\Java\jdk-21.0.11",
        ]
        java_root = r"C:\Program Files\Java"
        if os.path.exists(java_root):
            for item in sorted(os.listdir(java_root), reverse=True):
                full_p = os.path.join(java_root, item)
                if os.path.isdir(full_p) and item not in candidates:
                    candidates.append(full_p)
        for cand in candidates:
            if os.path.exists(cand):
                os.environ["JAVA_HOME"] = cand
                break
    print(f"[*] Using JAVA_HOME: {os.environ.get('JAVA_HOME', 'System Default')}")

    if "ANDROID_HOME" not in os.environ or not os.path.isdir(os.environ.get("ANDROID_HOME", "")):
        sdk_cand = os.path.expanduser(r"~\AppData\Local\Android\Sdk")
        if os.path.exists(sdk_cand):
            os.environ["ANDROID_HOME"] = sdk_cand
            os.environ["ANDROID_SDK_ROOT"] = sdk_cand
    print(f"[*] Using ANDROID_HOME: {os.environ.get('ANDROID_HOME', 'Configured via local.properties')}")

    # 1. Update www/static
    print("[1/4] Syncing frontend assets...")
    shutil.rmtree(os.path.join(www_dir, "static"), ignore_errors=True)
    shutil.copytree(os.path.join(frontend_dir, "static"), os.path.join(www_dir, "static"))

    # 2. Update www HTML templates
    print("[2/4] Updating template links...")
    templates_dir = os.path.join(frontend_dir, "templates")
    for fname in os.listdir(templates_dir):
        if not fname.endswith(".html"): continue
        with open(os.path.join(templates_dir, fname), "r", encoding="utf-8") as f:
            html = f.read()

        html = html.replace('href="/static/', 'href="./static/')
        html = html.replace('src="/static/', 'src="./static/')
        html = html.replace('href="/"', 'href="./index.html"')
        html = html.replace('href="/chat"', 'href="./chat.html"')
        html = html.replace('href="/marketplace"', 'href="./marketplace.html"')
        html = html.replace('href="/history"', 'href="./history.html"')
        html = html.replace('href="/profile"', 'href="./profile.html"')
        html = html.replace('href="/auth"', 'href="./auth.html"')
        html = html.replace('window.location.replace("/auth")', 'window.location.replace("./auth.html")')
        html = html.replace('window.location.replace("/")', 'window.location.replace("./index.html")')
        html = html.replace('window.location.href = "/chat"', 'window.location.href = "./chat.html"')

        with open(os.path.join(www_dir, fname), "w", encoding="utf-8") as f:
            f.write(html)

    # 3. Capacitor Sync
    print("[3/4] Syncing Capacitor Android assets...")
    subprocess.run(["npx.cmd", "cap", "sync", "android"], cwd=base_dir, check=True, shell=True)

    # 4. Gradle Assemble Debug APK
    print("[4/4] Compiling Android APK with Gradle...")
    gradle_cmd = os.path.join(android_dir, "gradlew.bat")
    subprocess.run([gradle_cmd, "assembleDebug"], cwd=android_dir, check=True, shell=True)

    # 5. Copy Output APK
    out_apk = os.path.join(android_dir, "app", "build", "outputs", "apk", "debug", "app-debug.apk")
    final_apk = os.path.join(base_dir, "PlantIQ.apk")
    if os.path.exists(out_apk):
        shutil.copy2(out_apk, final_apk)
        print("\n" + "="*50)
        print("SUCCESS! New APK generated successfully:")
        print(f"Path: {final_apk}")
        print("="*50 + "\n")
    else:
        print("Error: Could not locate generated APK file.")

if __name__ == "__main__":
    rebuild()

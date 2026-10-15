"""
run_app.py
==========
1-Click Launcher for the PlantIQ Dual CNN Model Comparator Web Application.
Starts Uvicorn server on http://localhost:8501 and opens the browser.
"""

import os
import sys
import webbrowser
import uvicorn

# Ensure model-comparator is on the python search path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def main():
    port = int(os.getenv("PORT", "8501"))
    host = os.getenv("HOST", "127.0.0.1")
    url = f"http://{host}:{port}"

    print("=" * 65)
    print("🌿 PlantIQ: Dual CNN Model Comparator & Benchmark Suite")
    print("=" * 65)
    print(f"[*] Starting Comparator Web App on: {url}")
    print("    - Model A: Old PyTorch ResNet-50 (96.40% Benchmark Accuracy)")
    print("    - Model B: New Custom 4-Block Keras CNN (89.19% Benchmark Accuracy)")
    print("=" * 65)

    # Open browser automatically after a short delay
    try:
        webbrowser.open(url)
    except Exception:
        pass

    uvicorn.run(
        "backend.app:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()

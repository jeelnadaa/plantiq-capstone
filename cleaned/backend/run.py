import uvicorn
import os
import sys

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    port = int(os.getenv("PORT", 8000))
    print(f"\n=======================================================")
    print(f"🚀 PlantIQ (Cleaned & Refactored v2.0) Starting...")
    print(f"📡 API & Web Interface available at: http://127.0.0.1:{port}")
    print(f"📖 Interactive OpenAPI Docs at: http://127.0.0.1:{port}/docs")
    print(f"=======================================================\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)

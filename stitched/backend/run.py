import uvicorn
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print("\n=======================================================")
    print(f"🚀 PlantIQ (Stitched Maximalist Edition) Starting...")
    print(f"📡 API & Web Interface available at: http://127.0.0.1:{port}")
    print(f"📖 Interactive OpenAPI Docs at: http://127.0.0.1:{port}/docs")
    print("=======================================================\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

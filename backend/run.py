import uvicorn
import os

if __name__ == "__main__":
    print("Starting PlantIQ FastAPI Backend Server on http://0.0.0.0:8000...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.database import Base, engine
from app.api.router import api_router

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes under /api
app.include_router(api_router, prefix=settings.API_V1_STR)

# Frontend directories
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))

@app.get("/scanner", include_in_schema=False)
def serve_scanner():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))

@app.get("/chat", include_in_schema=False)
def serve_chat():
    return FileResponse(os.path.join(TEMPLATES_DIR, "chat.html"))

@app.get("/marketplace", include_in_schema=False)
def serve_marketplace():
    return FileResponse(os.path.join(TEMPLATES_DIR, "marketplace.html"))

@app.get("/history", include_in_schema=False)
def serve_history():
    return FileResponse(os.path.join(TEMPLATES_DIR, "history.html"))

@app.get("/profile", include_in_schema=False)
def serve_profile():
    return FileResponse(os.path.join(TEMPLATES_DIR, "profile.html"))

@app.get("/auth", include_in_schema=False)
def serve_auth():
    return FileResponse(os.path.join(TEMPLATES_DIR, "auth.html"))

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "version": settings.VERSION}

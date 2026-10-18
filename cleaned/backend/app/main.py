import os
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings
from app.core.database import Base, engine, init_database
from app.api.router import api_router
import app.models  # Register all SQLAlchemy models

logger = logging.getLogger("plantiq.server")

# Initialize database schema with auto-creation, auto-migration, and SQLite fallback
init_database()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Explicit CORS Allowlist Middleware
allowed_origins = settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Non-Functional Security: Security Response Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Safe Global Unhandled Exception Handler (Prevents raw stack trace / secret leaks)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
        raise exc
    error_ref = uuid.uuid4().hex[:12]
    logger.error(f"[Unhandled Error ref={error_ref}] {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error. Reference ID: {error_ref}",
            "status": "error",
            "reference_id": error_ref
        }
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

"""PlantIQ API application factory."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.misc import public_media_router
from app.api.router import api_router
from app.core.config import settings
from app.core.db import SessionLocal, init_db
from app.core.errors import install_error_handlers
from app.core.middleware import SecurityMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(name)s: %(message)s")
log = logging.getLogger("plantiq")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    try:
        from app.api.scans import purge_soft_deleted

        with SessionLocal() as db:
            n = purge_soft_deleted(db)
            if n:
                log.info("Purged %d soft-deleted scans", n)
    except Exception as exc:  # pragma: no cover
        log.warning("Cleanup skipped: %s", exc)
    log.info("PlantIQ %s ready (env=%s, fake_ml=%s)", settings.VERSION, settings.ENV, settings.FAKE_ML)
    yield


def create_app() -> FastAPI:
    docs = not settings.is_production
    app = FastAPI(
        title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan,
        docs_url="/docs" if docs else None, redoc_url="/redoc" if docs else None,
        openapi_url="/openapi.json" if docs else None,
    )
    install_error_handlers(app)

    # Order: outermost first → SecurityMiddleware wraps CORS so even preflight/errors carry security headers.
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS if "*" not in settings.CORS_ORIGINS else ["*"],
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$"
        if not settings.is_production else None,
        allow_credentials=False,  # bearer tokens, no cookies → no CSRF surface
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "Accept-Language", "X-Device",
                       "Bypass-Tunnel-Reminder", "bypass-tunnel-reminder"],
        expose_headers=["X-Request-Id", "Retry-After"],
        max_age=600,
    )
    app.add_middleware(SecurityMiddleware)

    app.include_router(api_router, prefix=settings.API_PREFIX)
    app.include_router(api_router, prefix="/api", include_in_schema=False)  # original client paths
    app.include_router(public_media_router)

    @app.get("/health", tags=["System"])
    @app.get("/api/health", include_in_schema=False)
    def health() -> dict:
        return {"status": "ok", "name": "PlantIQ", "version": settings.VERSION}

    _mount_spa(app)
    return app


def _mount_spa(app: FastAPI) -> None:
    """Serve the built React app (frontend/dist copied to backend/static) at /."""
    static = settings.STATIC_DIR
    index = static / "index.html"
    if (static / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=static / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith(("api/", "media/")):
            return JSONResponse({"detail": "Not found.", "code": "not_found"}, status_code=404)
        candidate = (static / path).resolve()
        if path and candidate.is_file() and static.resolve() in candidate.parents:
            return FileResponse(candidate)
        if index.exists():
            return FileResponse(index, headers={"Cache-Control": "no-cache"})
        return JSONResponse({"name": "PlantIQ API", "version": settings.VERSION,
                             "hint": "Web UI not built. Run: python scripts/sync_web.py"}, status_code=200)


app = create_app()

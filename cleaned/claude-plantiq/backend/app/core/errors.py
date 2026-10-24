"""Uniform error responses: {"detail": ..., "code": ..., "request_id": ...}. No stack traces leak."""
from __future__ import annotations

import logging
import uuid

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

log = logging.getLogger("plantiq.errors")

_CODES = {400: "bad_request", 401: "unauthorized", 403: "forbidden", 404: "not_found", 409: "conflict",
          413: "payload_too_large", 415: "unsupported_media_type", 422: "validation_error", 423: "locked",
          429: "rate_limited", 503: "unavailable"}


def _rid(request: Request) -> str:
    return getattr(request.state, "request_id", None) or uuid.uuid4().hex[:16]


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_error(request: Request, exc: StarletteHTTPException):
        body = {"detail": exc.detail, "code": _CODES.get(exc.status_code, "error"), "request_id": _rid(request)}
        return JSONResponse(status_code=exc.status_code, content=jsonable_encoder(body), headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        errors = []
        for e in exc.errors():
            errors.append({
                "field": ".".join(str(p) for p in e.get("loc", []) if p not in ("body", "query", "path", "form")),
                "message": str(e.get("msg", "Invalid value")).removeprefix("Value error, "),
                "type": e.get("type"),
            })
        log.warning("422 on %s %s: %s", request.method, request.url.path, [(x["field"], x["message"]) for x in errors])
        return JSONResponse(status_code=422, content={
            "detail": errors[0]["message"] if errors else "Invalid request.",
            "errors": errors, "code": "validation_error", "request_id": _rid(request),
        })

    @app.exception_handler(Exception)
    async def unhandled(request: Request, exc: Exception):
        rid = _rid(request)
        log.error("Unhandled error rid=%s on %s %s", rid, request.method, request.url.path, exc_info=exc)
        return JSONResponse(status_code=500, content={
            "detail": f"Something went wrong on the server. Reference: {rid}", "code": "server_error", "request_id": rid,
        })

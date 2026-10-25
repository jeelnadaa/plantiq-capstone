"""ASGI middleware: request id, security headers, request body size limit, global rate limit."""
from __future__ import annotations

import logging
import time
import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.ratelimit import limiter

log = logging.getLogger("plantiq.http")

# The SPA is built by Vite with hashed asset files; no inline scripts are needed.
CSP = (
    "default-src 'self'; "
    "img-src 'self' data: blob:; "
    "media-src 'self' blob:; "
    "style-src 'self' 'unsafe-inline'; "
    "font-src 'self' data:; "
    "script-src 'self'; "
    "connect-src 'self' https: http:; "
    "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'"
)
DOCS_CSP = CSP.replace("script-src 'self'", "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net").replace(
    "style-src 'self' 'unsafe-inline'", "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
).replace("img-src 'self' data: blob:", "img-src 'self' data: blob: https://fastapi.tiangolo.com")


class SecurityMiddleware:
    """Adds request id + security headers, enforces a max body size and a coarse per-IP rate limit."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex[:16]
        scope.setdefault("state", {})["request_id"] = request_id
        path: str = scope.get("path", "")
        started = time.perf_counter()

        # --- body size limit (Content-Length fast path + streaming guard) ---
        headers = {k.decode().lower(): v.decode() for k, v in scope.get("headers", [])}
        declared = headers.get("content-length")
        if declared and declared.isdigit() and int(declared) > settings.MAX_BODY_BYTES:
            await _plain_response(send, 413, b'{"detail":"Request body too large.","code":"payload_too_large"}', request_id)
            return

        # --- coarse global rate limit for API paths ---
        if settings.RATE_LIMIT_ENABLED and path.startswith("/api"):
            client = scope.get("client")
            ip = client[0] if client else "unknown"
            if settings.TRUST_PROXY_HEADERS and headers.get("x-forwarded-for"):
                ip = headers["x-forwarded-for"].split(",")[0].strip()
            allowed, retry = limiter.hit(f"global:{ip}", settings.RATE_LIMIT_DEFAULT_PER_MIN)
            if not allowed:
                await _plain_response(
                    send, 429, b'{"detail":"Too many requests. Please slow down.","code":"rate_limited"}',
                    request_id, extra=[(b"retry-after", str(retry).encode())],
                )
                return

        received = 0

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > settings.MAX_BODY_BYTES:
                    raise _BodyTooLarge()
            return message

        is_docs = path in ("/docs", "/redoc") or path.startswith("/docs/")

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                hdrs = list(message.get("headers", []))
                present = {k.lower() for k, _ in hdrs}
                extra = [
                    (b"x-request-id", request_id.encode()),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"permissions-policy", b"camera=(self), microphone=(self), geolocation=(self), payment=()"),
                    (b"cross-origin-opener-policy", b"same-origin"),
                    (b"content-security-policy", (DOCS_CSP if is_docs else CSP).encode()),
                ]
                if scope.get("scheme") == "https" or headers.get("x-forwarded-proto") == "https":
                    extra.append((b"strict-transport-security", b"max-age=31536000; includeSubDomains"))
                if path.startswith("/api"):
                    extra.append((b"cache-control", b"no-store"))
                hdrs += [(k, v) for k, v in extra if k not in present]
                message["headers"] = hdrs
                status = message.get("status")
                if path.startswith("/api"):
                    log.info("%s %s -> %s (%.0f ms) rid=%s", scope.get("method"), path, status,
                             (time.perf_counter() - started) * 1000, request_id)
            await send(message)

        try:
            await self.app(scope, limited_receive, send_with_headers)
        except _BodyTooLarge:
            await _plain_response(send, 413, b'{"detail":"Request body too large.","code":"payload_too_large"}', request_id)


class _BodyTooLarge(Exception):
    pass


async def _plain_response(send: Send, status: int, body: bytes, request_id: str, extra: list | None = None) -> None:
    await send({
        "type": "http.response.start",
        "status": status,
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode()),
            (b"x-request-id", request_id.encode()),
            (b"x-content-type-options", b"nosniff"),
            *(extra or []),
        ],
    })
    await send({"type": "http.response.body", "body": body})

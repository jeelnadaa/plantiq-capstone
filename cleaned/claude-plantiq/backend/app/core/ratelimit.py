"""Small in-memory sliding-window rate limiter (per process).

Good enough for a single-node deployment; swap the store for Redis if the API is scaled out.
"""
from __future__ import annotations

import math
import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

from app.core.config import settings


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def hit(self, key: str, limit: int, window_s: float = 60.0) -> tuple[bool, int]:
        """Record a hit; returns (allowed, retry_after_seconds)."""
        now = time.monotonic()
        with self._lock:
            q = self._hits[key]
            while q and now - q[0] > window_s:
                q.popleft()
            if len(q) >= limit:
                return False, max(1, math.ceil(window_s - (now - q[0])))
            q.append(now)
            if len(self._hits) > 50_000:  # crude memory guard
                self._hits.clear()
            return True, 0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    if settings.TRUST_PROXY_HEADERS:
        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            return fwd.split(",")[0].strip()[:64]
    return (request.client.host if request.client else "unknown")[:64]


def rate_limit(bucket: str, per_minute: int | None = None):
    """FastAPI dependency: `Depends(rate_limit("auth"))`."""

    def _dep(request: Request) -> None:
        if not settings.RATE_LIMIT_ENABLED:
            return
        limit = per_minute or {
            "auth": settings.RATE_LIMIT_AUTH_PER_MIN,
            "heavy": settings.RATE_LIMIT_HEAVY_PER_MIN,
        }.get(bucket, settings.RATE_LIMIT_DEFAULT_PER_MIN)
        allowed, retry = limiter.hit(f"{bucket}:{client_ip(request)}", limit)
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait a moment and try again.",
                headers={"Retry-After": str(retry)},
            )

    return _dep

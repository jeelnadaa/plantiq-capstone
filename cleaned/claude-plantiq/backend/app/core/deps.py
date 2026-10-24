"""Authentication dependencies."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import TokenError, decode_access_token
from app.core.timeutil import as_aware
from app.models import RefreshToken, User

_UNAUTH = {"WWW-Authenticate": "Bearer"}


def _bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value.strip():
        return None
    return value.strip()


def _resolve_user(token: str, db: Session) -> User:
    try:
        payload = decode_access_token(token)
    except TokenError as exc:
        msg = "Session expired. Please sign in again." if str(exc) == "expired" else "Invalid session."
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, msg, headers=_UNAUTH) from exc
    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session.", headers=_UNAUTH) from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session.", headers=_UNAUTH)
    # Tokens issued before the last password change are void.
    changed = as_aware(user.password_changed_at)
    if changed and payload.get("iat", 0) < int(changed.timestamp()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired. Please sign in again.", headers=_UNAUTH)
    # Logged-out sessions are void immediately, not only when the access token expires.
    sid = payload.get("sid")
    if sid:
        alive = db.scalar(select(RefreshToken.id).where(
            RefreshToken.family_id == sid, RefreshToken.revoked_at.is_(None)).limit(1))
        if not alive:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session ended. Please sign in again.", headers=_UNAUTH)
    return user


def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    token = _bearer(authorization)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Please sign in to continue.", headers=_UNAUTH)
    return _resolve_user(token, db)


def get_optional_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User | None:
    token = _bearer(authorization)
    if not token:
        return None
    try:
        return _resolve_user(token, db)
    except HTTPException:
        return None


def get_session_id(authorization: str | None = Header(None)) -> str | None:
    token = _bearer(authorization)
    if not token:
        return None
    try:
        return decode_access_token(token).get("sid")
    except TokenError:
        return None

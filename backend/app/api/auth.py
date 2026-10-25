"""Sign-up, sign-in, token refresh, sign-out, sessions."""
from __future__ import annotations

import math
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import get_current_user, get_session_id
from app.core.ratelimit import client_ip, limiter, rate_limit
from app.core.security import check_password_policy, hash_password, needs_rehash, verify_password
from app.core.timeutil import as_aware, utcnow
from app.models import RefreshToken, User
from app.schemas.auth import (
    AvailabilityOut,
    LoginIn,
    PasswordStrengthIn,
    PasswordStrengthOut,
    RefreshIn,
    RegisterIn,
    SessionOut,
    TokenOut,
    UserOut,
)
from app.schemas.common import normalize_phone
from app.services.auth_service import active_sessions, audit, issue_session, revoke_all, revoke_family, rotate_session

router = APIRouter(prefix="/auth", tags=["Authentication"])

POLICY_MESSAGES = {
    "min_length": "Password must be at least 8 characters.",
    "max_length": "Password must be at most 128 characters.",
    "letters_and_digits": "Password must contain letters and numbers.",
    "too_common": "This password is too common. Choose another one.",
    "same_as_username": "Password must not be the same as your username.",
}


def _device(request: Request, given: str | None) -> str:
    if given:
        return given[:160]
    ua = request.headers.get("user-agent", "")
    if "Android" in ua:
        return "Android phone"
    if "iPhone" in ua or "iPad" in ua:
        return "iPhone / iPad"
    if "Windows" in ua:
        return "Windows browser"
    if "Mac OS" in ua:
        return "Mac browser"
    return (ua[:60] or "Unknown device")


def _find_user(db: Session, identifier: str) -> User | None:
    ident = identifier.strip().lower()
    phone = None
    try:
        phone = normalize_phone(ident)
    except ValueError:
        pass
    clauses = [func.lower(User.username) == ident, func.lower(User.email) == ident]
    if phone:
        clauses.append(User.phone == phone)
    return db.scalar(select(User).where(or_(*clauses)))


@router.post("/register", response_model=TokenOut, status_code=201, dependencies=[Depends(rate_limit("auth"))])
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    ip = client_ip(request)
    policy = check_password_policy(payload.password, payload.username)
    if not policy.ok:
        raise HTTPException(422, POLICY_MESSAGES[policy.problems[0]])
    conflicts = []
    if db.scalar(select(User.id).where(func.lower(User.username) == payload.username)):
        conflicts.append("username")
    if payload.email and db.scalar(select(User.id).where(func.lower(User.email) == payload.email)):
        conflicts.append("email")
    if payload.phone and db.scalar(select(User.id).where(User.phone == payload.phone)):
        conflicts.append("phone")
    if conflicts:
        audit(db, "register_conflict", None, ip, ",".join(conflicts))
        db.commit()
        label = {"username": "username", "email": "email", "phone": "mobile number"}[conflicts[0]]
        raise HTTPException(409, f"An account with this {label} already exists.")
    user = User(
        username=payload.username, full_name=payload.full_name, email=payload.email, phone=payload.phone,
        hashed_password=hash_password(payload.password), preferred_language=payload.preferred_language,
        last_login_at=utcnow(),
    )
    db.add(user)
    db.flush()
    out = issue_session(db, user, remember=payload.remember, device=_device(request, payload.device), ip=ip)
    audit(db, "register", user.id, ip)
    db.commit()
    return out


@router.post("/login", response_model=TokenOut, dependencies=[Depends(rate_limit("auth"))])
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    ip = client_ip(request)
    user = _find_user(db, payload.identifier)
    now = utcnow()

    if user and user.locked_until and as_aware(user.locked_until) > now:
        retry = math.ceil((as_aware(user.locked_until) - now).total_seconds())
        audit(db, "login_locked", user.id, ip)
        db.commit()
        raise HTTPException(
            status.HTTP_423_LOCKED,
            {"message": "Too many wrong attempts. Your account is locked for a short while.", "retry_after": retry},
            headers={"Retry-After": str(retry)},
        )

    if not user or not user.is_active or not verify_password(payload.password, user.hashed_password if user else None):
        if user:
            user.failed_logins = (user.failed_logins or 0) + 1
            if user.failed_logins >= settings.LOGIN_MAX_FAILURES:
                user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
                user.failed_logins = 0
                audit(db, "account_locked", user.id, ip)
        audit(db, "login_failed", user.id if user else None, ip, f"identifier={payload.identifier[:40]}")
        db.commit()
        # Per-identifier throttle as well, so rotating IPs does not help guessing one account.
        limiter.hit(f"login-id:{payload.identifier.lower()[:60]}", 10**9)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect login details. Check and try again.")

    user.failed_logins = 0
    user.locked_until = None
    user.last_login_at = now
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(payload.password)  # upgrade legacy bcrypt/PBKDF2 to Argon2id
    out = issue_session(db, user, remember=payload.remember, device=_device(request, payload.device), ip=ip)
    audit(db, "login", user.id, ip)
    db.commit()
    return out


@router.post("/refresh", response_model=TokenOut, dependencies=[Depends(rate_limit("auth", 60))])
def refresh(payload: RefreshIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    return rotate_session(db, payload.refresh_token, client_ip(request))


@router.post("/logout", status_code=204)
def logout(request: Request, user: User = Depends(get_current_user), sid: str | None = Depends(get_session_id),
           db: Session = Depends(get_db)) -> None:
    if sid:
        revoke_family(db, sid)
    audit(db, "logout", user.id, client_ip(request))
    db.commit()


@router.post("/logout-all", status_code=204)
def logout_all(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> None:
    revoke_all(db, user.id)
    audit(db, "logout_all", user.id, client_ip(request))
    db.commit()


@router.get("/sessions", response_model=list[SessionOut])
def list_sessions(user: User = Depends(get_current_user), sid: str | None = Depends(get_session_id),
                  db: Session = Depends(get_db)) -> list[SessionOut]:
    return [SessionOut(id=r.id, device=r.device, ip=r.ip, created_at=r.created_at, last_used_at=r.last_used_at,
                       current=(r.family_id == sid)) for r in active_sessions(db, user.id)]


@router.delete("/sessions/{session_id}", status_code=204)
def revoke_session(session_id: int, request: Request, user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)) -> None:
    row = db.get(RefreshToken, session_id)
    if not row or row.user_id != user.id:
        raise HTTPException(404, "Session not found.")
    revoke_family(db, row.family_id)
    audit(db, "session_revoked", user.id, client_ip(request), f"session={session_id}")
    db.commit()


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.get("/availability", response_model=AvailabilityOut, dependencies=[Depends(rate_limit("auth", 60))])
def availability(field: str = Query(pattern="^(username|email|phone)$"), value: str = Query(max_length=254),
                 db: Session = Depends(get_db)) -> AvailabilityOut:
    from app.schemas.auth import USERNAME_RE

    v = value.strip().lower()
    if field == "username":
        if not USERNAME_RE.fullmatch(v):
            return AvailabilityOut(field=field, available=False, reason="invalid")
        taken = db.scalar(select(User.id).where(func.lower(User.username) == v))
    elif field == "email":
        taken = db.scalar(select(User.id).where(func.lower(User.email) == v))
    else:
        try:
            v = normalize_phone(v)
        except ValueError:
            return AvailabilityOut(field=field, available=False, reason="invalid")
        taken = db.scalar(select(User.id).where(User.phone == v))
    return AvailabilityOut(field=field, available=not taken, reason="taken" if taken else None)


@router.post("/password-strength", response_model=PasswordStrengthOut)
def password_strength(payload: PasswordStrengthIn) -> PasswordStrengthOut:
    res = check_password_policy(payload.password, payload.username)
    return PasswordStrengthOut(ok=res.ok, score=res.score, problems=res.problems)

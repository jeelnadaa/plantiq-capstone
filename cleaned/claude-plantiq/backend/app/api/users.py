"""Profile: view/update, change password, stats, delete account (GDPR)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.auth import POLICY_MESSAGES
from app.core.db import get_db
from app.core.deps import get_current_user, get_session_id
from app.core.ratelimit import client_ip, rate_limit
from app.core.security import check_password_policy, hash_password, verify_password
from app.core.timeutil import utcnow
from app.models import ChatThread, CropListing, Scan, User
from app.schemas.auth import ChangePasswordIn, DeleteAccountIn, TokenOut, UserOut, UserUpdate
from app.services.auth_service import audit, issue_session, purge_user, revoke_all
from app.services.storage import delete_files

router = APIRouter(prefix="/users", tags=["Profile"])


class StatsOut(BaseModel):
    scans: int
    listings: int
    chats: int


@router.get("/me", response_model=UserOut)
def get_me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserOut)
def update_me(payload: UserUpdate, request: Request, user: User = Depends(get_current_user),
              db: Session = Depends(get_db)) -> User:
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.preferred_language is not None:
        user.preferred_language = payload.preferred_language
    if payload.email is not None:
        new_email = payload.email or None
        if new_email and db.scalar(select(User.id).where(func.lower(User.email) == new_email, User.id != user.id)):
            raise HTTPException(409, "An account with this email already exists.")
        user.email = new_email
    if payload.phone is not None:
        new_phone = payload.phone or None
        if new_phone and db.scalar(select(User.id).where(User.phone == new_phone, User.id != user.id)):
            raise HTTPException(409, "An account with this mobile number already exists.")
        user.phone = new_phone
    if not user.email and not user.phone:
        raise HTTPException(422, "Keep at least a mobile number or an email address.")
    audit(db, "profile_updated", user.id, client_ip(request))
    db.commit()
    return user


@router.get("/me/stats", response_model=StatsOut)
def my_stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> StatsOut:
    scans = db.scalar(select(func.count()).select_from(Scan).where(Scan.user_id == user.id, Scan.deleted_at.is_(None)))
    listings = db.scalar(select(func.count()).select_from(CropListing).where(CropListing.user_id == user.id))
    chats = db.scalar(select(func.count()).select_from(ChatThread).where(ChatThread.user_id == user.id))
    return StatsOut(scans=scans or 0, listings=listings or 0, chats=chats or 0)


@router.post("/me/password", response_model=TokenOut, dependencies=[Depends(rate_limit("auth"))])
def change_password(payload: ChangePasswordIn, request: Request, user: User = Depends(get_current_user),
                    sid: str | None = Depends(get_session_id), db: Session = Depends(get_db)) -> TokenOut:
    ip = client_ip(request)
    if not verify_password(payload.current_password, user.hashed_password):
        audit(db, "password_change_failed", user.id, ip)
        db.commit()
        raise HTTPException(400, "Your current password is not correct.")
    policy = check_password_policy(payload.new_password, user.username)
    if not policy.ok:
        raise HTTPException(422, POLICY_MESSAGES[policy.problems[0]])
    if verify_password(payload.new_password, user.hashed_password):
        raise HTTPException(422, "New password must be different from the current one.")
    user.hashed_password = hash_password(payload.new_password)
    # Access tokens with iat before this second become invalid; other devices' refresh tokens are revoked.
    user.password_changed_at = utcnow()
    revoke_all(db, user.id)
    audit(db, "password_changed", user.id, ip)
    db.flush()
    # Re-issue a fresh session for this device so the farmer stays signed in here.
    out = issue_session(db, user, remember=True, device=request.headers.get("x-device") or "This device", ip=ip)
    db.commit()
    return out


@router.delete("/me", status_code=200)
def delete_me(payload: DeleteAccountIn, request: Request, user: User = Depends(get_current_user),
              db: Session = Depends(get_db)) -> dict:
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(400, "Password is not correct.")
    username, uid = user.username, user.id
    media_ids = purge_user(db, user)
    audit(db, "account_deleted", uid, client_ip(request), f"username={username}")
    db.commit()
    delete_files(media_ids)
    return {"status": "deleted", "message": f"Account '{username}' and all its data were permanently removed."}

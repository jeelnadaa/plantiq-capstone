"""Session issuing, rotation and revocation; audit logging; account purge."""
from __future__ import annotations

import logging
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_token, new_family_id, new_refresh_token
from app.core.timeutil import as_aware, utcnow
from app.models import (
    AnalysisCache,
    AuditEvent,
    ChatThread,
    CropListing,
    ListingReport,
    MediaFile,
    RefreshToken,
    Scan,
    User,
)
from app.schemas.auth import TokenOut, UserOut

log = logging.getLogger("plantiq.auth")


def audit(db: Session, event: str, user_id: int | None = None, ip: str | None = None, detail: str | None = None) -> None:
    db.add(AuditEvent(event=event, user_id=user_id, ip=ip, detail=(detail or "")[:500] or None))
    log.info("[audit] %s user=%s ip=%s %s", event, user_id, ip, detail or "")


def _refresh_lifetime(remember: bool) -> timedelta:
    return timedelta(days=settings.REFRESH_TOKEN_DAYS) if remember else timedelta(hours=settings.REFRESH_TOKEN_SHORT_HOURS)


def issue_session(db: Session, user: User, *, remember: bool, device: str | None, ip: str | None,
                  family_id: str | None = None) -> TokenOut:
    raw = new_refresh_token()
    family = family_id or new_family_id()
    now = utcnow()
    db.add(RefreshToken(
        user_id=user.id, token_hash=hash_token(raw), family_id=family,
        device=(device or "Unknown device")[:160], ip=ip, remember=remember,
        created_at=now, last_used_at=now, expires_at=now + _refresh_lifetime(remember),
    ))
    db.flush()
    access, expires_in = create_access_token(user.id, family)
    return TokenOut(access_token=access, refresh_token=raw, expires_in=expires_in, user=UserOut.model_validate(user))


def rotate_session(db: Session, raw_refresh: str, ip: str | None) -> TokenOut:
    row = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_token(raw_refresh)))
    invalid = HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired. Please sign in again.")
    if row is None:
        raise invalid
    now = utcnow()
    if row.rotated_at is not None:
        # A token that was already exchanged is being replayed → assume theft, kill the whole family.
        revoke_family(db, row.family_id, reason="refresh_reuse")
        audit(db, "refresh_reuse_detected", row.user_id, ip, f"family={row.family_id}")
        db.commit()
        raise invalid
    if row.revoked_at is not None:
        raise invalid
    if as_aware(row.expires_at) <= now:
        row.revoked_at = now
        db.commit()
        raise invalid
    user = db.get(User, row.user_id)
    if not user or not user.is_active:
        raise invalid
    row.rotated_at = now
    row.last_used_at = now
    out = issue_session(db, user, remember=row.remember, device=row.device, ip=ip, family_id=row.family_id)
    db.commit()
    return out


def revoke_family(db: Session, family_id: str, reason: str = "logout") -> None:
    db.execute(update(RefreshToken).where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
               .values(revoked_at=utcnow()))


def revoke_all(db: Session, user_id: int, except_family: str | None = None) -> int:
    q = update(RefreshToken).where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
    if except_family:
        q = q.where(RefreshToken.family_id != except_family)
    return db.execute(q.values(revoked_at=utcnow())).rowcount or 0


def active_sessions(db: Session, user_id: int) -> list[RefreshToken]:
    """Latest live token per family = one row per signed-in device."""
    now = utcnow()
    rows = db.scalars(select(RefreshToken).where(
        RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None), RefreshToken.rotated_at.is_(None),
    ).order_by(RefreshToken.last_used_at.desc())).all()
    return [r for r in rows if as_aware(r.expires_at) > now]


def purge_user(db: Session, user: User) -> list[str]:
    """GDPR erase: listings, reports, chats, scans, cache, tokens, media rows. Returns media ids to delete on disk."""
    uid = user.id
    media_ids = [m for (m,) in db.execute(select(MediaFile.id).where(MediaFile.owner_id == uid)).all()]
    db.execute(delete(ListingReport).where(ListingReport.reported_by_user_id == uid))
    listing_ids = [i for (i,) in db.execute(select(CropListing.id).where(CropListing.user_id == uid)).all()]
    if listing_ids:
        db.execute(delete(ListingReport).where(ListingReport.listing_id.in_(listing_ids)))
    db.execute(delete(CropListing).where(CropListing.user_id == uid))
    for thread in db.scalars(select(ChatThread).where(ChatThread.user_id == uid)).all():
        db.delete(thread)
    db.execute(delete(Scan).where(Scan.user_id == uid))
    db.execute(delete(AnalysisCache).where(AnalysisCache.user_id == uid))
    db.execute(delete(MediaFile).where(MediaFile.owner_id == uid))
    db.execute(delete(RefreshToken).where(RefreshToken.user_id == uid))
    db.delete(user)
    return media_ids

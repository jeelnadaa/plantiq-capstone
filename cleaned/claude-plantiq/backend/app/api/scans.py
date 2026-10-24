"""Scan history (server-side) with soft delete + restore, which powers the 3-second undo in the UI."""
from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.timeutil import utcnow
from app.models import MediaFile, Scan, User
from app.schemas.scans import ScanIdsIn, ScanOut
from app.services.cnn import DISPLAY
from app.services.storage import delete_files, media_url

router = APIRouter(prefix="/scans", tags=["Scan history"])


def to_out(s: Scan) -> ScanOut:
    d = DISPLAY.get(s.disease, {"en": s.disease, "kn": s.disease})
    return ScanOut(
        id=s.id, disease=s.disease, disease_display=d["en"], disease_display_kn=d["kn"], confidence=s.confidence,
        is_healthy=s.is_healthy, is_blended=s.is_blended, image_url=media_url(s.media_id), distribution=s.distribution or {},
        env_data=s.env_data, advisory=s.advisory, sources=s.sources, citations=s.citations, safety_audit=s.safety_audit,
        reasons=s.reasons, question=s.question, language=s.language, latitude=s.latitude, longitude=s.longitude,
        created_at=s.created_at,
    )


def _owned(db: Session, user: User, scan_id: int, include_deleted: bool = False) -> Scan:
    s = db.get(Scan, scan_id)
    if not s or s.user_id != user.id or (s.deleted_at is not None and not include_deleted):
        raise HTTPException(404, "Scan not found.")
    return s


@router.get("", response_model=list[ScanOut])
def list_scans(kind: str = Query("all", pattern="^(all|disease|healthy)$"), limit: int = Query(50, ge=1, le=200),
               offset: int = Query(0, ge=0), user: User = Depends(get_current_user),
               db: Session = Depends(get_db)) -> list[ScanOut]:
    q = select(Scan).where(Scan.user_id == user.id, Scan.deleted_at.is_(None))
    if kind == "disease":
        q = q.where(Scan.is_healthy.is_(False))
    elif kind == "healthy":
        q = q.where(Scan.is_healthy.is_(True))
    rows = db.scalars(q.order_by(Scan.created_at.desc(), Scan.id.desc()).offset(offset).limit(limit)).all()
    return [to_out(s) for s in rows]


@router.get("/{scan_id}", response_model=ScanOut)
def get_scan(scan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ScanOut:
    return to_out(_owned(db, user, scan_id))


@router.delete("/{scan_id}")
def delete_scan(scan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    s = _owned(db, user, scan_id)
    s.deleted_at = utcnow()
    db.commit()
    return {"status": "deleted", "id": scan_id, "undo_seconds": 3}


@router.post("/{scan_id}/restore", response_model=ScanOut)
def restore_scan(scan_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> ScanOut:
    s = _owned(db, user, scan_id, include_deleted=True)
    s.deleted_at = None
    db.commit()
    return to_out(s)


@router.delete("")
def clear_all(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    ids = list(db.scalars(select(Scan.id).where(Scan.user_id == user.id, Scan.deleted_at.is_(None))).all())
    if ids:
        db.execute(update(Scan).where(Scan.id.in_(ids)).values(deleted_at=utcnow()))
        db.commit()
    return {"status": "cleared", "ids": ids, "count": len(ids)}


@router.post("/restore")
def restore_many(payload: ScanIdsIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    if not payload.ids:
        return {"restored": 0}
    res = db.execute(update(Scan).where(Scan.user_id == user.id, Scan.id.in_(payload.ids)).values(deleted_at=None))
    db.commit()
    return {"restored": res.rowcount or 0}


def purge_soft_deleted(db: Session, older_than: timedelta = timedelta(hours=24)) -> int:
    """Hard-delete scans soft-deleted long ago (and their images)."""
    cutoff = utcnow() - older_than
    rows = db.execute(select(Scan.id, Scan.media_id).where(Scan.deleted_at.is_not(None), Scan.deleted_at < cutoff)).all()
    if not rows:
        return 0
    media = [m for _, m in rows if m]
    db.execute(delete(Scan).where(Scan.id.in_([i for i, _ in rows])))
    if media:
        still_used = set(db.scalars(select(Scan.media_id).where(Scan.media_id.in_(media))).all())
        gone = [m for m in media if m not in still_used]
        db.execute(delete(MediaFile).where(MediaFile.id.in_(gone)))
        db.commit()
        delete_files(gone)
    else:
        db.commit()
    return len(rows)

"""Media storage: sanitised JPEGs on disk, metadata in the media_files table."""
from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.uploads import CleanImage, clean_image
from app.models import MediaFile

log = logging.getLogger("plantiq.storage")
MEDIA_ID_RE = re.compile(r"^[a-f0-9]{32}$")


def media_path(media_id: str) -> Path:
    if not MEDIA_ID_RE.fullmatch(media_id or ""):
        raise ValueError("bad media id")
    return settings.media_dir / f"{media_id}.jpg"


def media_url(media_id: str | None) -> str | None:
    return f"/media/{media_id}.jpg" if media_id else None


def save_image(db: Session, data: bytes, *, owner_id: int | None, kind: str, filename: str | None = None,
               max_side: int = 1600, already_clean: CleanImage | None = None) -> MediaFile:
    img = already_clean or clean_image(data, filename, max_side=max_side, quality=85)
    if max(img.width, img.height) > max_side:
        img = clean_image(img.data, filename, max_side=max_side, quality=85)
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    media_id = uuid.uuid4().hex
    media_path(media_id).write_bytes(img.data)
    row = MediaFile(id=media_id, owner_id=owner_id, kind=kind, width=img.width, height=img.height, size_bytes=len(img.data))
    db.add(row)
    db.flush()
    return row


def delete_files(media_ids: list[str]) -> None:
    for mid in media_ids:
        try:
            media_path(mid).unlink(missing_ok=True)
        except (OSError, ValueError) as exc:
            log.warning("Could not delete media %s: %s", mid, exc)

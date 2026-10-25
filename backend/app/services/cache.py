"""SHA-256 deduplication cache for diagnoses (scoped by image + user + question + language)."""
from __future__ import annotations

import hashlib

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import AnalysisCache


def analysis_key(image: bytes, user_id: int | None, question: str | None, language: str) -> str:
    h = hashlib.sha256()
    h.update(image)
    h.update(f"_user_{user_id or 0}".encode())
    if question and question.strip():
        h.update(f"_q_{question.strip().lower()}".encode())
    h.update(f"_lang_{language}".encode())
    return h.hexdigest()


def get_cached(db: Session, key: str) -> dict | None:
    row = db.scalar(select(AnalysisCache).where(AnalysisCache.image_hash == key))
    return dict(row.result) if row else None


def put_cached(db: Session, key: str, user_id: int | None, result: dict) -> None:
    if db.scalar(select(AnalysisCache.id).where(AnalysisCache.image_hash == key)):
        return
    db.add(AnalysisCache(image_hash=key, user_id=user_id, result=result))
    try:
        db.flush()
    except IntegrityError:  # concurrent identical request
        db.rollback()

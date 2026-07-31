import hashlib
import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, String, Text, Float, DateTime
from sqlalchemy.orm import Session
from app.core.database import Base, engine

class ProcessedImageCache(Base):
    __tablename__ = "image_cache"

    sha256_hash = Column(String(64), primary_key=True, index=True)
    filename = Column(String(255))
    disease_class = Column(String(100))
    confidence = Column(Float)
    distribution_json = Column(Text)
    env_data_json = Column(Text)
    advisory_text = Column(Text)
    sources_json = Column(Text)
    is_blended = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)

# Ensure tables are created
Base.metadata.create_all(bind=engine)

def compute_image_hash(
    image_bytes: bytes, 
    user_id: Optional[Any] = None, 
    user_question: Optional[str] = None, 
    language: str = "en"
) -> str:
    """
    Computes SHA-256 hash incorporating raw image bytes, user_id, user question, and language
    so that each user has an isolated cache entry and asking a new question generates a distinct entry.
    """
    hasher = hashlib.sha256()
    hasher.update(image_bytes)
    if user_id:
        hasher.update(str(user_id).encode("utf-8"))
    hasher.update(language.strip().lower().encode("utf-8"))
    if user_question and user_question.strip():
        hasher.update(user_question.strip().lower().encode("utf-8"))
    return hasher.hexdigest()

def get_cached_image_result(db: Session, image_hash: str) -> Optional[Dict[str, Any]]:
    """Fetches stored result by image hash if available."""
    cached = db.query(ProcessedImageCache).filter(ProcessedImageCache.sha256_hash == image_hash).first()
    if not cached:
        return None

    return {
        "cache_hit": True,
        "sha256_hash": cached.sha256_hash,
        "filename": cached.filename,
        "disease": cached.disease_class,
        "confidence": cached.confidence,
        "is_healthy": cached.disease_class == "Healthy",
        "distribution": json.loads(cached.distribution_json or "{}"),
        "env_data": json.loads(cached.env_data_json or "{}"),
        "advisory": cached.advisory_text,
        "sources": json.loads(cached.sources_json or "[]"),
        "is_blended": cached.is_blended == "True",
        "created_at": cached.created_at.isoformat()
    }

def save_image_result_to_cache(
    db: Session,
    image_hash: str,
    filename: str,
    disease_class: str,
    confidence: float,
    distribution: Dict[str, float],
    env_data: Dict[str, Any],
    advisory_text: str,
    sources: list,
    is_blended: bool
) -> ProcessedImageCache:
    """Saves new image result into cache database."""
    entry = ProcessedImageCache(
        sha256_hash=image_hash,
        filename=filename,
        disease_class=disease_class,
        confidence=confidence,
        distribution_json=json.dumps(distribution),
        env_data_json=json.dumps(env_data),
        advisory_text=advisory_text,
        sources_json=json.dumps(sources),
        is_blended=str(is_blended),
        created_at=datetime.utcnow()
    )
    db.merge(entry)  # Use merge to insert or update
    db.commit()
    return entry

def delete_cached_image_result(db: Session, image_hash: str) -> bool:
    """Deletes a specific cached image record by its SHA-256 hash."""
    cached = db.query(ProcessedImageCache).filter(ProcessedImageCache.sha256_hash == image_hash).first()
    if cached:
        db.delete(cached)
        db.commit()
        return True
    return False

def clear_all_cached_image_results(db: Session) -> int:
    """Deletes all cached image records from the SQLite database."""
    count = db.query(ProcessedImageCache).delete()
    db.commit()
    return count

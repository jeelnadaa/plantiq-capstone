import hashlib
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.cache import ImageAnalysisCache

def compute_image_hash(image_bytes: bytes, user_id: Optional[int] = None, user_question: Optional[str] = None, language: str = 'en') -> str:
    hasher = hashlib.sha256()
    hasher.update(image_bytes)
    hasher.update(f'_user_{user_id or 0}'.encode('utf-8'))
    if user_question:
        hasher.update(f'_q_{user_question.strip().lower()}'.encode('utf-8'))
    hasher.update(f'_lang_{language}'.encode('utf-8'))
    return hasher.hexdigest()

def get_cached_result(db: Session, image_hash: str) -> Optional[Dict[str, Any]]:
    record = db.query(ImageAnalysisCache).filter(ImageAnalysisCache.image_hash == image_hash).first()
    if not record:
        return None
    return {
        'cache_hit': True,
        'sha256_hash': record.image_hash,
        'filename': record.filename,
        'disease': record.disease_class,
        'confidence': record.confidence,
        'is_healthy': (record.disease_class == 'Healthy'),
        'distribution': record.distribution,
        'env_data': record.env_data,
        'advisory': record.advisory_text,
        'sources': record.sources,
        'is_blended': record.is_blended,
        'reasons': ['Retrieved from user-scoped SHA-256 deduplication cache.']
    }

def save_result_to_cache(
    db: Session,
    image_hash: str,
    filename: str,
    disease_class: str,
    confidence: float,
    distribution: dict,
    env_data: Optional[dict],
    advisory_text: str,
    sources: Optional[list] = None,
    is_blended: bool = False,
    user_id: Optional[int] = None
) -> ImageAnalysisCache:
    existing = db.query(ImageAnalysisCache).filter(ImageAnalysisCache.image_hash == image_hash).first()
    if existing:
        return existing
    record = ImageAnalysisCache(
        image_hash=image_hash,
        user_id=user_id,
        filename=filename,
        disease_class=disease_class,
        confidence=confidence,
        distribution=distribution,
        env_data=env_data,
        advisory_text=advisory_text,
        sources=sources,
        is_blended=is_blended
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

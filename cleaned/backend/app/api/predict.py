from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.core.image_guard import validate_and_sanitize_image
from app.services.cnn_service import get_detector
from app.services.cache_service import compute_image_hash, get_cached_result, save_result_to_cache
from app.services.env_service import get_env_service
from app.services.rag_service import get_rag_service
from app.schemas.predict import DiagnosisResponse

router = APIRouter(tags=["Leaf Diagnosis"])

import time
from app.core.terminal_logger import tracker

@router.post("/predict", response_model=DiagnosisResponse)
async def predict_leaf(
    file: UploadFile = File(...),
    user_question: Optional[str] = Form(None),
    language: str = Form("en"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    t_start = time.perf_counter()
    user_id = current_user.id if current_user else None

    try:
        raw_contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image file: {e}")

    # Security Guard: Magic bytes, 10MB size bound, EXIF stripping, dimension check, path traversal sanitization
    contents, safe_filename = validate_and_sanitize_image(raw_contents, file.filename or "leaf.jpg")

    tracker.log_request_header(
        operation="Leaf Image Diagnosis (ResNet-50 + Hybrid RAG + LLM)",
        filename=safe_filename,
        user_id=user_id,
        language=language
    )

    # 1. SHA-256 Deduplication Cache Check
    image_hash = compute_image_hash(contents, user_id=user_id, user_question=user_question, language=language)
    cached = get_cached_result(db, image_hash)
    if cached:
        tracker.log_cache_status(True, image_hash)
        total_time_s = time.perf_counter() - t_start
        tracker.log_pipeline_complete(total_time_s, cached=True)
        return cached

    tracker.log_cache_status(False, image_hash)

    # 2. ResNet50 Inference
    detector = get_detector()
    prediction = detector.predict(contents)
    if prediction.get("error"):
        raise HTTPException(status_code=500, detail=f"CNN Model Error: {prediction['error']}")

    disease = prediction["class"]
    confidence = prediction["confidence"]
    distribution = prediction["distribution"]

    # 3. Microclimate Weather Engine
    env_service = get_env_service()
    env_data = env_service.get_environmental_data(latitude, longitude)
    tracker.log_microclimate(env_data)

    # 4. RAG Advisory Synthesis & LLM
    rag_service = get_rag_service()
    advisory_res = rag_service.generate_advisory(
        disease=disease,
        cnn_confidence=confidence,
        is_healthy=(disease == "Healthy"),
        env_data=env_data,
        user_question=user_question,
        language=language
    )

    # 5. Persist to Cache
    save_result_to_cache(
        db=db,
        image_hash=image_hash,
        filename=safe_filename,
        disease_class=disease,
        confidence=confidence,
        distribution=distribution,
        env_data=env_data,
        advisory_text=advisory_res.answer,
        sources=advisory_res.sources,
        is_blended=advisory_res.is_blended,
        user_id=user_id
    )

    total_time_s = time.perf_counter() - t_start
    tracker.log_pipeline_complete(total_time_s, cached=False, device="cuda" if rag_service.device == "cuda" else "cpu")

    return {
        "cache_hit": False,
        "sha256_hash": image_hash,
        "filename": safe_filename,
        "disease": disease,
        "confidence": confidence,
        "is_healthy": (disease == "Healthy"),
        "distribution": distribution,
        "env_data": env_data,
        "advisory": advisory_res.answer,
        "sources": advisory_res.sources,
        "is_blended": advisory_res.is_blended,
        "reasons": advisory_res.reasons,
        "citations": advisory_res.citations,
        "safety_audit": advisory_res.safety_audit
    }

import os
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.modules.cnn.detector import get_detector
from app.modules.environment.mock_provider import get_env_service
from app.modules.rag.pipeline import generate_disease_advisory, query_llm
from app.modules.cache.image_cache import (
    compute_image_hash, 
    get_cached_image_result, 
    save_image_result_to_cache
)
from app.modules.chat.chat_service import process_chat_message, start_chat_from_cnn_handoff
from app.modules.marketplace.router import router as marketplace_router
from app.modules.speech.translator import get_translations

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for PlantIQ Coffee Leaf Disease Diagnostics, RAG Advisory, Chatbot & Marketplace"
)

# CORS middleware for mobile app clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static uploaded images
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Marketplace Router
app.include_router(marketplace_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "predict_disease": "/api/predict",
            "chat_message": "/api/chat/message",
            "chat_handoff": "/api/chat/start-from-scan",
            "marketplace": "/api/marketplace/listings",
            "translations": "/api/i18n/{lang}"
        }
    }



@app.get("/api/i18n/{lang}")
def get_i18n(lang: str = "en"):
    return get_translations(lang)

@app.post("/api/predict")
async def predict_and_advise(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    language: str = Form("en"),
    user_question: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    CNN -> Environmental Data -> RAG & LLM Advisory Pipeline with Image Deduplication Caching.
    """
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Step 1: Deduplication Check via Image Hash
        image_hash = compute_image_hash(contents)
        cached_result = get_cached_image_result(db, image_hash)
        if cached_result:
            print(f"[Cache HIT] Found cached analysis for hash={image_hash[:10]}...")
            return cached_result

        # Step 2: CNN ResNet50 Inference
        detector = get_detector()
        prediction = detector.predict(contents)
        if prediction.get("error"):
            raise HTTPException(status_code=500, detail=f"CNN Model Error: {prediction['error']}")

        disease = prediction["class"]
        confidence = prediction["confidence"]
        is_healthy = prediction["is_healthy"]
        distribution = prediction["distribution"]

        # Step 3: Fetch Environmental Data (Allowed vs Disallowed GPS)
        env_service = get_env_service()
        env_data = env_service.get_environmental_data(latitude, longitude)

        # Step 4: Run RAG & LLM Advisory Engine with Low-Confidence Blending
        advisory_res = generate_disease_advisory(
            disease=disease,
            cnn_confidence=confidence,
            is_healthy=is_healthy,
            env_data=env_data,
            user_question=user_question,
            language=language
        )

        # Step 5: Save to Image Cache Store
        save_image_result_to_cache(
            db=db,
            image_hash=image_hash,
            filename=file.filename or "leaf.jpg",
            disease_class=disease,
            confidence=confidence,
            distribution=distribution,
            env_data=env_data,
            advisory_text=advisory_res.answer,
            sources=advisory_res.sources,
            is_blended=advisory_res.is_blended
        )

        return {
            "cache_hit": False,
            "sha256_hash": image_hash,
            "filename": file.filename,
            "disease": disease,
            "confidence": confidence,
            "is_healthy": is_healthy,
            "distribution": distribution,
            "env_data": env_data,
            "advisory": advisory_res.answer,
            "sources": advisory_res.sources,
            "is_blended": advisory_res.is_blended,
            "reasons": advisory_res.reasons
        }

    except Exception as e:
        print(f"[Predict API Error] {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/message")
async def chat_message(
    session_id: Optional[str] = Form(None),
    user_message: str = Form(...),
    language: str = Form("en"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Chatbot endpoint supporting bilingual questions, location factors, and image attachments.
    """
    image_bytes = None
    if image:
        image_bytes = await image.read()

    res = process_chat_message(
        session_id=session_id or "",
        user_message=user_message,
        language=language,
        latitude=latitude,
        longitude=longitude,
        image_bytes=image_bytes
    )
    return res

@app.post("/api/chat/start-from-scan")
def chat_start_from_scan(
    disease: str = Form(...),
    confidence: float = Form(...),
    advisory: str = Form(...),
    language: str = Form("en")
):
    """
    Handoff entrypoint: Jump from CNN diagnostic scan into Chatbot with context pre-loaded.
    """
    res = start_chat_from_cnn_handoff(
        disease=disease,
        confidence=confidence,
        distribution={},
        env_data={},
        advisory=advisory
    )
    return res

# Mount Mobile App Frontend at ROOT (MUST BE LAST so /api routes take precedence)
MOBILE_APP_DIR = settings.BASE_DIR.parent / "mobile_app"
if MOBILE_APP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(MOBILE_APP_DIR), html=True), name="mobile_frontend")

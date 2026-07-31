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
    save_image_result_to_cache,
    delete_cached_image_result,
    clear_all_cached_image_results
)
from app.modules.chat.chat_service import (
    process_chat_message, 
    start_chat_from_cnn_handoff,
    get_user_chat_threads,
    get_thread_message_history,
    get_or_create_thread
)
from app.modules.auth.router import router as auth_router
from app.modules.auth.security import get_current_user
from app.modules.auth.models import User
from app.modules.marketplace.router import router as marketplace_router
from app.modules.speech.translator import get_translations
from sqlalchemy import text
from app.core.database import engine, Base
import app.modules.auth.models
import app.modules.chat.models
import app.modules.marketplace.models
import app.modules.cache.image_cache

def ensure_db_schema():
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(marketplace_listings);")).fetchall()
            columns = [row[1] for row in res]
            if "user_id" not in columns:
                print("[Migration] Adding user_id column to marketplace_listings table...")
                conn.execute(text("ALTER TABLE marketplace_listings ADD COLUMN user_id VARCHAR REFERENCES users(id);"))
                conn.commit()
            if "image_url" not in columns:
                print("[Migration] Adding image_url column to marketplace_listings table...")
                conn.execute(text("ALTER TABLE marketplace_listings ADD COLUMN image_url VARCHAR;"))
                conn.commit()
    except Exception as e:
        print("[Migration Check Note]", e)

ensure_db_schema()

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

# Include Routers
app.include_router(auth_router)
app.include_router(marketplace_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "auth": "/api/auth/login",
            "predict_disease": "/api/predict",
            "chat_message": "/api/chat/message",
            "chat_threads": "/api/chat/threads",
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
    user_question: Optional[str] = Form(None),
    language: str = Form("en"),
    provider: str = Form("gemini"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Main Diagnostic & Advisory Endpoint requiring mandatory authentication.
    """
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        # Step 1: Deduplication Check via Composite Hash (image + question + language)
        image_hash = compute_image_hash(contents, user_question=user_question, language=language)
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
        distribution = prediction["distribution"]

        # Step 3: Location Factors
        env_service = get_env_service()
        env_data = env_service.get_environmental_data(latitude, longitude)

        # Step 4: RAG Agronomic Advisory Generation
        advisory_res = generate_disease_advisory(
            disease=disease,
            cnn_confidence=confidence,
            is_healthy=(disease == "Healthy"),
            env_data=env_data,
            user_question=user_question,
            language=language,
            provider=provider
        )

        # Step 5: Save Result in SQLite Cache Database
        save_image_result_to_cache(
            db=db,
            image_hash=image_hash,
            filename=file.filename or "uploaded_leaf.jpg",
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
            "is_healthy": disease == "Healthy",
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

@app.get("/api/chat/threads")
def list_chat_threads(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lists persistent chat threads for current authenticated user."""
    return get_user_chat_threads(db, user_id=current_user.id)

@app.get("/api/chat/threads/{thread_id}/messages")
def get_thread_messages(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches full message history for a specific chat thread."""
    return get_thread_message_history(db, thread_id)

@app.post("/api/chat/threads/new")
def create_new_chat_thread(
    title: str = Form("New Conversation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Creates a new empty chat thread for logged-in user."""
    thread = get_or_create_thread(db, user_id=current_user.id, title=title)
    return {
        "thread_id": thread.id,
        "title": thread.title,
        "created_at": thread.created_at.isoformat()
    }

@app.post("/api/chat/message")
async def chat_message(
    session_id: Optional[str] = Form(None),
    user_message: str = Form(...),
    language: str = Form("en"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chatbot endpoint requiring mandatory authentication.
    """
    image_bytes = None
    if image:
        image_bytes = await image.read()

    res = process_chat_message(
        db=db,
        session_id=session_id,
        user_message=user_message,
        user_id=current_user.id,
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
    language: str = Form("en"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Handoff entrypoint requiring mandatory authentication.
    """
    res = start_chat_from_cnn_handoff(
        db=db,
        disease=disease,
        confidence=confidence,
        distribution={},
        env_data={},
        advisory=advisory,
        user_id=current_user.id
    )
    return res

@app.delete("/api/cache/item/{image_hash}")
def delete_cache_item(
    image_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a specific image analysis result from the backend SQLite cache.
    """
    success = delete_cached_image_result(db, image_hash)
    return {"status": "deleted" if success else "not_found", "hash": image_hash}

@app.delete("/api/cache/clear")
def clear_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Purges all cached image analysis results from the backend SQLite database.
    """
    count = clear_all_cached_image_results(db)
    return {"status": "cleared", "deleted_count": count}

# Mount Mobile App Frontend at ROOT (MUST BE LAST so /api routes take precedence)
MOBILE_APP_DIR = settings.BASE_DIR.parent / "mobile_app"
if MOBILE_APP_DIR.exists():
    app.mount("/", StaticFiles(directory=str(MOBILE_APP_DIR), html=True), name="mobile_frontend")

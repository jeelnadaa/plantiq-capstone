"""Leaf diagnosis: CNN + microclimate + hybrid-RAG advisory; stored as a scan in the farmer's history."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.pipeline_log import Pipeline
from app.core.ratelimit import rate_limit
from app.core.timeutil import utcnow
from app.core.uploads import MAX_IMAGE_BYTES, clean_image
from app.models import Scan, User
from app.schemas.scans import DiagnosisOut
from app.services import registry
from app.services.advisory import generate_advisory
from app.services.cache import analysis_key, get_cached, put_cached
from app.services.cnn import DISPLAY
from app.services.storage import media_url, save_image

router = APIRouter(tags=["Leaf diagnosis"])


def _coords(lat: float | None, lng: float | None) -> tuple[float | None, float | None]:
    if lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
        return None, None
    return lat, lng


@router.post("/predict", response_model=DiagnosisOut, dependencies=[Depends(rate_limit("heavy"))])
def predict(
    file: UploadFile = File(...),
    user_question: str | None = Form(None, max_length=500),
    language: str = Form("en", pattern="^(en|kn)$"),
    latitude: float | None = Form(None),
    longitude: float | None = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DiagnosisOut:
    raw = file.file.read(MAX_IMAGE_BYTES + 1)
    img = clean_image(raw, file.filename)  # magic bytes, size, dims, EXIF strip, filename sanitise
    lat, lng = _coords(latitude, longitude)
    question = (user_question or "").strip() or None

    with Pipeline("Leaf diagnosis", user=user.id, lang=language, file=img.filename) as p:
        key = analysis_key(img.data, user.id, question, language)
        cached = get_cached(db, key)
        if cached:
            p.note("cache hit")
            result = cached
        else:
            with p.step("ResNet-50 inference"):
                pred = registry.get_cnn().predict(img.data)
            p.note(f"{pred['class']} {pred['confidence']:.1f}%")
            with p.step("Microclimate"):
                env = registry.get_env().get_environmental_data(lat, lng)
            with p.step("Hybrid RAG + LLM advisory"):
                adv = generate_advisory(disease=pred["class"], confidence=pred["confidence"], env=env, question=question,
                                        language=language, rag=registry.get_rag(), llm=registry.get_llm())
            p.note(f"provider={adv.provider} blended={adv.is_blended} doses_ok={adv.safety_audit['verified']}")
            result = {
                "disease": pred["class"], "confidence": pred["confidence"], "distribution": pred["distribution"],
                "env_data": env, "advisory": adv.answer, "sources": adv.sources, "citations": adv.citations,
                "is_blended": adv.is_blended, "reasons": adv.reasons, "safety_audit": adv.safety_audit,
                "provider": adv.provider, "language": adv.language,
            }
            put_cached(db, key, user.id, result)

        media = save_image(db, img.data, owner_id=user.id, kind="scan", filename=img.filename, already_clean=img)
        scan = Scan(
            user_id=user.id, media_id=media.id, image_hash=key, filename=img.filename, disease=result["disease"],
            confidence=result["confidence"], is_healthy=result["disease"] == "Healthy",
            distribution=result["distribution"], env_data=result.get("env_data"), advisory=result["advisory"],
            sources=result.get("sources"), citations=result.get("citations"), safety_audit=result.get("safety_audit"),
            reasons=result.get("reasons"), is_blended=bool(result.get("is_blended")), question=question,
            language=language, latitude=lat, longitude=lng, created_at=utcnow(),
        )
        db.add(scan)
        db.commit()

    d = DISPLAY.get(result["disease"], {"en": result["disease"], "kn": result["disease"], "latin": "", "kind": "disease"})
    reasons = list(result.get("reasons") or [])
    if cached:
        reasons = ["Same photo and question as an earlier scan — reused the earlier result."] + reasons
    return DiagnosisOut(
        scan_id=scan.id, cache_hit=bool(cached), sha256_hash=key, filename=img.filename, image_url=media_url(media.id),
        disease=result["disease"], disease_display=d["en"], disease_display_kn=d["kn"], latin_name=d.get("latin") or None,
        kind=d["kind"], confidence=result["confidence"], is_healthy=result["disease"] == "Healthy",
        distribution=result["distribution"], env_data=result.get("env_data"), advisory=result["advisory"],
        sources=result.get("sources") or [], citations=result.get("citations") or [], is_blended=bool(result.get("is_blended")),
        reasons=reasons, safety_audit=result.get("safety_audit"), provider=result.get("provider"),
        language=result.get("language", language), created_at=scan.created_at,
    )


@router.get("/predict/classes")
def classes() -> list[dict]:
    return [{"id": k, **v} for k, v in DISPLAY.items()]


def ensure_image_upload(file: UploadFile | None) -> None:
    if file is not None and file.size is not None and file.size > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image is larger than 10 MB.")

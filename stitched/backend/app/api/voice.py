from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.voice_service import transcribe_audio

router = APIRouter(prefix="/voice", tags=["Voice Speech-to-Text"])

@router.post("/transcribe")
async def transcribe_voice(
    file: UploadFile = File(...),
    target_language: str = Form("kn")
):
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read audio file: {e}")

    result = transcribe_audio(contents, file.filename or "recording.webm", target_lang=target_language)
    return result

import io
import logging
from typing import Optional
import google.generativeai as genai
from groq import Groq
from app.core.config import settings

log = logging.getLogger(__name__)

def transcribe_audio_snippet(
    audio_bytes: bytes,
    content_type: str = "audio/webm",
    language_hint: Optional[str] = None
) -> str:
    """
    Transcribes spoken audio using Gemini 1.5 Flash Audio as primary,
    with Groq Whisper-large-v3 as automatic fallback.
    Accurately transcribes Kannada (in Kannada script) and English.
    """
    if not audio_bytes:
        return ""

    # Primary: Gemini 1.5 Flash Audio
    if settings.GEMINI_API_KEY:
        try:
            return _transcribe_with_gemini(audio_bytes, content_type, language_hint)
        except Exception as e:
            log.warning("Gemini audio transcription failed: %s. Falling back to Groq Whisper...", e)

    # Fallback: Groq Whisper Large v3
    if settings.GROQ_API_KEY:
        try:
            return _transcribe_with_groq(audio_bytes, content_type, language_hint)
        except Exception as e:
            log.error("Groq Whisper transcription failed: %s", e)

    return ""

def _transcribe_with_gemini(audio_bytes: bytes, content_type: str, language_hint: Optional[str] = None) -> str:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Map browser mime types if necessary
    mime = content_type.split(";")[0].strip()
    if not mime:
        mime = "audio/webm"

    audio_part = {
        "mime_type": mime,
        "data": audio_bytes
    }

    lang_prompt = ""
    if language_hint == "kn":
        lang_prompt = "The speech is likely in Kannada. Please transcribe accurately in standard Kannada script (ಕನ್ನಡ ಲಿಪಿ)."
    elif language_hint == "en":
        lang_prompt = "The speech is in English. Please transcribe accurately in English."
    else:
        lang_prompt = "The speech may be in Kannada or English. If spoken in Kannada, transcribe in Kannada script (ಕನ್ನಡ). If English, transcribe in English."

    prompt = (
        f"You are a high-precision speech-to-text transcriber for agriculture and coffee farming. {lang_prompt} "
        "Transcribe exactly what is spoken. Do NOT add preamble, commentary, or markdown formatting. Output ONLY the transcribed words."
    )

    response = model.generate_content([prompt, audio_part])
    return response.text.strip() if response.text else ""

def _transcribe_with_groq(audio_bytes: bytes, content_type: str, language_hint: Optional[str] = None) -> str:
    client = Groq(api_key=settings.GROQ_API_KEY)

    # Groq whisper requires file-like tuple with filename and bytes
    ext = "webm"
    if "wav" in content_type:
        ext = "wav"
    elif "mp4" in content_type:
        ext = "mp4"
    elif "ogg" in content_type:
        ext = "ogg"
    elif "mpeg" in content_type or "mp3" in content_type:
        ext = "mp3"

    file_tuple = (f"audio.{ext}", io.BytesIO(audio_bytes), content_type)

    kwargs = {
        "file": file_tuple,
        "model": "whisper-large-v3",
        "response_format": "text"
    }
    if language_hint in ["kn", "en"]:
        kwargs["language"] = language_hint

    transcription = client.audio.transcriptions.create(**kwargs)
    return str(transcription).strip()

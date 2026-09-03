import os
from typing import Dict, Any
from app.core.config import settings

def transcribe_audio(audio_bytes: bytes, filename: str, target_lang: str = "kn") -> Dict[str, Any]:
    # 1. Try Gemini 1.5 Flash Audio
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=settings.GEMINI_API_KEY)
            
            mime_type = "audio/webm"
            if filename.endswith(".wav"):
                mime_type = "audio/wav"
            elif filename.endswith(".mp3"):
                mime_type = "audio/mp3"
            elif filename.endswith(".ogg"):
                mime_type = "audio/ogg"

            audio_part = {"mime_type": mime_type, "data": audio_bytes}
            lang_prompt = (
                "Listen carefully to this farmer's voice and transcribe it accurately into NATIVE KANNADA SCRIPT (ಕನ್ನಡ ಲಿಪಿ). "
                "Even if spoken as Kanglish, output clean, natural Kannada script. Return ONLY the transcribed text."
                if target_lang == "kn"
                else "Listen carefully to this farmer's voice and transcribe it accurately into English. Return ONLY the transcribed text."
            )
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content([lang_prompt, audio_part])
            if resp.text:
                return {"text": resp.text.strip(), "language": target_lang, "provider": "gemini-audio"}
        except Exception as e:
            print(f"[Cleaned Voice] Gemini Audio error: {e}. Trying Groq Whisper...")

    # 2. Fallback to Groq Whisper
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            g_client = Groq(api_key=settings.GROQ_API_KEY)
            transcription = g_client.audio.transcriptions.create(
                file=(filename, audio_bytes),
                model="whisper-large-v3",
                language="kn" if target_lang == "kn" else "en",
                response_format="json"
            )
            return {"text": transcription.text.strip(), "language": target_lang, "provider": "groq-whisper"}
        except Exception as e:
            print(f"[Cleaned Voice] Groq Whisper error: {e}")

    return {"text": "", "error": "Transcription unavailable. Please check API keys."}

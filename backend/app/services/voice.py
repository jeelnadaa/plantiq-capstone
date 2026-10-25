"""Speech-to-text with the original provider chain and env toggles:

    Kannada : IndicConformer-600M (local)  → Groq whisper-large-v3 → Gemini audio
    English : Svarah Indian-English Whisper (local) → Groq whisper-large-v3 → Gemini audio
"""
from __future__ import annotations

import io
import logging
import os
import shutil
import subprocess
import tempfile
import threading
import time

import numpy as np

from app.core.config import settings

log = logging.getLogger("plantiq.voice")

MIME = {"webm": "audio/webm", "ogg": "audio/ogg", "wav": "audio/wav", "mp3": "audio/mp3", "mp4": "audio/mp4",
        "flac": "audio/flac", "aac": "audio/aac"}
MAX_SECONDS = 90


def ffmpeg_binary() -> str | None:
    try:
        import imageio_ffmpeg

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass
    return shutil.which("ffmpeg")


def _read_wav_bytes(data: bytes) -> np.ndarray:
    import soundfile as sf

    pcm, _ = sf.read(io.BytesIO(data), dtype="float32")
    if pcm.ndim == 2:
        pcm = pcm.mean(axis=1)
    return pcm.astype(np.float32)


def decode_to_pcm16k(audio: bytes, ext: str = "webm") -> np.ndarray:
    """Any container → mono 16 kHz float32 via FFmpeg (pipe first, temp file for non-seekable WebM)."""
    exe = ffmpeg_binary()
    if exe:
        cmd = [exe, "-hide_banner", "-loglevel", "error", "-i", "pipe:0", "-t", str(MAX_SECONDS),
               "-ac", "1", "-ar", "16000", "-f", "wav", "pipe:1"]
        try:
            proc = subprocess.run(cmd, input=audio, capture_output=True, timeout=20)
            if proc.returncode == 0 and len(proc.stdout) > 44:
                return _read_wav_bytes(proc.stdout)
        except (subprocess.SubprocessError, OSError):
            pass
        with tempfile.TemporaryDirectory() as tmp:
            src, dst = os.path.join(tmp, f"in.{ext}"), os.path.join(tmp, "out.wav")
            with open(src, "wb") as fh:
                fh.write(audio)
            proc = subprocess.run([exe, "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-t", str(MAX_SECONDS),
                                   "-ac", "1", "-ar", "16000", dst], capture_output=True, timeout=20)
            if proc.returncode == 0 and os.path.exists(dst):
                with open(dst, "rb") as fh:
                    return _read_wav_bytes(fh.read())
    # Fallback for plain WAV/FLAC without FFmpeg
    import soundfile as sf

    pcm, sr = sf.read(io.BytesIO(audio), dtype="float32")
    if pcm.ndim == 2:
        pcm = pcm.mean(axis=1)
    if sr != 16000:
        import scipy.signal

        pcm = scipy.signal.resample(pcm, int(len(pcm) * 16000 / sr))
    return pcm.astype(np.float32)


class _LocalModels:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.indic = None
        self.english = None
        self.device = "cpu"

    def _device(self) -> str:
        from app.services.cnn import resolve_device

        return resolve_device()

    def load_indic(self):
        with self._lock:
            if self.indic is None:
                from transformers import AutoModel

                self.device = self._device()
                kwargs = {"trust_remote_code": True}
                if settings.HF_TOKEN:
                    kwargs["token"] = settings.HF_TOKEN
                model = AutoModel.from_pretrained(settings.INDIC_CONFORMER_MODEL_ID, **kwargs)
                model.to(self.device)
                model.eval()
                self.indic = model
                log.info("IndicConformer loaded on %s", self.device)
        return self.indic

    def load_english(self):
        with self._lock:
            if self.english is None:
                from transformers import logging as hf_logging
                from transformers import pipeline

                hf_logging.set_verbosity_error()
                self.device = self._device()
                kwargs = {"device": self.device}
                if settings.HF_TOKEN:
                    kwargs["token"] = settings.HF_TOKEN
                self.english = pipeline("automatic-speech-recognition", model=settings.ENGLISH_STT_MODEL_ID, **kwargs)
                log.info("Svarah English Whisper loaded on %s", self.device)
        return self.english


class SpeechToText:
    def __init__(self, llm=None) -> None:
        self.local = _LocalModels()
        self._llm = llm

    @property
    def llm(self):
        if self._llm is None:
            from app.services.registry import get_llm

            self._llm = get_llm()
        return self._llm

    def status(self) -> dict:
        return {
            "local_kannada": settings.is_local_kannada_stt_enabled,
            "local_english": settings.is_local_english_stt_enabled,
            "groq": bool(settings.GROQ_API_KEY),
            "gemini": bool(settings.GEMINI_API_KEY),
            "ffmpeg": bool(ffmpeg_binary()),
        }

    def _indic(self, audio: bytes, ext: str) -> str:
        import torch

        model = self.local.load_indic()
        wav = torch.from_numpy(decode_to_pcm16k(audio, ext)).unsqueeze(0).to(self.local.device)
        with torch.inference_mode():
            try:
                out = model(wav, "kn", settings.INDIC_CONFORMER_DECODER)
            except TypeError:
                out = model(wav, "kn")
        if isinstance(out, (list, tuple)):
            return " ".join(str(x).strip() for x in out if x).strip()
        if isinstance(out, dict):
            return str(out.get("text") or out.get("transcription") or "").strip()
        return str(out).strip()

    def _english(self, audio: bytes, ext: str) -> str:
        pipe = self.local.load_english()
        pcm = decode_to_pcm16k(audio, ext)
        if pcm.size == 0:
            return ""
        res = pipe({"raw": pcm, "sampling_rate": 16000})
        if isinstance(res, list):
            res = res[0] if res else {}
        return str((res or {}).get("text", "")).strip()

    def transcribe(self, audio: bytes, filename: str, lang: str, kind: str = "webm") -> dict:
        lang = "kn" if (lang or "").lower() in ("kn", "kannada", "kan") else "en"
        errors: list[str] = []
        t0 = time.perf_counter()

        def done(text: str, provider: str, model: str | None = None) -> dict:
            log.info("STT %s via %s in %.0f ms", lang, provider, (time.perf_counter() - t0) * 1000)
            return {"text": text, "language": lang, "provider": provider, "model": model, "device": self.local.device}

        local_on = settings.is_local_kannada_stt_enabled if lang == "kn" else settings.is_local_english_stt_enabled
        if local_on:
            try:
                text = self._indic(audio, kind) if lang == "kn" else self._english(audio, kind)
                if text:
                    model = settings.INDIC_CONFORMER_MODEL_ID if lang == "kn" else settings.ENGLISH_STT_MODEL_ID
                    return done(text, "indic-conformer-local" if lang == "kn" else "local-whisper-indian-english", model)
                errors.append("local model returned empty text")
            except Exception as exc:
                errors.append(f"local: {exc.__class__.__name__}")
                log.warning("Local STT failed: %s", exc)
        if settings.GROQ_API_KEY:
            try:
                text = self.llm.transcribe_groq(audio, filename, lang)
                if text:
                    return done(text, "groq-whisper", "whisper-large-v3")
            except Exception as exc:
                errors.append(f"groq: {exc.__class__.__name__}")
        if settings.GEMINI_API_KEY:
            try:
                text = self.llm.transcribe_gemini(audio, MIME.get(kind, "audio/webm"), lang)
                if text:
                    return done(text, "gemini-audio", settings.GEMINI_MODEL)
            except Exception as exc:
                errors.append(f"gemini: {exc.__class__.__name__}")
        return {"text": "", "language": lang, "provider": None, "error": "Speech could not be transcribed. Please type instead.",
                "details": errors}

import io
import os
import time
import tempfile
import threading
import shutil
import subprocess
from typing import Dict, Any, Optional
import numpy as np
from app.core.config import settings
from app.core.terminal_logger import tracker

def _get_ffmpeg_binary() -> Optional[str]:
    """Finds ffmpeg executable: first in project backend/bin/, then imageio_ffmpeg, then system PATH."""
    base_backend = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for candidate in [
        os.path.join(base_backend, "bin", "ffmpeg.exe"),
        os.path.join(base_backend, "bin", "ffmpeg"),
    ]:
        if os.path.exists(candidate):
            return candidate

    try:
        import imageio_ffmpeg
        bundled = imageio_ffmpeg.get_ffmpeg_exe()
        if bundled and os.path.exists(bundled):
            return bundled
    except Exception:
        pass

    sys_bin = shutil.which("ffmpeg")
    if sys_bin:
        return sys_bin

    for fallback in [r"C:\ffmpeg\bin\ffmpeg.EXE", "/usr/bin/ffmpeg", "/usr/local/bin/ffmpeg"]:
        if os.path.exists(fallback):
            return fallback
    return None

def _decode_audio_with_ffmpeg(audio_bytes: bytes, filename: str = "") -> Optional[np.ndarray]:
    """
    Decodes arbitrary audio bytes (e.g. webm, ogg, mp3, mp4, wav) to 16kHz mono float32 numpy array using ffmpeg.
    """
    ffmpeg_bin = _get_ffmpeg_binary()
    if not ffmpeg_bin:
        return None

    # Strategy A: in-memory pipe conversion directly to 16kHz mono wav
    try:
        cmd = [
            ffmpeg_bin,
            "-y",
            "-i", "pipe:0",
            "-ac", "1",
            "-ar", "16000",
            "-f", "wav",
            "pipe:1"
        ]
        proc = subprocess.run(cmd, input=audio_bytes, capture_output=True, timeout=12)
        if proc.returncode == 0 and len(proc.stdout) > 44:
            try:
                import soundfile as sf
                data, _ = sf.read(io.BytesIO(proc.stdout), dtype="float32")
                return data
            except Exception:
                import scipy.io.wavfile as wavfile
                _, data = wavfile.read(io.BytesIO(proc.stdout))
                if data.dtype == np.int16:
                    return data.astype(np.float32) / 32768.0
                elif data.dtype == np.int32:
                    return data.astype(np.float32) / 2147483648.0
                return data.astype(np.float32)
    except Exception:
        pass

    # Strategy B: tempfile conversion (for WebM streams needing seekable media container headers)
    try:
        ext = os.path.splitext(filename)[1] or ".webm"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as in_tmp:
            in_tmp.write(audio_bytes)
            in_path = in_tmp.name
        out_path = in_path + ".wav"
        try:
            cmd = [
                ffmpeg_bin,
                "-y",
                "-i", in_path,
                "-ac", "1",
                "-ar", "16000",
                out_path
            ]
            proc = subprocess.run(cmd, capture_output=True, timeout=12)
            if proc.returncode == 0 and os.path.exists(out_path):
                try:
                    import soundfile as sf
                    data, _ = sf.read(out_path, dtype="float32")
                    return data
                except Exception:
                    import scipy.io.wavfile as wavfile
                    _, data = wavfile.read(out_path)
                    if data.dtype == np.int16:
                        return data.astype(np.float32) / 32768.0
                    return data.astype(np.float32)
        finally:
            if os.path.exists(in_path):
                try: os.remove(in_path)
                except Exception: pass
            if os.path.exists(out_path):
                try: os.remove(out_path)
                except Exception: pass
    except Exception:
        pass

    return None

def decode_audio_to_pcm16k(audio_bytes: bytes, filename: str = "") -> np.ndarray:
    """
    Decodes arbitrary audio bytes into a 1D 16kHz float32 numpy array.
    Uses FFmpeg (bundled in backend/bin/ or system), falling back to soundfile / torchaudio / scipy.
    """
    # 1. Primary: FFmpeg (universal container decoding for WebM, OGG, MP3, MP4, WAV)
    try:
        data = _decode_audio_with_ffmpeg(audio_bytes, filename)
        if data is not None and len(data) > 0:
            if data.ndim == 2:
                data = np.mean(data, axis=0) if data.shape[0] < data.shape[1] else np.mean(data, axis=1)
            return data.astype(np.float32)
    except Exception:
        pass

    # 2. Secondary: soundfile
    try:
        import soundfile as sf
        data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
        if data.ndim == 2:
            data = np.mean(data, axis=1)
        if sr != 16000:
            import scipy.signal
            num_samples = int(len(data) * 16000 / sr)
            data = scipy.signal.resample(data, num_samples).astype(np.float32)
        return data.astype(np.float32)
    except Exception:
        pass

    # 3. Tertiary: torchaudio
    try:
        import torch
        import torchaudio
        waveform, sr = torchaudio.load(io.BytesIO(audio_bytes))
        if waveform.ndim == 2 and waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        if sr != 16000:
            import torchaudio.transforms as T
            waveform = T.Resample(sr, 16000)(waveform)
        return waveform.squeeze().cpu().numpy().astype(np.float32)
    except Exception:
        pass

    # 4. Quaternary: torchaudio temporary file
    try:
        import torch
        import torchaudio
        ext = os.path.splitext(filename)[1] or ".wav"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            waveform, sr = torchaudio.load(tmp_path)
            if waveform.ndim == 2 and waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            if sr != 16000:
                import torchaudio.transforms as T
                waveform = T.Resample(sr, 16000)(waveform)
            return waveform.squeeze().cpu().numpy().astype(np.float32)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        raise RuntimeError(f"Unable to decode audio format for '{filename}': {e}")


class IndicConformerSTTManager:
    """
    Thread-safe lazy-loaded singleton for ai4bharat/indic-conformer-600m-multilingual.
    Optimized for native Kannada ('kn') and 22 Indic regional languages.
    Runs on CUDA (if available & enabled) or CPU.
    """
    _instance: Optional["IndicConformerSTTManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.model = None
        self.device = "cpu"
        self.model_id = settings.INDIC_CONFORMER_MODEL_ID
        self.decoder = settings.INDIC_CONFORMER_DECODER
        self._initialized = False
        self._init_error = None

    @classmethod
    def get_instance(cls) -> "IndicConformerSTTManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _determine_device(self) -> str:
        pref = (settings.INDIC_CONFORMER_DEVICE or "auto").lower()
        try:
            import torch
            if pref == "cuda":
                if torch.cuda.is_available():
                    return "cuda"
                print("[IndicConformer] CUDA requested but not available. Falling back to CPU.")
                return "cpu"
            elif pref == "cpu":
                return "cpu"
            else:  # 'auto'
                return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def load_model(self):
        """Loads model into memory if not already loaded."""
        if self._initialized and self.model is not None:
            return self.model

        with self._lock:
            if self._initialized and self.model is not None:
                return self.model

            try:
                import torch
                from transformers import AutoModel

                self.device = self._determine_device()
                print(f"[IndicConformer] Loading '{self.model_id}' on device: {self.device}...")

                hf_token = settings.HF_TOKEN or os.getenv("HF_TOKEN") or None

                # Load HuggingFace model with remote code
                load_kwargs = {"trust_remote_code": True}
                if hf_token:
                    load_kwargs["token"] = hf_token

                self.model = AutoModel.from_pretrained(self.model_id, **load_kwargs)
                self.model.to(self.device)
                self.model.eval()

                self._initialized = True
                self._init_error = None
                print(f"[IndicConformer] Model loaded successfully on {self.device}.")
                return self.model
            except Exception as e:
                self._init_error = str(e)
                self.model = None
                self._initialized = False
                print(f"[IndicConformer] Failed to load local model: {e}")
                raise e

    def preprocess_audio(self, audio_bytes: bytes, filename: str):
        """Prepares mono 16kHz PyTorch tensor for the IndicConformer model."""
        import torch
        pcm = decode_audio_to_pcm16k(audio_bytes, filename)
        waveform = torch.from_numpy(pcm)
        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        return waveform.to(self.device)

    def transcribe(self, audio_bytes: bytes, filename: str, target_lang: str = "kn") -> str:
        """
        Transcribes audio bytes using the IndicConformer model for Kannada ('kn').
        """
        import torch

        # Normalize language code for IndicConformer
        lang_lower = (target_lang or "kn").lower().strip()
        lang_code = "kn" if lang_lower in ["kn", "kannada", "kan"] else lang_lower

        model = self.load_model()
        wav = self.preprocess_audio(audio_bytes, filename)

        with torch.no_grad():
            output = None
            try:
                output = model(wav, lang_code, self.decoder)
            except TypeError:
                try:
                    output = model(wav, lang=lang_code, decoding_strategy=self.decoder)
                except TypeError:
                    output = model(wav, lang_code)

        # Parse text output (could be str, list, or dict)
        if isinstance(output, list):
            transcription = " ".join([str(item).strip() for item in output if item]).strip()
        elif isinstance(output, dict):
            transcription = str(output.get("text") or output.get("transcription") or "").strip()
        elif isinstance(output, tuple):
            transcription = str(output[0]).strip()
        else:
            transcription = str(output).strip()

        return transcription


class LocalEnglishSTTManager:
    """
    Thread-safe lazy-loaded singleton for Indian-accent English ASR.
    Uses 'bryandts/whisper-base-en-india-accent-svarah' (fine-tuned on the Svarah Indian English Accent corpus)
    via HuggingFace transformers pipeline on CUDA (if available) or CPU.
    """
    _instance: Optional["LocalEnglishSTTManager"] = None
    _lock = threading.Lock()

    def __init__(self):
        self.pipeline = None
        self.device = "cpu"
        self.model_id = getattr(settings, "ENGLISH_STT_MODEL_ID", "bryandts/whisper-base-en-india-accent-svarah")
        self._initialized = False
        self._init_error = None

    @classmethod
    def get_instance(cls) -> "LocalEnglishSTTManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _determine_device(self) -> str:
        pref = (getattr(settings, "INDIC_CONFORMER_DEVICE", None) or "auto").lower()
        try:
            import torch
            if pref == "cuda":
                return "cuda" if torch.cuda.is_available() else "cpu"
            elif pref == "cpu":
                return "cpu"
            else:  # 'auto'
                return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def load_pipeline(self):
        """Loads Whisper Indian-English pipeline if not already loaded."""
        if self._initialized and self.pipeline is not None:
            return self.pipeline

        with self._lock:
            if self._initialized and self.pipeline is not None:
                return self.pipeline

            try:
                import torch
                from transformers import pipeline, logging as hf_logging
                hf_logging.set_verbosity_error()

                self.device = self._determine_device()
                print(f"[LocalEnglishSTT] Loading Indian-accent model '{self.model_id}' on device: {self.device}...")

                hf_token = settings.HF_TOKEN or os.getenv("HF_TOKEN") or None
                pipe_kwargs = {
                    "device": self.device,
                }
                if hf_token:
                    pipe_kwargs["token"] = hf_token

                self.pipeline = pipeline(
                    "automatic-speech-recognition",
                    model=self.model_id,
                    **pipe_kwargs
                )
                self._initialized = True
                self._init_error = None
                print(f"[LocalEnglishSTT] Indian English model loaded successfully on {self.device}.")
                return self.pipeline
            except Exception as e:
                self._init_error = str(e)
                self.pipeline = None
                self._initialized = False
                print(f"[LocalEnglishSTT] Failed to load local English model: {e}")
                raise e

    def transcribe(self, audio_bytes: bytes, filename: str) -> str:
        """Transcribes audio bytes into English text with Indian accent robustness."""
        pipe = self.load_pipeline()
        pcm = decode_audio_to_pcm16k(audio_bytes, filename)
        if pcm is None or len(pcm) == 0:
            return ""

        result = pipe({"raw": pcm, "sampling_rate": 16000})
        if isinstance(result, dict):
            text = result.get("text", "")
        elif isinstance(result, list) and len(result) > 0:
            text = result[0].get("text", "")
        else:
            text = str(result)

        return (text or "").strip()


def transcribe_audio(audio_bytes: bytes, filename: str, target_lang: str = "kn") -> Dict[str, Any]:
    """
    Speech-to-Text Transcription with Priority Fallback Pipeline:
    1. Local Specialized Models:
       - Kannada: ai4bharat/indic-conformer-600m-multilingual (Native Kannada CTC/RNNT)
       - English: bryandts/whisper-base-en-india-accent-svarah (Fine-tuned on Svarah Indian English corpus)
    2. Fallback 1: Groq Whisper (whisper-large-v3, Cloud)
    3. Fallback 2: Gemini 1.5 Flash Audio (Google AI Studio Cloud)
    """
    t_voice_0 = time.perf_counter()
    tracker.log_voice_request(filename, len(audio_bytes), target_lang)
    errors = []

    is_kannada = (target_lang or "kn").lower().strip() in ["kn", "kannada", "kan"]

    # 1. Primary: Local STT (Specialized per language with separate .env toggles)
    use_local_kannada = getattr(settings, "is_local_kannada_stt_enabled", (settings.ENABLE_LOCAL_STT and getattr(settings, "ENABLE_LOCAL_KANNADA_STT", True)))
    use_local_english = getattr(settings, "is_local_english_stt_enabled", (settings.ENABLE_LOCAL_STT and getattr(settings, "ENABLE_LOCAL_ENGLISH_STT", True)))

    if is_kannada:
        if use_local_kannada:
            try:
                manager = IndicConformerSTTManager.get_instance()
                text = manager.transcribe(audio_bytes, filename, target_lang="kn")
                if text:
                    dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                    tracker.log_voice_step("IndicConformer (Local)", manager.device, dur_ms, text)
                    return {
                        "text": text,
                        "language": "kn",
                        "provider": "indic-conformer-local",
                        "device": manager.device,
                        "model": settings.INDIC_CONFORMER_MODEL_ID,
                    }
                else:
                    errors.append("IndicConformer returned empty transcription")
            except Exception as e:
                err_msg = f"Indic-Conformer STT error: {e}"
                errors.append(err_msg)
                print(f"[Cleaned Voice] {err_msg}. Falling back to Groq Whisper...")
        else:
            reason = "ENABLE_LOCAL_STT=false" if not settings.ENABLE_LOCAL_STT else "ENABLE_LOCAL_KANNADA_STT=false in .env"
            print(f"[Cleaned Voice] Local Kannada STT is bypassed ({reason}). Falling back directly to cloud providers...")
    else:
        # English / Indian-accent English
        if use_local_english:
            try:
                en_manager = LocalEnglishSTTManager.get_instance()
                text = en_manager.transcribe(audio_bytes, filename)
                if text:
                    dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                    tracker.log_voice_step("Whisper-Svarah Indian English (Local)", en_manager.device, dur_ms, text)
                    return {
                        "text": text,
                        "language": "en",
                        "provider": "local-whisper-indian-english",
                        "device": en_manager.device,
                        "model": en_manager.model_id,
                    }
                else:
                    errors.append("Local Indian English STT returned empty transcription")
            except Exception as e:
                err_msg = f"Local Indian English STT error: {e}"
                errors.append(err_msg)
                print(f"[Cleaned Voice] {err_msg}. Falling back to Groq Whisper...")
        else:
            reason = "ENABLE_LOCAL_STT=false" if not settings.ENABLE_LOCAL_STT else "ENABLE_LOCAL_ENGLISH_STT=false in .env"
            print(f"[Cleaned Voice] Local English STT is bypassed ({reason}). Falling back directly to cloud providers...")

    # 2. Fallback 1: Groq Whisper (whisper-large-v3)
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            g_client = Groq(api_key=settings.GROQ_API_KEY)
            transcription = g_client.audio.transcriptions.create(
                file=(filename, audio_bytes),
                model="whisper-large-v3",
                language="kn" if is_kannada else "en",
                response_format="json"
            )
            if transcription.text:
                dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                tracker.log_voice_step("Groq Whisper (whisper-large-v3)", "Cloud", dur_ms, transcription.text.strip())
                return {
                    "text": transcription.text.strip(),
                    "language": "kn" if is_kannada else "en",
                    "provider": "groq-whisper"
                }
        except Exception as e:
            err_msg = f"Groq Whisper error: {e}"
            errors.append(err_msg)
            print(f"[Cleaned Voice] {err_msg}. Falling back to Gemini Audio...")

    # 3. Fallback 2: Gemini 1.5 Flash Audio
    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=settings.GEMINI_API_KEY)

            mime_type = "audio/webm"
            lower_name = filename.lower()
            if lower_name.endswith(".wav"):
                mime_type = "audio/wav"
            elif lower_name.endswith(".mp3"):
                mime_type = "audio/mp3"
            elif lower_name.endswith(".ogg"):
                mime_type = "audio/ogg"
            elif lower_name.endswith(".flac"):
                mime_type = "audio/flac"

            audio_part = {"mime_type": mime_type, "data": audio_bytes}
            lang_prompt = (
                "Listen carefully to this farmer's voice and transcribe it accurately into NATIVE KANNADA SCRIPT (ಕನ್ನಡ ಲಿಪಿ). "
                "Even if spoken as Kanglish, output clean, natural Kannada script. Return ONLY the transcribed text."
                if is_kannada
                else "Listen carefully to this farmer's voice with an Indian accent and transcribe it accurately into English. Return ONLY the transcribed text."
            )
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content([lang_prompt, audio_part])
            if resp.text:
                dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                tracker.log_voice_step("Gemini Audio (gemini-1.5-flash)", "Cloud", dur_ms, resp.text.strip())
                return {
                    "text": resp.text.strip(),
                    "language": "kn" if is_kannada else "en",
                    "provider": "gemini-audio"
                }
        except Exception as e:
            err_msg = f"Gemini Audio error: {e}"
            errors.append(err_msg)
            print(f"[Cleaned Voice] {err_msg}")

    return {
        "text": "",
        "error": "Transcription unavailable across all STT providers.",
        "details": errors
    }

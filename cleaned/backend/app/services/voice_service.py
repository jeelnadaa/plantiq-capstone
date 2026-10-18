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

def _decode_audio_with_ffmpeg(audio_bytes: bytes, filename: str = "") -> Optional[np.ndarray]:
    """
    Decodes arbitrary audio bytes (e.g. webm, ogg, mp3, mp4, wav) to 16kHz mono float32 numpy array using ffmpeg.
    """
    ffmpeg_bin = shutil.which("ffmpeg") or (r"C:\ffmpeg\bin\ffmpeg.EXE" if os.path.exists(r"C:\ffmpeg\bin\ffmpeg.EXE") else None)
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

class IndicConformerSTTManager:
    """
    Thread-safe lazy-loaded singleton for ai4bharat/indic-conformer-600m-multilingual.
    Supports English ('en') and Kannada ('kn').
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
        """
        Loads audio from bytes and prepares mono 16kHz PyTorch tensor for the model.
        Supports WebM, OGG, MP3, WAV and all container formats seamlessly via FFmpeg, soundfile, and torchaudio.
        """
        import torch

        waveform = None
        sample_rate = 16000
        errors = {}

        # 1. Primary Strategy: FFmpeg decoding (universal support for browser WebM, OGG, MP4, etc.)
        try:
            data = _decode_audio_with_ffmpeg(audio_bytes, filename)
            if data is not None and len(data) > 0:
                waveform = torch.from_numpy(data)
                if waveform.ndim == 1:
                    waveform = waveform.unsqueeze(0)
                elif waveform.ndim == 2 and waveform.shape[0] > 1:
                    waveform = torch.mean(waveform, dim=0, keepdim=True)
                return waveform.to(self.device)
        except Exception as e_ffmpeg:
            errors["ffmpeg"] = str(e_ffmpeg)

        # 2. Secondary Strategy: soundfile
        try:
            import soundfile as sf
            data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
            sample_rate = sr
            if data.ndim == 1:
                waveform = torch.from_numpy(data).unsqueeze(0)
            else:
                waveform = torch.from_numpy(data.T)
        except Exception as e_sf:
            errors["soundfile"] = str(e_sf)

            # 3. Tertiary Strategy: torchaudio in memory
            try:
                import torchaudio
                waveform, sample_rate = torchaudio.load(io.BytesIO(audio_bytes))
            except Exception as e_ta_mem:
                errors["torchaudio_mem"] = str(e_ta_mem)

                # 4. Quaternary Strategy: torchaudio temporary file
                try:
                    import torchaudio
                    ext = os.path.splitext(filename)[1] or ".wav"
                    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                        tmp.write(audio_bytes)
                        tmp_path = tmp.name
                    try:
                        waveform, sample_rate = torchaudio.load(tmp_path)
                    finally:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                except Exception as e_ta_tmp:
                    errors["torchaudio_tmp"] = str(e_ta_tmp)
                    err_details = ", ".join([f"{k}=({v})" for k, v in errors.items()])
                    raise RuntimeError(f"Unable to decode audio format for '{filename}'. Errors: {err_details}")

        # Convert to mono if multi-channel
        if waveform.dim() == 2 and waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)
        elif waveform.dim() == 1:
            waveform = waveform.unsqueeze(0)

        # Resample to 16,000 Hz if needed
        if sample_rate != 16000:
            try:
                import torchaudio.transforms as T
                resampler = T.Resample(orig_freq=sample_rate, new_freq=16000)
                waveform = resampler(waveform)
            except Exception:
                # Fallback resampler using scipy or linear interpolation
                import scipy.signal
                num_target_samples = int(waveform.shape[-1] * 16000 / sample_rate)
                resampled_np = scipy.signal.resample(waveform.squeeze().numpy(), num_target_samples)
                waveform = torch.from_numpy(resampled_np).float().unsqueeze(0)

        return waveform.to(self.device)

    def transcribe(self, audio_bytes: bytes, filename: str, target_lang: str = "kn") -> str:
        """
        Transcribes audio bytes using the IndicConformer model.
        Maps target_lang to 'kn' (Kannada) or 'en' (English).
        """
        import torch

        # Normalize language code for IndicConformer
        lang_lower = (target_lang or "kn").lower().strip()
        if lang_lower in ["kn", "kannada", "kan"]:
            lang_code = "kn"
        elif lang_lower in ["en", "english", "eng"]:
            lang_code = "en"
        else:
            lang_code = lang_lower

        model = self.load_model()
        wav = self.preprocess_audio(audio_bytes, filename)

        with torch.no_grad():
            output = None
            # The model accepts (wav, lang, decoding_strategy)
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


def transcribe_audio(audio_bytes: bytes, filename: str, target_lang: str = "kn") -> Dict[str, Any]:
    """
    Speech-to-Text Transcription with Priority Fallback Pipeline:
    1. ai4bharat/indic-conformer-600m-multilingual (Default local model on GPU/CPU)
    2. Groq Whisper (WhisperFlow large-v3)
    3. Gemini 1.5 Flash Audio
    """
    t_voice_0 = time.perf_counter()
    tracker.log_voice_request(filename, len(audio_bytes), target_lang)
    errors = []

    # 1. Primary: Local Indic-Conformer 600M Multilingual (English & Kannada)
    if settings.ENABLE_LOCAL_STT:
        try:
            manager = IndicConformerSTTManager.get_instance()
            text = manager.transcribe(audio_bytes, filename, target_lang=target_lang)
            if text:
                dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                tracker.log_voice_step("IndicConformer (Local)", manager.device, dur_ms, text)
                return {
                    "text": text,
                    "language": target_lang,
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
        print("[Cleaned Voice] Local STT is disabled in settings. Skipping to Groq Whisper...")

    # 2. Fallback 1: Groq Whisper (whisper-large-v3)
    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            g_client = Groq(api_key=settings.GROQ_API_KEY)
            transcription = g_client.audio.transcriptions.create(
                file=(filename, audio_bytes),
                model="whisper-large-v3",
                language="kn" if target_lang.lower().startswith("kn") else "en",
                response_format="json"
            )
            if transcription.text:
                dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                tracker.log_voice_step("Groq Whisper (whisper-large-v3)", "Cloud", dur_ms, transcription.text.strip())
                return {
                    "text": transcription.text.strip(),
                    "language": target_lang,
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
                if target_lang.lower().startswith("kn")
                else "Listen carefully to this farmer's voice and transcribe it accurately into English. Return ONLY the transcribed text."
            )
            model = legacy_genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content([lang_prompt, audio_part])
            if resp.text:
                dur_ms = (time.perf_counter() - t_voice_0) * 1000.0
                tracker.log_voice_step("Gemini Audio (gemini-1.5-flash)", "Cloud", dur_ms, resp.text.strip())
                return {
                    "text": resp.text.strip(),
                    "language": target_lang,
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

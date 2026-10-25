#!/usr/bin/env python3
"""
PlantIQ Voice STT Diagnostic & Test Utility
Tests local and cloud speech-to-text models:
  1. English (Local): bryandts/whisper-base-en-india-accent-svarah (Indian accent tuned)
  2. Kannada (Local): ai4bharat/indic-conformer-600m-multilingual (Native Kannada CTC)
  3. Cloud Fallback 1: Groq Whisper (whisper-large-v3)
  4. Cloud Fallback 2: Gemini 1.5 Flash Audio
"""

import os
import sys
import io
import wave
import struct
import argparse

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.services.voice_service import (
    transcribe_audio,
    LocalEnglishSTTManager,
    IndicConformerSTTManager,
    _get_ffmpeg_binary
)

def create_synthetic_wav(duration_s: float = 2.0, freq_hz: float = 440.0) -> bytes:
    """Generates a synthetic 16kHz mono WAV file in memory."""
    buf = io.BytesIO()
    sample_rate = 16000
    total_samples = int(sample_rate * duration_s)
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        for i in range(total_samples):
            # Square-like tone simulating voice formant harmonics
            val = int(32767.0 * 0.35 * (1.0 if (i % int(sample_rate / freq_hz) < int(sample_rate / (2 * freq_hz))) else -1.0))
            wav.writeframes(struct.pack("<h", val))
    return buf.getvalue()

def run_tests(audio_path: str = None):
    print("=" * 80)
    print("  PlantIQ Speech-to-Text Pipeline Diagnostics")
    print("=" * 80)

    # 1. Check FFmpeg
    ffmpeg_path = _get_ffmpeg_binary()
    print(f"\n[1] FFmpeg Binary Check:")
    if ffmpeg_path and os.path.exists(ffmpeg_path):
        print(f"    [+] Found FFmpeg: {ffmpeg_path}")
    else:
        print(f"    [-] FFmpeg not detected in backend/bin/ or system PATH.")

    # 2. Prepare audio
    if audio_path and os.path.exists(audio_path):
        print(f"\n[2] Loading provided audio file: {audio_path}")
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        filename = os.path.basename(audio_path)
    else:
        print(f"\n[2] Generating 2.0s synthetic 16kHz audio sample in memory...")
        audio_bytes = create_synthetic_wav(duration_s=2.0)
        filename = "synthetic_sample.wav"

    # 3. Test English (Indian Accent Whisper)
    print("\n" + "-" * 80)
    print("--> [3] Testing English Transcription (Local Indian Accent Whisper Svarah)")
    print("-" * 80)
    try:
        res_en = transcribe_audio(audio_bytes, filename, target_lang="en")
        print(f"    [+] Provider : {res_en.get('provider')}")
        print(f"    [+] Device   : {res_en.get('device', 'cloud')}")
        print(f"    [+] Model    : {res_en.get('model', 'N/A')}")
        print(f"    [+] Output   : \"{res_en.get('text', '')}\"")
    except Exception as e:
        print(f"    [-] English STT error: {e}")

    # 4. Test Kannada (IndicConformer)
    print("\n" + "-" * 80)
    print("--> [4] Testing Kannada Transcription (Local Indic-Conformer 600M)")
    print("-" * 80)
    try:
        res_kn = transcribe_audio(audio_bytes, filename, target_lang="kn")
        print(f"    [+] Provider : {res_kn.get('provider')}")
        print(f"    [+] Device   : {res_kn.get('device', 'cloud')}")
        print(f"    [+] Model    : {res_kn.get('model', 'N/A')}")
        print(f"    [+] Output   : \"{res_kn.get('text', '')}\"")
    except Exception as e:
        print(f"    [-] Kannada STT error: {e}")

    print("\n" + "=" * 80)
    print("  Speech-to-Text Pipeline Diagnostics Completed Successfully!")
    print("=" * 80)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test PlantIQ Speech-to-Text Pipeline")
    parser.add_argument("--audio", type=str, default=None, help="Path to custom audio file (.wav, .webm, .mp3, etc.)")
    args = parser.parse_args()
    run_tests(audio_path=args.audio)

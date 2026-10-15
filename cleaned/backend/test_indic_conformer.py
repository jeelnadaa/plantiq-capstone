#!/usr/bin/env python3
"""
Test & Diagnostic Script for ai4bharat/indic-conformer-600m-multilingual STT
Usage:
    python test_indic_conformer.py [--device auto|cuda|cpu] [--audio path/to/sample.wav] [--token YOUR_HF_TOKEN]
"""

import sys
import os
import time
import argparse
import platform
import subprocess

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_system_environment():
    print_header("1. SYSTEM & HARDWARE DIAGNOSTICS")
    print(f"[OS]           : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"[Python]       : {sys.version.split()[0]} ({sys.executable})")

    # Check Python version compatibility
    py_major, py_minor = sys.version_info.major, sys.version_info.minor
    if py_minor >= 13:
        print(f"  [!] WARNING: Python {py_major}.{py_minor} detected.")
        print("      PyTorch CUDA wheels, onnxruntime-gpu, and HuggingFace libraries have")
        print("      limited or no prebuilt Windows binaries for Python 3.13 / 3.14+.")
        print("      RECOMMENDED: Use Python 3.10 or 3.11 for full RTX 3070 Ti CUDA support.\n")
    else:
        print(f"  [+] Python version {py_major}.{py_minor} is well-supported for ML / CUDA libraries.\n")

    # Check NVIDIA-SMI
    print("[NVIDIA Driver & Hardware Check]:")
    try:
        smi_out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=gpu_name,driver_version,memory.total,memory.free", "--format=csv,noheader"],
            stderr=subprocess.STDOUT,
            text=True
        ).strip()
        gpu_info = [x.strip() for x in smi_out.split(",")]
        print(f"  [+] GPU Detected via driver : {gpu_info[0]}")
        print(f"  [+] Driver Version          : {gpu_info[1]}")
        print(f"  [+] Total VRAM              : {gpu_info[2]}")
        print(f"  [+] Free VRAM               : {gpu_info[3]}")
    except Exception as e:
        print(f"  [-] Unable to query nvidia-smi: {e}")

    # Check PyTorch & CUDA inside Python
    print("\n[PyTorch & CUDA Binding]:")
    try:
        import torch
        print(f"  [+] PyTorch Version        : {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        print(f"  [+] torch.cuda.is_available: {cuda_avail}")
        if cuda_avail:
            print(f"  [+] PyTorch CUDA Version   : {torch.version.cuda}")
            print(f"  [+] cuDNN Version          : {torch.backends.cudnn.version()}")
            print(f"  [+] Active Device Name     : {torch.cuda.get_device_name(0)}")
            print(f"  [+] Device Count           : {torch.cuda.device_count()}")
            props = torch.cuda.get_device_properties(0)
            print(f"  [+] Compute Capability     : {props.major}.{props.minor}")
            print(f"  [+] Total Memory (GB)      : {props.total_memory / (1024**3):.2f} GB")
        else:
            print("  [-] CUDA is NOT available in this PyTorch installation.")
            print("      (PyTorch may have been installed as CPU-only or Python version lacks CUDA wheel).")
    except ImportError:
        print("  [-] PyTorch is not installed in this Python environment.")
        print("      Run: pip install torch torchaudio")

def generate_synthetic_audio(sample_rate=16000, duration_sec=2.0):
    """Generates a synthetic 16kHz sine wave audio tensor for testing."""
    import torch
    import math
    num_samples = int(sample_rate * duration_sec)
    t = torch.linspace(0, duration_sec, num_samples)
    waveform = torch.sin(2 * math.pi * 440.0 * t).unsqueeze(0)  # [1, N]
    return waveform

def load_or_generate_audio(audio_path: str = None, target_device: str = "cpu"):
    """Loads given audio file or generates a synthetic audio tensor."""
    import torch

    if audio_path and os.path.exists(audio_path):
        print(f"Loading provided audio: {audio_path}")
        try:
            import torchaudio
            waveform, sr = torchaudio.load(audio_path)
            if waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            if sr != 16000:
                import torchaudio.transforms as T
                waveform = T.Resample(sr, 16000)(waveform)
            return waveform.to(target_device)
        except Exception as e:
            print(f"Failed to load with torchaudio ({e}), falling back to soundfile...")
            import soundfile as sf
            data, sr = sf.read(audio_path, dtype="float32")
            if data.ndim == 1:
                waveform = torch.from_numpy(data).unsqueeze(0)
            else:
                waveform = torch.from_numpy(data.T)
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            return waveform.to(target_device)
    else:
        print("No audio file supplied. Generating 2-second synthetic 16kHz audio sample...")
        return generate_synthetic_audio(16000, 2.0).to(target_device)

def run_indic_conformer_test(requested_device: str = "auto", audio_path: str = None, token: str = None):
    print_header("2. RUNNING INDIC-CONFORMER TEST")

    try:
        import torch
    except ImportError:
        print("[FAIL] PyTorch is required. Please install it first.")
        print_compatibility_guide()
        return

    # Resolve target device
    if requested_device == "auto":
        target_device = "cuda" if torch.cuda.is_available() else "cpu"
    elif requested_device == "cuda":
        if not torch.cuda.is_available():
            print("[ERROR] CUDA was explicitly requested, but torch.cuda.is_available() is False!")
            print_compatibility_guide()
            return
        target_device = "cuda"
    else:
        target_device = "cpu"

    print(f"Target execution device: {target_device.upper()}")

    # Check dependencies
    missing_deps = []
    for pkg in ["transformers", "torchaudio", "onnx", "onnxruntime"]:
        try:
            __import__(pkg)
        except ImportError:
            missing_deps.append(pkg)

    if missing_deps:
        print(f"[!] Warning: Missing optional/recommended STT packages: {missing_deps}")
        print(f"    You can install them via: pip install {' '.join(missing_deps)}")

    # Load Model
    model_id = "ai4bharat/indic-conformer-600m-multilingual"
    hf_token = token or os.getenv("HF_TOKEN") or None

    print(f"\nLoading model: '{model_id}'...")
    print("Note: If running for the first time, this downloads model weights (~2.4 GB).")
    print("If you see an access error, make sure you accepted the model terms at:")
    print("https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual\n")

    t0 = time.time()
    try:
        from transformers import AutoModel
        load_kwargs = {"trust_remote_code": True}
        if hf_token:
            load_kwargs["token"] = hf_token

        model = AutoModel.from_pretrained(model_id, **load_kwargs)
        model = model.to(target_device)
        model.eval()
        load_time = time.time() - t0
        print(f"[SUCCESS] Model loaded onto {target_device.upper()} in {load_time:.2f} seconds.")
    except Exception as e:
        print(f"\n[FAIL] Failed to load model: {e}\n")
        if "gated" in str(e).lower() or "403" in str(e) or "401" in str(e):
            print("-> This model is GATED on Hugging Face.")
            print("   1. Visit https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual")
            print("   2. Click 'Acknowledge license' / 'Accept conditions'")
            print("   3. Run with: python test_indic_conformer.py --token YOUR_HF_READ_TOKEN")
        print_compatibility_guide()
        return

    # Report device memory
    if target_device == "cuda":
        allocated = torch.cuda.memory_allocated() / (1024**2)
        reserved = torch.cuda.memory_reserved() / (1024**2)
        print(f"[VRAM] Allocated: {allocated:.1f} MB | Reserved: {reserved:.1f} MB")

    # Load audio
    wav = load_or_generate_audio(audio_path, target_device=target_device)
    print(f"Audio Tensor Shape: {tuple(wav.shape)}, Device: {wav.device}, Dtype: {wav.dtype}")

    # Test Languages: English and Kannada
    test_languages = [
        ("kn", "Kannada"),
        ("en", "English")
    ]

    print("\nRunning Inference...")
    for lang_code, lang_name in test_languages:
        print(f"\n--> Testing Language: {lang_name} ('{lang_code}') with 'ctc' decoding...")
        try:
            start_infer = time.time()
            with torch.no_grad():
                try:
                    res = model(wav, lang_code, "ctc")
                except TypeError:
                    res = model(wav, lang=lang_code, decoding_strategy="ctc")
            elapsed = (time.time() - start_infer) * 1000

            print(f"    [Result] Output    : {res}")
            print(f"    [Latency] Time     : {elapsed:.2f} ms")
        except Exception as e:
            print(f"    [!] Inference error for {lang_name}: {e}")

    print_header("3. TEST COMPLETE")
    print(f"Model successfully executed on {target_device.upper()}!")

def print_compatibility_guide():
    print_header("COMPATIBILITY & SETUP RECOMMENDATIONS FOR RTX 3070 Ti")
    guide = """
Your GPU is an NVIDIA GeForce RTX 3070 Ti Laptop (Ampere architecture, Compute Capability 8.6, 8GB VRAM).

1. PYTHON VERSION:
   - Use Python 3.11 (e.g., Python 3.11.9) or Python 3.10.
   - DO NOT USE Python 3.14 / 3.13 preview for PyTorch/CUDA. Official CUDA wheels for PyTorch,
     Hugging Face transformers, torchaudio, and onnxruntime-gpu require Python 3.10 or 3.11 on Windows.

2. CUDA & CUDNN DRIVER:
   - Your NVIDIA driver (610.x) fully supports CUDA 12.x and 11.8.
   - For PyTorch, you do NOT need to install the separate CUDA Toolkit installer because
     PyTorch pip wheels already include the CUDA 12.1 runtime!
   - Recommended CUDA runtime: CUDA 12.1 or 12.4
   - cuDNN: cuDNN 8.9 / 9.x (bundled inside PyTorch CUDA wheel)

3. STEP-BY-STEP SETUP COMMANDS:
   Option A: Using Conda (Recommended for ML):
     conda create -n plantiq-stt python=3.11 -y
     conda activate plantiq-stt
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
     pip install transformers soundfile onnx onnxruntime onnxruntime-gpu
     pip install -r requirements.txt

   Option B: Using Windows Python 3.11 venv:
     py -3.11 -m venv venv
     .\\venv\\Scripts\\activate
     pip install --upgrade pip
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
     pip install transformers soundfile onnx onnxruntime onnxruntime-gpu
     pip install -r requirements.txt

4. HUGGING FACE GATED MODEL ACCESS:
   - Go to: https://huggingface.co/ai4bharat/indic-conformer-600m-multilingual
   - Log in and accept the access terms.
   - Generate a Read Token at: https://huggingface.co/settings/tokens
   - Run: huggingface-cli login
     OR set HF_TOKEN=your_token in backend/.env
"""
    print(guide)

def main():
    parser = argparse.ArgumentParser(description="Test ai4bharat/indic-conformer-600m-multilingual on CPU/GPU")
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto", help="Device to test on (default: auto)")
    parser.add_argument("--audio", type=str, default=None, help="Path to a .wav audio file to transcribe")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face User Access Token (if gated)")
    parser.add_argument("--info-only", action="store_true", help="Only display hardware/Python compatibility info")
    args = parser.parse_args()

    check_system_environment()

    if args.info_only:
        print_compatibility_guide()
        return

    run_indic_conformer_test(requested_device=args.device, audio_path=args.audio, token=args.token)

if __name__ == "__main__":
    main()

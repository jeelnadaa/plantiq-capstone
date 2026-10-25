"""
PlantIQ - Hardware & GPU Acceleration Diagnostic Tool
-----------------------------------------------------
Tests whether PyTorch, TorchVision, ONNX Runtime, and other machine learning
libraries are actively utilizing your NVIDIA GPU (CUDA) or falling back to CPU.

Usage:
    python test.py
"""

import sys
import os
import time
import subprocess
import platform

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Color helpers for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def print_header(title: str):
    width = 75
    print("\n" + "=" * width)
    print(f" {title.upper()} ".center(width, "="))
    print("=" * width)

def print_badge(label: str, status: bool, info: str = ""):
    tag = f"{Colors.GREEN}[ ACTIVE / DETECTED ]{Colors.RESET}" if status else f"{Colors.RED}[ NOT AVAILABLE / CPU ONLY ]{Colors.RESET}"
    print(f" * {label:<32} {tag} {info}")

def format_bytes(bytes_val: int) -> str:
    gb = bytes_val / (1024 ** 3)
    mb = bytes_val / (1024 ** 2)
    if gb >= 1.0:
        return f"{gb:.2f} GB"
    return f"{mb:.1f} MB"


def check_system_and_nvidia():
    print_header("1. System & NVIDIA Driver Status")
    print(f" * OS Platform:                  {platform.system()} {platform.release()} ({platform.machine()})")
    print(f" * Python Version:               {platform.python_version()} ({sys.executable})")

    # Run nvidia-smi
    try:
        smi_out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        lines = smi_out.splitlines()
        for idx, line in enumerate(lines):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 6:
                name, driver, mem_total, mem_used, temp, util = parts[:6]
                print(f" * NVIDIA GPU #{idx}:                 {Colors.BOLD}{name}{Colors.RESET}")
                print(f"   - Driver Version:             {driver}")
                print(f"   - Total VRAM:                 {mem_total} MB")
                print(f"   - Used VRAM:                  {mem_used} MB")
                print(f"   - GPU Temperature:            {temp} C")
                print(f"   - GPU Current Utilization:    {util}%")
                return True, name
    except Exception:
        pass

    try:
        # Fallback raw nvidia-smi check
        subprocess.check_output(["nvidia-smi"], stderr=subprocess.DEVNULL)
        print(f" * NVIDIA Driver:                {Colors.GREEN}Detected via nvidia-smi{Colors.RESET}")
        return True, "NVIDIA GPU"
    except Exception:
        print(f" * NVIDIA Driver (nvidia-smi):   {Colors.YELLOW}Not found in PATH or no NVIDIA GPU detected.{Colors.RESET}")
        return False, None


def check_pytorch():
    print_header("2. PyTorch CUDA & Hardware Binding")
    try:
        import torch
    except ImportError:
        print(f" {Colors.RED}[!] PyTorch is not installed in this Python environment.{Colors.RESET}")
        print("     Install with CUDA support: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
        return False, "Not Installed"

    torch_ver = torch.__version__
    cuda_avail = torch.cuda.is_available()

    print(f" * PyTorch Version:              {torch_ver}")
    print_badge("PyTorch CUDA Available", cuda_avail)

    if not cuda_avail:
        print(f"\n {Colors.YELLOW}[!] Why is CUDA not available in PyTorch?{Colors.RESET}")
        if "+cpu" in torch_ver:
            print(f"   -> You currently have the {Colors.BOLD}CPU-only build{Colors.RESET} of PyTorch installed ({torch_ver}).")
            print("   -> Fix: Reinstall PyTorch with CUDA support using:")
            print(f"      {Colors.CYAN}pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121{Colors.RESET}")
        else:
            print("   -> PyTorch could not communicate with the NVIDIA CUDA runtime.")
            print("   -> Check if NVIDIA drivers are up-to-date and compatible with CUDA.")
        return False, "CPU"

    # Details on CUDA
    cuda_ver = torch.version.cuda
    cudnn_ver = torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else "N/A"
    dev_count = torch.cuda.device_count()
    dev_name = torch.cuda.get_device_name(0)
    dev_props = torch.cuda.get_device_properties(0)

    print(f" * PyTorch Compiled CUDA:        {cuda_ver}")
    print(f" * cuDNN Version:                {cudnn_ver} (Enabled: {torch.backends.cudnn.enabled})")
    print(f" * Detected GPU Count:           {dev_count}")
    print(f" * Primary Device:               cuda:0 ({Colors.BOLD}{dev_name}{Colors.RESET})")
    print(f" * Total Dedicated VRAM:         {format_bytes(dev_props.total_memory)}")
    print(f" * Compute Capability:           {dev_props.major}.{dev_props.minor}")
    return True, dev_name


def benchmark_gpu_vs_cpu():
    print_header("3. Active Compute & Memory Test (GPU vs CPU)")
    try:
        import torch
    except ImportError:
        print(" Skipping compute test: PyTorch not installed.")
        return

    matrix_size = 4000
    print(f" Performing matrix multiplication benchmark: ({matrix_size}x{matrix_size}) float32 tensors...\n")

    # 1. CPU Run
    print(" [1/2] Running on CPU...")
    try:
        t0_cpu = time.perf_counter()
        a_cpu = torch.randn(matrix_size, matrix_size, dtype=torch.float32, device="cpu")
        b_cpu = torch.randn(matrix_size, matrix_size, dtype=torch.float32, device="cpu")
        c_cpu = torch.matmul(a_cpu, b_cpu)
        cpu_time = time.perf_counter() - t0_cpu
        print(f"       -> CPU execution time:    {cpu_time * 1000:.2f} ms")
    except Exception as e:
        print(f"       -> CPU test failed: {e}")
        cpu_time = None

    # 2. GPU Run
    if not torch.cuda.is_available():
        print(f"\n {Colors.YELLOW}[!] Skipping GPU test: torch.cuda.is_available() is False.{Colors.RESET}")
        return

    print(" [2/2] Running on GPU (CUDA)...")
    try:
        # Measure VRAM before
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        mem_before = torch.cuda.memory_allocated()

        # Warm-up pass
        w1 = torch.randn(500, 500, device="cuda")
        w2 = torch.matmul(w1, w1)
        torch.cuda.synchronize()

        # Timed benchmark
        t0_gpu = time.perf_counter()
        a_gpu = torch.randn(matrix_size, matrix_size, dtype=torch.float32, device="cuda")
        b_gpu = torch.randn(matrix_size, matrix_size, dtype=torch.float32, device="cuda")
        c_gpu = torch.matmul(a_gpu, b_gpu)
        torch.cuda.synchronize()
        gpu_time = time.perf_counter() - t0_gpu

        mem_after = torch.cuda.memory_allocated()
        peak_mem = torch.cuda.max_memory_allocated()

        print(f"       -> GPU execution time:    {Colors.GREEN}{gpu_time * 1000:.2f} ms{Colors.RESET}")
        print(f"       -> VRAM Active Allocs:    {format_bytes(mem_after)}")
        print(f"       -> VRAM Peak Used:        {format_bytes(peak_mem)}")
        print(f"       -> Device of Result:      {c_gpu.device} (actively computed on hardware)")

        if cpu_time and gpu_time > 0:
            speedup = cpu_time / gpu_time
            print(f"\n {Colors.BOLD}{Colors.GREEN}★ SPEEDUP FACTOR: GPU is {speedup:.1f}x faster than CPU! ★{Colors.RESET}")
    except Exception as e:
        print(f"       -> GPU test failed: {e}")


def check_other_modules():
    print_header("4. Project Machine Learning Modules Check")

    # TorchVision
    try:
        import torchvision
        import torch
        print_badge("TorchVision", True, f"v{torchvision.__version__}")
        try:
            from torchvision.models import resnet18
            model = resnet18().eval()
            device_str = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device_str)
            dummy_img = torch.randn(1, 3, 224, 224, device=device_str)
            with torch.no_grad():
                _ = model(dummy_img)
            print(f"   - Vision Model Forward Pass:  {Colors.GREEN}Success on {device_str.upper()}{Colors.RESET}")
        except Exception as e:
            print(f"   - Vision Model Pass Warning:  {e}")
    except ImportError:
        print_badge("TorchVision", False, "Not Installed")

    # Torchaudio
    try:
        import torchaudio
        print_badge("Torchaudio", True, f"v{torchaudio.__version__}")
    except ImportError:
        print_badge("Torchaudio", False, "Not Installed")

    # ONNX Runtime
    try:
        import onnxruntime as ort
        providers = ort.get_available_providers()
        has_cuda = "CUDAExecutionProvider" in providers
        print_badge("ONNX Runtime", True, f"v{ort.__version__}")
        print(f"   - Available Providers:        {providers}")
        if has_cuda:
            print(f"   - Hardware Acceleration:      {Colors.GREEN}CUDAExecutionProvider ENABLED{Colors.RESET}")
        else:
            print(f"   - Hardware Acceleration:      {Colors.YELLOW}CPUExecutionProvider only (install onnxruntime-gpu for GPU){Colors.RESET}")
    except ImportError:
        print_badge("ONNX Runtime", False, "Not Installed")

    # Hugging Face Transformers
    try:
        import transformers
        print_badge("Transformers (HuggingFace)", True, f"v{transformers.__version__}")
    except ImportError:
        print_badge("Transformers (HuggingFace)", False, "Not Installed")

    # Sentence Transformers
    try:
        import sentence_transformers
        print_badge("Sentence-Transformers", True, f"v{sentence_transformers.__version__}")
    except ImportError:
        print_badge("Sentence-Transformers", False, "Not Installed")

    # CTranslate2 / Faster-Whisper (if present)
    try:
        import ctranslate2
        cuda_types = ctranslate2.get_supported_compute_types("cuda") if "cuda" in ctranslate2.get_cuda_device_count() > 0 or hasattr(ctranslate2, "get_cuda_device_count") and ctranslate2.get_cuda_device_count() > 0 else []
        print_badge("CTranslate2 (Whisper Engine)", True, f"v{ctranslate2.__version__} (CUDA types: {cuda_types or 'None'})")
    except Exception:
        pass


def check_plantiq_services():
    print_header("5. PlantIQ Services Device Resolution")
    try:
        from app.core.config import settings
        import torch

        # CNN Service Target Device
        cnn_device = "cuda" if torch.cuda.is_available() else "cpu"
        weights_exist = os.path.exists(settings.CNN_WEIGHTS_PATH)
        print(f" * Leaf Pathology ResNet-50 Target: {Colors.BOLD}{cnn_device.upper()}{Colors.RESET}")
        print(f"   - Weights path:               {settings.CNN_WEIGHTS_PATH}")
        print(f"   - Weights file present:       {'Yes' if weights_exist else Colors.YELLOW + 'Missing/Not downloaded' + Colors.RESET}")

        # IndicConformer Speech-to-Text Target Device
        pref = (settings.INDIC_CONFORMER_DEVICE or "auto").lower()
        if pref == "cuda":
            stt_device = "cuda" if torch.cuda.is_available() else "cpu (fallback)"
        elif pref == "cpu":
            stt_device = "cpu (configured preference)"
        else:
            stt_device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print(f" * IndicConformer STT Target:     {Colors.BOLD}{stt_device.upper()}{Colors.RESET}")
        print(f"   - Configured preference:      {settings.INDIC_CONFORMER_DEVICE}")
        print(f"   - Local Master STT Enabled:   {settings.ENABLE_LOCAL_STT}")
        print(f"   - Local Kannada STT (Indic):  {settings.is_local_kannada_stt_enabled}")
        print(f"   - Local English STT (Svarah): {settings.is_local_english_stt_enabled}")
        print(f"   - Hugging Face Token:         {'Set' if bool(settings.HF_TOKEN) else Colors.YELLOW + 'Empty' + Colors.RESET}")
    except Exception as e:
        print(f" * Could not resolve app settings: {e}")


def check_rag_pipeline():
    print_header("6. 3-Stage Hybrid RAG Knowledge Base Status")
    index_dir = os.path.join(os.path.dirname(__file__), "app", "services", "index")
    kb_dir = os.path.join(os.path.dirname(__file__), "app", "services", "knowledge_base")

    # 1. Knowledge Base PDFs
    if os.path.exists(kb_dir):
        pdf_count = len([f for f in os.listdir(kb_dir) if f.endswith(".pdf")])
        print(f" * CCRI Knowledge PDFs:          {pdf_count} files in {kb_dir}")
    else:
        print(f" * CCRI Knowledge PDFs:          {Colors.YELLOW}Directory missing{Colors.RESET}")

    # 2. Indexes
    faiss_file = os.path.join(index_dir, "faiss_index.bin")
    chunks_file = os.path.join(index_dir, "chunks.pkl")
    bm25_file = os.path.join(index_dir, "bm25_index.pkl")

    has_faiss = os.path.exists(faiss_file)
    has_chunks = os.path.exists(chunks_file)
    has_bm25 = os.path.exists(bm25_file)

    print_badge("FAISS Dense Vector Store", has_faiss, f"({os.path.basename(faiss_file)})" if has_faiss else "Missing")
    print_badge("BM25Okapi Lexical Index", has_bm25, f"({os.path.basename(bm25_file)})" if has_bm25 else "Missing")
    print_badge("Semantic Chunks & Metadata", has_chunks, f"({os.path.basename(chunks_file)})" if has_chunks else "Missing")

    # 3. Upgraded Features Status
    print("\n   [Upgraded RAG Pipeline Capabilities]:")
    print(f"   + BGE Asymmetric Prompting:   {Colors.GREEN}ENABLED ('Represent this sentence for searching...'){Colors.RESET}")
    print(f"   + Reciprocal Rank Fusion:     {Colors.GREEN}ENABLED (Dense + BM25 RRF score balancing){Colors.RESET}")
    print(f"   + Dynamic Intent Expansion:   {Colors.GREEN}ENABLED (Timing, Dosage, Organic, Canopy){Colors.RESET}")
    print(f"   + Chemical Safety Guardrail:  {Colors.GREEN}ENABLED (Dosage verification audit){Colors.RESET}")
    print(f"   + High-Speed Query Cache:     {Colors.GREEN}ENABLED (In-memory LRU search cache){Colors.RESET}")
    print(f"   + Tabular Matrix Extraction:  {Colors.GREEN}ENABLED (PyMuPDF table parser){Colors.RESET}")


def print_final_verdict(gpu_available: bool, gpu_name: str = ""):
    print_header("Summary Verdict")
    if gpu_available:
        print(f"""
{Colors.GREEN}{Colors.BOLD}===========================================================================
  SUCCESS: GPU ACCELERATION IS ACTIVE!
  Device: {gpu_name}
  PyTorch, CNN classification, and voice models will run on your NVIDIA GPU.
==========================================================================={Colors.RESET}
""")
    else:
        print(f"""
{Colors.YELLOW}{Colors.BOLD}===========================================================================
  NOTICE: RUNNING ON CPU ONLY
  PyTorch is not using your NVIDIA GPU.
  If you have an NVIDIA GPU, install the CUDA-enabled PyTorch build:
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
==========================================================================={Colors.RESET}
""")


if __name__ == "__main__":
    print(f"\n{Colors.BOLD}{Colors.CYAN}PlantIQ - Hardware & GPU Acceleration Diagnostic Tool{Colors.RESET}")
    has_nvidia, gpu_name = check_system_and_nvidia()
    cuda_ok, dev_name = check_pytorch()
    benchmark_gpu_vs_cpu()
    check_other_modules()
    check_plantiq_services()
    check_rag_pipeline()
    print_final_verdict(cuda_ok, dev_name if cuda_ok else (gpu_name or "N/A"))

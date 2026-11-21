"""GPU check, seeding and run metadata (written into every result file)."""
from __future__ import annotations

import json
import platform
import random
import subprocess
import time
from pathlib import Path

from . import config


def require_cuda(allow_cpu: bool = False):
    """Stop the notebook if PyTorch cannot see the NVIDIA GPU, and turn on the fast-training switches."""
    import torch

    if not torch.cuda.is_available():
        if allow_cpu:
            print("WARNING: CUDA not available, running on CPU")
            return torch.device("cpu")
        raise RuntimeError(
            "PyTorch cannot see the GPU. Make sure the notebook kernel is 'PlantIQ compare (GPU)' "
            "(compare/.venv) and that torch was installed from the CUDA index (see compare/README.md, step 1).")
    torch.backends.cudnn.benchmark = True
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    dev = torch.device("cuda")
    print(f"Using GPU: {torch.cuda.get_device_name(0)} | torch {torch.__version__} | CUDA {torch.version.cuda}")
    return dev


def seed_everything(seed: int = config.SEED) -> None:
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=config.REPO,
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unknown"


def run_meta(**extra) -> dict:
    import torch

    meta = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "git_commit": git_commit(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "cpu": platform.processor(),
        "seed": config.SEED,
        "smoke": config.SMOKE,
    }
    folds_sha = config.AUDIT_DIR / "splits.csv.sha256"
    if folds_sha.exists():
        meta["splits_sha256"] = folds_sha.read_text().split()[0]
    meta.update(extra)
    return meta


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=_default), encoding="utf-8")


def _default(o):
    try:
        import numpy as np

        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if isinstance(o, Path):
        return str(o)
    raise TypeError(f"not JSON serialisable: {type(o)}")

"""Paths, class names and run-mode switches shared by every notebook."""
from __future__ import annotations

import os
from pathlib import Path

# compare/ is the folder that contains this package
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent

try:  # compare/.env can set PLANTIQ_FOLDS (and the API keys used by the RAG notebooks)
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env", override=False)
except ImportError:
    pass

SEED = 42
N_FOLDS = int(os.getenv("PLANTIQ_FOLDS", "5"))
# SMOKE=1 runs every notebook end-to-end on a tiny budget to check the pipeline. Smoke runs write ONLY into
# compare/_smoke/, so they can never mix with real results.
SMOKE = os.getenv("PLANTIQ_SMOKE", "0") == "1"
_OUT = ROOT / "_smoke" if SMOKE else ROOT

DATA_DIR = ROOT / "dataset-coffee-leaves-images" / "Original"
AUDIT_DIR = ROOT / "01_dataset_audit" / "outputs"       # the audit is deterministic and always real
RUNS_DIR = _OUT / "02_cnn" / "runs"
RESULTS_DIR = _OUT / "results"
CNN_RESULTS = RESULTS_DIR / "cnn"
CNN_PREDS = CNN_RESULTS / "preds"
RAG_RESULTS = RESULTS_DIR / "rag"
FIG_DIR = RESULTS_DIR / "figures"
RAG_DIR = ROOT / "03_rag"
KB_DIR = RAG_DIR / "kb"
RAG_DATA = (_OUT / "03_rag" / "data") if SMOKE else RAG_DIR / "data"
RAG_INDEX = _OUT / "03_rag" / "index"

# Read-only inputs taken from the PlantIQ app (never written to)
DEPLOYED_WEIGHTS = REPO / "backend" / "data" / "models" / "best_resnet50_coffee.pth"
APP_KB_DIR = REPO / "backend" / "data" / "knowledge_base"

# Class order of the deployed backend model (backend/app/services/cnn.py). Every model here outputs in this order,
# so a better ResNet-50 is a drop-in replacement.
CLASSES = ["Miner", "Rust", "Phoma", "Healthy", "Cerscospora"]
FOLDER_TO_CLASS = {"Miner": "Miner", "Leaf rust": "Rust", "Phoma": "Phoma", "Healthy": "Healthy",
                   "Cerscospora": "Cerscospora"}
CLASS_TO_IDX = {c: i for i, c in enumerate(CLASSES)}
PRETTY = {"Miner": "Leaf miner", "Rust": "Leaf rust", "Phoma": "Phoma", "Healthy": "Healthy",
          "Cerscospora": "Cercospora"}

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
STORE_SIZE = 128          # images are kept in RAM at 128x128 (95% of the dataset is natively 128x128)
CONF_GATE = 0.75          # PlantIQ's confidence gate (CONFIDENCE_THRESHOLD_CNN = 75 %)
DEPLOYED_CPU_MS = 54.9    # current model's CPU latency reported in the paper



def ensure_dirs() -> None:
    for d in (AUDIT_DIR, RUNS_DIR, CNN_RESULTS, CNN_PREDS, RAG_RESULTS, FIG_DIR, KB_DIR, RAG_DATA, RAG_INDEX):
        d.mkdir(parents=True, exist_ok=True)

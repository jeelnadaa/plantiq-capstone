"""
app.py
======
FastAPI Server for PlantIQ Model Comparator Web Application.
Serves interactive comparison dashboard on port 8501 (or user-defined port).
"""

import os
import glob
from io import BytesIO
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pydantic import BaseModel

from .dual_model_service import get_model_comparator, CANONICAL_CLASSES

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
SAMPLES_DIR = os.path.join(BASE_DIR, "sample_images")

app = FastAPI(
    title="PlantIQ Dual CNN Model Comparator & Benchmark Suite",
    version="1.0.0",
    description="Interactive side-by-side evaluation of Old ResNet-50 vs New Custom CNN on coffee leaf pathology."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and sample images
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/sample_images", StaticFiles(directory=SAMPLES_DIR), name="sample_images")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(TEMPLATES_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>PlantIQ Model Comparator UI loading...</h1>")


@app.get("/api/samples")
async def get_sample_images():
    """Returns preset test images available for 1-click comparison."""
    samples = []
    if os.path.exists(SAMPLES_DIR):
        for f in sorted(glob.glob(os.path.join(SAMPLES_DIR, "*.jpg"))):
            fname = os.path.basename(f)
            label = fname.replace("_sample.jpg", "").replace("_", " ").title()
            samples.append({
                "filename": fname,
                "label": f"{label} Leaf",
                "url": f"/sample_images/{fname}"
            })
    return {"samples": samples}


@app.post("/api/compare")
async def compare_leaf_models(
    file: Optional[UploadFile] = File(None),
    sample_filename: Optional[str] = Form(None)
):
    """
    Executes parallel inference across both CNN architectures on the provided leaf.
    Accepts direct image file upload OR a sample image filename.
    """
    comparator = get_model_comparator()
    image_bytes = None

    if file and file.filename:
        image_bytes = await file.read()
    elif sample_filename:
        sample_path = os.path.join(SAMPLES_DIR, sample_filename)
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as sf:
                image_bytes = sf.read()
        else:
            raise HTTPException(status_code=404, detail="Sample image not found")

    if not image_bytes:
        raise HTTPException(status_code=400, detail="No image provided. Please upload an image or choose a sample.")

    results = comparator.predict_dual(image_bytes)
    return JSONResponse(content=results)


@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "service": "PlantIQ Model Comparator",
        "canonical_classes": CANONICAL_CLASSES
    }

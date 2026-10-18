"""
image_guard.py
==============
Security utility for validating and sanitizing uploaded leaf photographs:
1. Validates magic bytes (JPEG, PNG, WebP) to prevent polyglot/binary upload attacks.
2. Enforces strict file size bounds (max 10MB) and prevents zero-byte uploads.
3. Protects against PIL decompression bombs (dimension bounds <= 4096px).
4. Strips all EXIF metadata (camera serial numbers, timestamps, GPS geotags).
5. Re-encodes images into clean RGB byte streams.
6. Sanitizes client filenames to eliminate directory traversal (../) risks.
"""

import io
import re
import os
from PIL import Image
from fastapi import HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_DIMENSION = 4096
Image.MAX_IMAGE_PIXELS = 25_000_000  # Guard against PIL decompression bombs

def validate_and_sanitize_image(image_bytes: bytes, filename: str = "leaf.jpg") -> tuple[bytes, str]:
    """
    Validates upload against magic bytes and size constraints, strips all EXIF metadata,
    and returns a clean, sanitized JPEG byte stream along with a safe filename.
    """
    if not image_bytes or len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(image_bytes) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE // (1024*1024)}MB.")

    # 1. Magic byte signatures verification
    is_jpeg = image_bytes.startswith(b"\xff\xd8\xff")
    is_png = image_bytes.startswith(b"\x89PNG\r\n\x1a\n")
    is_webp = image_bytes.startswith(b"RIFF") and len(image_bytes) >= 12 and image_bytes[8:12] == b"WEBP"

    if not (is_jpeg or is_png or is_webp):
        raise HTTPException(status_code=400, detail="Invalid image file format. Only JPEG, PNG, and WebP images are permitted.")

    # 2. Decompression bomb check & dimension bounds
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                raise HTTPException(status_code=400, detail=f"Image dimensions ({img.width}x{img.height}) exceed maximum allowed limit of {MAX_DIMENSION}x{MAX_DIMENSION} pixels.")
            
            # 3. EXIF stripping and re-encoding to clean RGB JPEG
            clean_io = io.BytesIO()
            clean_img = img.convert("RGB")
            clean_img.save(clean_io, format="JPEG", quality=92, optimize=True)
            sanitized_bytes = clean_io.getvalue()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Corrupted or invalid image data: {e}")

    # 4. Sanitize filename (prevent path traversal / injection)
    safe_name = os.path.basename(filename or "leaf.jpg")
    safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', safe_name)
    if not safe_name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        safe_name = f"{safe_name}.jpg"

    return sanitized_bytes, safe_name

"""Upload guards for images and audio.

Images: magic bytes (JPEG/PNG/WebP), size ≤ 10 MB, dimensions ≤ 4096 px, decompression-bomb guard,
EXIF/GPS stripped by re-encoding to RGB JPEG, filename sanitised (path traversal).
Audio: size ≤ 10 MB, container sniffing (webm/ogg/wav/mp3/mp4/flac/aac).
"""
from __future__ import annotations

import base64
import binascii
import io
import os
import re
from dataclasses import dataclass

from fastapi import HTTPException
from PIL import Image, ImageOps

MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_DIMENSION = 4096
MAX_AUDIO_BYTES = 10 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 25_000_000


@dataclass
class CleanImage:
    data: bytes
    filename: str
    width: int
    height: int


def sanitize_filename(name: str | None, default: str = "leaf.jpg") -> str:
    base = os.path.basename((name or default).replace("\\", "/"))
    base = re.sub(r"[^A-Za-z0-9_.-]", "_", base).lstrip(".")[:120] or default
    root, _ = os.path.splitext(base)
    return f"{root or 'image'}.jpg"


def sniff_image(data: bytes) -> str | None:
    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None


def clean_image(data: bytes, filename: str | None = None, max_side: int | None = None, quality: int = 90) -> CleanImage:
    if not data:
        raise HTTPException(400, "The image file is empty.")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(413, "Image is larger than 10 MB. Please choose a smaller photo.")
    if not sniff_image(data):
        raise HTTPException(415, "Only JPEG, PNG or WebP photos are allowed.")
    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
                raise HTTPException(400, f"Image is too large ({img.width}×{img.height}). Maximum is {MAX_DIMENSION} px.")
            img.load()
            img = ImageOps.exif_transpose(img)  # keep the orientation the farmer saw, then drop EXIF
            rgb = img.convert("RGB")
            if max_side and max(rgb.size) > max_side:
                rgb.thumbnail((max_side, max_side))
            out = io.BytesIO()
            rgb.save(out, format="JPEG", quality=quality, optimize=True)  # no exif= → metadata stripped
            return CleanImage(out.getvalue(), sanitize_filename(filename), rgb.width, rgb.height)
    except HTTPException:
        raise
    except Image.DecompressionBombError as exc:
        raise HTTPException(400, "Image has too many pixels.") from exc
    except Exception as exc:
        raise HTTPException(400, "The image could not be read. It may be corrupted.") from exc


def decode_data_url(value: str, max_bytes: int = MAX_IMAGE_BYTES) -> bytes:
    raw = value.split(",", 1)[1] if value.startswith("data:") and "," in value else value
    if len(raw) > (max_bytes * 4) // 3 + 16:
        raise HTTPException(413, "Image is larger than 10 MB.")
    try:
        return base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(400, "Attached image data is not valid.") from exc


_AUDIO_SIGNATURES = (
    (b"\x1a\x45\xdf\xa3", "webm"),
    (b"OggS", "ogg"),
    (b"fLaC", "flac"),
    (b"ID3", "mp3"),
    (b"\xff\xfb", "mp3"),
    (b"\xff\xf3", "mp3"),
    (b"\xff\xf1", "aac"),
    (b"\xff\xf9", "aac"),
)


def sniff_audio(data: bytes) -> str | None:
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE":
        return "wav"
    if len(data) >= 12 and data[4:8] == b"ftyp":
        return "mp4"
    for sig, kind in _AUDIO_SIGNATURES:
        if data.startswith(sig):
            return kind
    return None


def check_audio(data: bytes) -> str:
    if not data:
        raise HTTPException(400, "The recording is empty.")
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(413, "Recording is too long. Please keep it under one minute.")
    kind = sniff_audio(data)
    if not kind:
        raise HTTPException(415, "Unsupported audio format.")
    return kind

"""Copied from backend/app/core/text.py (clean_user_text, has_kannada)."""
from __future__ import annotations

import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_user_text(text: str | None, limit: int = 1000) -> str:
    """Strip control chars and characters used to break out of prompt fences; trim length."""
    if not text:
        return ""
    text = _CONTROL.sub(" ", text)
    text = re.sub(r"[<>{}\[\]\\`]", " ", text)
    text = re.sub(r"\s{3,}", "  ", text)
    return text[:limit].strip()


def has_kannada(text: str) -> bool:
    return bool(re.search(r"[ಀ-೿]", text or ""))

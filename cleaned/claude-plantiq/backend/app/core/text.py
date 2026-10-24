"""Text hygiene for prompts and LLM output."""
from __future__ import annotations

import re

_SECRET_PATTERNS = [
    (re.compile(r"\bgsk_[A-Za-z0-9]{20,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"\bAQ\.[0-9A-Za-z_\-]{30,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}\b"), "[REDACTED_API_KEY]"),
    (re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\b"), "[REDACTED_TOKEN]"),
    (re.compile(r"\b[a-f0-9]{64}\b"), "[REDACTED_TOKEN]"),
]
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def redact_secrets(text: str) -> str:
    if not text:
        return ""
    for pattern, repl in _SECRET_PATTERNS:
        text = pattern.sub(repl, text)
    return text


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

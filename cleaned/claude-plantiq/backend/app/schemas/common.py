from __future__ import annotations

import html
import re

_PHONE_RE = re.compile(r"\d{10}")


def normalize_phone(value: object) -> str:
    """Exactly 10 digits; strips spaces, dashes and a leading +91 / 91 / 0."""
    digits = re.sub(r"\D", "", str(value or ""))
    if len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    if not _PHONE_RE.fullmatch(digits):
        raise ValueError("Phone number must have exactly 10 digits (e.g. 9876543210).")
    return digits


def clean_text_field(value: object, *, min_len: int, max_len: int, label: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    # Angle brackets are never needed in names/addresses; dropping them neutralises HTML injection while
    # keeping text display-correct (no "&amp;" artefacts). The React UI escapes output as well.
    text = re.sub(r"[\x00-\x1f\x7f<>]", "", text)
    if len(text) < min_len:
        raise ValueError(f"{label} must be at least {min_len} characters.")
    if len(text) > max_len:
        raise ValueError(f"{label} must be at most {max_len} characters.")
    return text


def escape(value: str) -> str:
    """HTML-escape for defence in depth (the React UI escapes again)."""
    return html.escape(value, quote=True)

"""LLM + cloud speech providers over REST: Gemini first, Groq second, offline last (same order as the original).

Using httpx directly (no vendor SDKs) gives uniform timeouts/retries and simple mocking in tests.
"""
from __future__ import annotations

import base64
import json
import logging
import time
from dataclasses import dataclass

import httpx

from app.core.config import settings
from app.core.text import redact_secrets

log = logging.getLogger("plantiq.llm")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_STT_URL = "https://api.groq.com/openai/v1/audio/transcriptions"


@dataclass
class LLMResult:
    text: str
    provider: str
    model: str


class LLMClient:
    def __init__(self, timeout: float | None = None, transport: httpx.BaseTransport | None = None) -> None:
        self.timeout = timeout or settings.LLM_TIMEOUT_S
        self._http = httpx.Client(timeout=httpx.Timeout(self.timeout, connect=8.0), transport=transport)

    # ------------------------------------------------------------------ info
    def providers(self) -> list[str]:
        out = []
        if settings.GEMINI_API_KEY:
            out.append("gemini")
        if settings.GROQ_API_KEY:
            out.append("groq")
        return out

    @property
    def available(self) -> bool:
        return bool(self.providers())

    # ------------------------------------------------------------------ http
    def _post(self, url: str, *, headers: dict, json_body: dict | None = None, files=None, data=None) -> dict:
        last_exc: Exception | None = None
        for attempt in range(2):
            try:
                resp = self._http.post(url, headers=headers, json=json_body, files=files, data=data)
                if resp.status_code in (429, 500, 502, 503, 504) and attempt == 0:
                    time.sleep(0.8)
                    continue
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPError, json.JSONDecodeError) as exc:
                last_exc = exc
                if attempt == 0 and not isinstance(exc, httpx.HTTPStatusError):
                    time.sleep(0.5)
                    continue
                break
        raise last_exc or RuntimeError("request failed")

    # ------------------------------------------------------------------ text
    def _gemini(self, system: str, prompt: str, temperature: float, max_tokens: int, json_mode: bool) -> str:
        body: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"
        data = self._post(GEMINI_URL.format(model=settings.GEMINI_MODEL),
                          headers={"x-goog-api-key": settings.GEMINI_API_KEY}, json_body=body)
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()

    def _groq(self, system: str, prompt: str, temperature: float, max_tokens: int, json_mode: bool) -> str:
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body: dict = {"model": settings.GROQ_MODEL, "messages": messages, "temperature": temperature,
                      "max_completion_tokens": max_tokens + 1200}  # gpt-oss spends tokens on reasoning first
        if "gpt-oss" in settings.GROQ_MODEL:
            body["reasoning_effort"] = "low"
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        data = self._post(GROQ_CHAT_URL, headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}, json_body=body)
        return ((data.get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()

    def generate(self, prompt: str, *, system: str = "", temperature: float = 0.2, max_tokens: int = 900,
                 json_mode: bool = False) -> LLMResult | None:
        chain = []
        if settings.GEMINI_API_KEY:
            chain.append(("gemini", settings.GEMINI_MODEL, self._gemini))
        if settings.GROQ_API_KEY:
            chain.append(("groq", settings.GROQ_MODEL, self._groq))
        for name, model, fn in chain:
            t0 = time.perf_counter()
            try:
                text = fn(system, prompt, temperature, max_tokens, json_mode)
                if text:
                    log.info("LLM %s/%s answered in %.1fs (%d chars)", name, model, time.perf_counter() - t0, len(text))
                    return LLMResult(redact_secrets(text), name, model)
                log.warning("LLM %s returned empty text", name)
            except Exception as exc:
                log.warning("LLM %s failed: %s", name, _safe_err(exc))
        return None

    # ------------------------------------------------------------------ speech
    def transcribe_groq(self, audio: bytes, filename: str, lang: str) -> str:
        files = {"file": (filename, audio)}
        data = {"model": "whisper-large-v3", "language": lang, "response_format": "json"}
        out = self._post(GROQ_STT_URL, headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"}, files=files, data=data)
        return (out.get("text") or "").strip()

    def transcribe_gemini(self, audio: bytes, mime: str, lang: str) -> str:
        instruction = (
            "Transcribe this farmer's speech into NATIVE KANNADA SCRIPT (ಕನ್ನಡ ಲಿಪಿ). Even if spoken as Kanglish, output "
            "Kannada script. Return ONLY the transcription."
            if lang == "kn" else
            "Transcribe this farmer's speech (Indian English accent) into English. Return ONLY the transcription."
        )
        body = {"contents": [{"role": "user", "parts": [
            {"text": instruction},
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}},
        ]}], "generationConfig": {"temperature": 0.0}}
        data = self._post(GEMINI_URL.format(model=settings.GEMINI_MODEL),
                          headers={"x-goog-api-key": settings.GEMINI_API_KEY}, json_body=body)
        parts = (data.get("candidates") or [{}])[0].get("content", {}).get("parts", [])
        return "".join(p.get("text", "") for p in parts).strip()


def _safe_err(exc: Exception) -> str:
    if isinstance(exc, httpx.HTTPStatusError):
        return f"HTTP {exc.response.status_code}"
    return redact_secrets(f"{exc.__class__.__name__}: {exc}")[:200]

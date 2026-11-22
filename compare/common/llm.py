"""Minimal LLM client for the RAG benchmark: Gemini and Groq over REST (OpenAI optional), with a disk cache.

Models are named "provider:model", e.g. "gemini:gemini-3.5-flash-lite", "groq:llama-3.1-8b-instant".
Keys come from compare/.env (GEMINI_API_KEY, GROQ_API_KEY). Every response is cached on disk (keyed by provider,
model, prompt and settings) together with the latency of the original call, so an interrupted notebook resumes
for free (important on free-tier quotas) and latency numbers stay the real first-call values.

Roles (override any of them in .env with <ROLE>_MODEL=provider:model):
    GENERATOR     PlantIQ's own LLM (generates the advice and routes Kannada questions)
    BASELINE_LLM  LLM of the Selva Kumar et al. baseline; by default the SAME model as GENERATOR, because the
                  benchmark compares RAG pipelines, not language models
    JUDGE         drafts/validates the question set and scores every answer (a different, stronger model)

provider "fake" returns deterministic text without any network call (used only in smoke mode).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from dataclasses import dataclass

from . import config

CACHE_DIR = (config.ROOT / "_smoke" / "llm_cache") if config.SMOKE else (config.RAG_DIR / "llm_cache")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_LIST = "https://generativelanguage.googleapis.com/v1beta/models?pageSize=200"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_LIST = "https://api.groq.com/openai/v1/models"

DEFAULTS = {
    "GENERATOR": "gemini:gemini-3.5-flash-lite",
    # The benchmark tests the RAG pipelines, not the LLMs: by default the baseline uses the SAME model as PlantIQ,
    # so differences come from retrieval, prompting and grounding only. Set BASELINE_LLM_MODEL to override.
    "BASELINE_LLM": "SAME_AS_GENERATOR",
    "JUDGE": "gemini:gemini-3.5-flash",
}
FALLBACK = {  # used when the provider of the configured model has no key
    "GENERATOR": "gemini:gemini-3.5-flash-lite",
    "BASELINE_LLM": "SAME_AS_GENERATOR",
    "JUDGE": "gemini:gemini-3.5-flash",
}


class QuotaExhausted(RuntimeError):
    """Daily free-tier quota used up: re-run the notebook later, cached answers are kept."""


def load_env() -> None:
    from dotenv import load_dotenv

    load_dotenv(config.ROOT / ".env", override=False)


def has_key(provider: str) -> bool:
    load_env()
    return provider == "fake" or bool(os.getenv(f"{provider.upper()}_API_KEY", "").strip())


def role_model(role: str, verbose: bool = False) -> str:
    """The model for a role: .env override, else default; falls back if that provider has no key."""
    load_env()
    if config.SMOKE:
        return "fake:fake"
    spec = (os.getenv(f"{role}_MODEL") or DEFAULTS[role]).strip()
    if spec == "SAME_AS_GENERATOR":
        return role_model("GENERATOR", verbose)
    if not has_key(spec.split(":", 1)[0]):
        alt = FALLBACK[role]
        if alt == "SAME_AS_GENERATOR":
            alt = role_model("GENERATOR", verbose)
        if verbose:
            print(f"[{role}] no key for {spec.split(':')[0]} -> using {alt}")
        spec = alt
    return spec


@dataclass
class LLMResult:
    text: str
    latency_s: float
    model: str
    cached: bool


class LLM:
    def __init__(self, spec: str, rpm: float | None = None):
        load_env()
        self.spec = spec
        self.provider, self.model = spec.split(":", 1)
        default_rpm = {"gemini": "10", "groq": "25"}.get(self.provider, "0")
        self.rpm = rpm if rpm is not None else float(os.getenv(f"{self.provider.upper()}_RPM", default_rpm) or 0)
        self._last = 0.0
        self._lock = threading.Lock()
        if self.provider not in ("gemini", "groq", "openai", "fake"):
            raise ValueError(f"unknown provider in {spec}")
        if not has_key(self.provider):
            raise RuntimeError(f"{self.provider.upper()}_API_KEY is empty in compare/.env (needed for {spec})")
        CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _key(self) -> str:
        return os.getenv(f"{self.provider.upper()}_API_KEY", "").strip()

    # ---------------------------------------------------------------- public
    def generate(self, prompt: str, system: str = "", temperature: float = 0.2, max_tokens: int = 900,
                 json_mode: bool = False) -> LLMResult:
        key = hashlib.sha256(json.dumps([self.spec, system, prompt, temperature, max_tokens, json_mode],
                                        ensure_ascii=False).encode()).hexdigest()
        path = CACHE_DIR / key[:2] / f"{key}.json"
        if path.exists():
            d = json.loads(path.read_text(encoding="utf-8"))
            return LLMResult(d["text"], d["latency_s"], self.spec, True)
        self._throttle()
        t0 = time.perf_counter()
        text = self._call(system, prompt, temperature, max_tokens, json_mode)
        latency = time.perf_counter() - t0
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"spec": self.spec, "text": text, "latency_s": latency}, ensure_ascii=False),
                        encoding="utf-8")
        return LLMResult(text, latency, self.spec, False)

    def generate_json(self, prompt: str, system: str = "", temperature: float = 0.0, max_tokens: int = 1500):
        res = self.generate(prompt, system, temperature, max_tokens, json_mode=True)
        return parse_json(res.text), res

    def ping(self) -> str:
        """One tiny uncached call; returns '' if it works, else a readable error message."""
        if self.provider == "fake":
            return ""
        try:
            self._call("", "Reply with the single word OK.", 0.0, 50, False)
            return ""
        except Exception as exc:  # noqa: BLE001 - shown to the user
            return str(exc)[:400]

    # ---------------------------------------------------------------- internals
    def _throttle(self):
        if not self.rpm:
            return
        with self._lock:
            wait = 60.0 / self.rpm - (time.time() - self._last)
            if wait > 0:
                time.sleep(wait)
            self._last = time.time()

    def _call(self, system, prompt, temperature, max_tokens, json_mode) -> str:
        if self.provider == "fake":
            return _fake(prompt, json_mode)
        import httpx

        last = None
        for attempt in range(8):
            try:
                if self.provider == "gemini":
                    return self._gemini(httpx, system, prompt, temperature, max_tokens, json_mode)
                return self._openai_like(httpx, system, prompt, temperature, max_tokens, json_mode)
            except httpx.HTTPStatusError as exc:
                last = exc
                code, body = exc.response.status_code, exc.response.text
                if code == 429 and re.search(r"per ?day|PerDay|daily|RPD|TPD", body, re.I):
                    raise QuotaExhausted(f"{self.spec}: daily free-tier quota used up. Run this notebook again "
                                         f"later (tomorrow); everything answered so far is cached.") from None
                if code in (429, 500, 502, 503, 504):
                    time.sleep(min(90, 6 * 2 ** attempt))
                    continue
                raise RuntimeError(f"{self.spec}: HTTP {code}: {body[:300]}") from None
            except (httpx.TransportError, EmptyAnswer) as exc:
                last = exc
                time.sleep(min(60, 3 * 2 ** attempt))
        raise RuntimeError(f"{self.spec}: giving up after retries: {last}")

    def _gemini(self, httpx, system, prompt, temperature, max_tokens, json_mode) -> str:
        gen = {"temperature": temperature, "maxOutputTokens": max(2048, max_tokens * 2)}
        # Thinking tokens count against the output budget and can truncate answers. Gemini 2.5 turns thinking off
        # with thinkingBudget=0; Gemini 3.x rejects that ("invalid argument") and uses thinkingLevel instead.
        if re.match(r"gemini-2\.5", self.model):
            gen["thinkingConfig"] = {"thinkingBudget": 0}
        elif re.match(r"gemini-3", self.model) or "latest" in self.model:
            gen["thinkingConfig"] = {"thinkingLevel": "minimal"}
        if json_mode:
            gen["responseMimeType"] = "application/json"
        body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": gen}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        r = httpx.post(GEMINI_URL.format(model=self.model), headers={"x-goog-api-key": self._key()}, json=body,
                       timeout=180)
        r.raise_for_status()
        cand = (r.json().get("candidates") or [{}])[0]
        text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []) if not p.get("thought"))
        if not text.strip():
            raise EmptyAnswer(f"empty Gemini answer (finishReason={cand.get('finishReason')})")
        return text.strip()

    def _openai_like(self, httpx, system, prompt, temperature, max_tokens, json_mode) -> str:
        url = GROQ_URL if self.provider == "groq" else OPENAI_URL
        messages = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
        body = {"model": self.model, "messages": messages, "temperature": temperature}
        if "gpt-oss" in self.model:          # reasoning models spend tokens on reasoning first
            body["reasoning_effort"] = "low"
            body["max_completion_tokens"] = max_tokens + 1200
        else:
            body["max_tokens"] = max_tokens
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        r = httpx.post(url, headers={"Authorization": f"Bearer {self._key()}"}, json=body, timeout=180)
        r.raise_for_status()
        text = ((r.json().get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()
        if not text:
            raise EmptyAnswer("empty answer")
        return text


class EmptyAnswer(RuntimeError):
    pass


def available_models(provider: str) -> list[str]:
    """Model names this key can use (for the preflight check's error messages)."""
    import httpx

    load_env()
    key = os.getenv(f"{provider.upper()}_API_KEY", "").strip()
    try:
        if provider == "gemini":
            r = httpx.get(GEMINI_LIST, headers={"x-goog-api-key": key}, timeout=30)
            return sorted(m["name"].split("/")[1] for m in r.json().get("models", [])
                          if "generateContent" in m.get("supportedGenerationMethods", []))
        if provider == "groq":
            r = httpx.get(GROQ_LIST, headers={"Authorization": f"Bearer {key}"}, timeout=30)
            return sorted(m["id"] for m in r.json().get("data", []))
    except Exception:  # noqa: BLE001
        pass
    return []


def parse_json(text: str):
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\}|\[.*\])", t, re.S)
        if m:
            return json.loads(m.group(1))
        raise


def _fake(prompt: str, json_mode: bool) -> str:
    """Deterministic stand-in used only by smoke runs: shaped like each prompt's expected JSON."""
    h = int(hashlib.md5(prompt.encode("utf-8")).hexdigest(), 16)
    if not json_mode:
        return "Spray 0.5% Bordeaux mixture before monsoon. Remove infected leaves. Source: guide."
    if "<passage>" in prompt and '"questions"' in prompt:
        quote = re.search(r"<passage>\s*(.{20,160}?[.!?])", prompt, re.S)
        q = (quote.group(1) if quote else "coffee leaf rust is a fungal disease.").strip()
        return json.dumps({"questions": [{"question": f"What does the guide say ({h % 97})?",
                                          "answer": q, "evidence": [q]}]})
    if '"grower_relevance"' in prompt:
        return json.dumps({"answerable": 1, "grower_relevance": 1 + h % 5, "clear": 1,
                           "kannada": "ಕಾಫಿ ಎಲೆ ತುಕ್ಕು ರೋಗವನ್ನು ಹೇಗೆ ನಿಯಂತ್ರಿಸುವುದು?"})
    if '"context_verdicts"' in prompt:
        n = prompt.count("<chunk ")
        return json.dumps({"claims": [{"text": "Spray Bordeaux mixture.", "supported": h % 2},
                                      {"text": "Remove leaves.", "supported": 1}],
                           "generated_questions": ["How to control coffee leaf rust?"] * 3, "noncommittal": 0,
                           "context_verdicts": [int((h >> i) & 1) for i in range(n)],
                           "tp": ["Spray Bordeaux mixture."], "fp": ["Remove leaves."], "fn": [], "abstained": h % 2})
    if "search_query_english" in prompt:
        return json.dumps({"detected_script": "kannada_script", "search_query_english": "coffee leaf rust control",
                           "is_greeting_or_location_only": False, "target_response_language": "kn"})
    return json.dumps({})

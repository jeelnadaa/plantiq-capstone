"""Lazy service singletons with a fake-ML switch and test overrides.

    get_cnn(), get_rag(), get_llm(), get_env(), get_stt()

With PLANTIQ_FAKE_ML=1 the CNN/RAG/LLM/STT are deterministic fakes (fast tests, UI E2E).
Tests can also call `override("llm", obj)` and `reset()`.
"""
from __future__ import annotations

import logging
import threading
from typing import Any, Callable

from app.core.config import settings

log = logging.getLogger("plantiq.registry")
_instances: dict[str, Any] = {}
_overrides: dict[str, Any] = {}
_lock = threading.Lock()


def _get(name: str, real: Callable[[], Any], fake: Callable[[], Any]) -> Any:
    if name in _overrides:
        return _overrides[name]
    inst = _instances.get(name)
    if inst is not None:
        return inst
    with _lock:
        inst = _instances.get(name)
        if inst is None:
            inst = fake() if settings.FAKE_ML and name != "env" else real()
            _instances[name] = inst
    return inst


def override(name: str, obj: Any) -> None:
    _overrides[name] = obj


def reset() -> None:
    _overrides.clear()
    _instances.clear()


def loaded(name: str) -> bool:
    return name in _instances or name in _overrides


def get_cnn():
    from app.services import fakes
    from app.services.cnn import CNNClassifier

    return _get("cnn", CNNClassifier, fakes.FakeCNN)


def get_rag():
    from app.services import fakes
    from app.services.rag.retriever import HybridRetriever

    return _get("rag", HybridRetriever.load_or_build, fakes.FakeRetriever)


def get_llm():
    from app.services import fakes
    from app.services.llm import LLMClient

    return _get("llm", LLMClient, fakes.FakeLLM)


def get_stt():
    from app.services import fakes
    from app.services.voice import SpeechToText

    return _get("stt", SpeechToText, fakes.FakeSTT)


def get_env():
    from app.services.environment import EnvironmentService

    return _get("env", EnvironmentService, EnvironmentService)

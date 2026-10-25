"""Readable terminal progress for the diagnosis / chat / voice pipelines (port of the original terminal_logger)."""
from __future__ import annotations

import logging
import sys
import time
from contextlib import contextmanager

if sys.platform == "win32":
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except Exception:
            pass

log = logging.getLogger("plantiq.pipeline")

_C = {"g": "\033[32m", "c": "\033[36m", "y": "\033[33m", "r": "\033[31m", "b": "\033[1m", "d": "\033[2m", "x": "\033[0m"}
_color = sys.stdout.isatty()


def _fmt(color: str, text: str) -> str:
    return f"{_C[color]}{text}{_C['x']}" if _color else text


class Pipeline:
    """Usage:
        with Pipeline("Leaf diagnosis", user=3) as p:
            with p.step("CNN inference"): ...
            p.note("cache miss")
    """

    def __init__(self, name: str, **context) -> None:
        self.name = name
        self.context = context
        self.t0 = 0.0
        self.n = 0

    def __enter__(self) -> "Pipeline":
        self.t0 = time.perf_counter()
        ctx = " ".join(f"{k}={v}" for k, v in self.context.items() if v is not None)
        log.info(_fmt("b", f"▶ {self.name}") + (f" {_fmt('d', ctx)}" if ctx else ""))
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        ms = (time.perf_counter() - self.t0) * 1000
        if exc_type:
            log.warning(_fmt("r", f"✖ {self.name} failed after {ms:.0f} ms: {exc_type.__name__}"))
        else:
            log.info(_fmt("g", f"✔ {self.name} done in {ms:.0f} ms"))

    @contextmanager
    def step(self, label: str):
        self.n += 1
        t = time.perf_counter()
        try:
            yield
        finally:
            log.info(f"  {_fmt('c', str(self.n))}. {label} {_fmt('d', f'({(time.perf_counter() - t) * 1000:.0f} ms)')}")

    def note(self, text: str) -> None:
        log.info(f"     {_fmt('d', text)}")

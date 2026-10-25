from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Citation(BaseModel):
    source: str
    title: str | None = None
    page: int | None = None
    section: str | None = None
    score: float | None = None


class DiagnosisOut(BaseModel):
    scan_id: int | None = None
    cache_hit: bool
    sha256_hash: str
    filename: str | None = None
    image_url: str | None = None
    disease: str
    disease_display: str
    disease_display_kn: str
    latin_name: str | None = None
    kind: str
    confidence: float
    is_healthy: bool
    distribution: dict[str, float]
    env_data: dict | None = None
    advisory: str
    sources: list[str] = []
    citations: list[Citation] = []
    is_blended: bool = False
    reasons: list[str] = []
    safety_audit: dict | None = None
    provider: str | None = None
    language: str = "en"
    created_at: datetime | None = None


class ScanOut(BaseModel):
    id: int
    disease: str
    disease_display: str
    disease_display_kn: str
    confidence: float
    is_healthy: bool
    is_blended: bool
    image_url: str | None
    distribution: dict[str, float]
    env_data: dict | None
    advisory: str
    sources: list[str] | None
    citations: list[dict] | None
    safety_audit: dict | None
    reasons: list[str] | None
    question: str | None
    language: str
    latitude: float | None
    longitude: float | None
    created_at: datetime


class ScanIdsIn(BaseModel):
    ids: list[int] = Field(default_factory=list, max_length=500)

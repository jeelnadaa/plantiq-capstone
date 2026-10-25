"""Application settings, read from environment variables (and backend/.env)."""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=False)
# transformers 5.x loads .bin checkpoints (bge-m3, bge-reranker-v2-m3 ship no safetensors) with a thread pool
# that intermittently segfaults on Windows. Sequential loading is stable and only a few seconds slower.
os.environ.setdefault("HF_DEACTIVATE_ASYNC_LOAD", "1")

_DEFAULT_SECRET_SENTINEL = "change-me"
_TRUE = {"1", "true", "yes", "on", "t", "y"}


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in _TRUE


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _list(name: str, default: str) -> list[str]:
    return [p.strip() for p in os.getenv(name, default).split(",") if p.strip()]


@dataclass
class Settings:
    PROJECT_NAME: str = "PlantIQ API"
    VERSION: str = "3.0.0"
    ENV: str = field(default_factory=lambda: os.getenv("ENV", "development").lower())
    DEBUG: bool = field(default_factory=lambda: _bool("DEBUG", False))

    # --- paths ---
    DATA_DIR: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", str(BACKEND_DIR / "data"))))
    VAR_DIR: Path = field(default_factory=lambda: Path(os.getenv("VAR_DIR", str(BACKEND_DIR / "var"))))
    STATIC_DIR: Path = field(default_factory=lambda: Path(os.getenv("STATIC_DIR", str(BACKEND_DIR / "static"))))

    # --- database ---
    DATABASE_URL: str = ""
    DB_FALLBACK_TO_SQLITE: bool = field(default_factory=lambda: _bool("DB_FALLBACK_TO_SQLITE", True))

    # --- security ---
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY", _DEFAULT_SECRET_SENTINEL))
    JWT_ISSUER: str = "plantiq"
    JWT_AUDIENCE: str = "plantiq-app"
    ACCESS_TOKEN_MINUTES: int = field(default_factory=lambda: _int("ACCESS_TOKEN_MINUTES", 15))
    REFRESH_TOKEN_DAYS: int = field(default_factory=lambda: _int("REFRESH_TOKEN_DAYS", 30))
    REFRESH_TOKEN_SHORT_HOURS: int = field(default_factory=lambda: _int("REFRESH_TOKEN_SHORT_HOURS", 24))
    LOGIN_MAX_FAILURES: int = field(default_factory=lambda: _int("LOGIN_MAX_FAILURES", 5))
    LOGIN_LOCK_MINUTES: int = field(default_factory=lambda: _int("LOGIN_LOCK_MINUTES", 15))
    RATE_LIMIT_ENABLED: bool = field(default_factory=lambda: _bool("RATE_LIMIT_ENABLED", True))
    RATE_LIMIT_AUTH_PER_MIN: int = field(default_factory=lambda: _int("RATE_LIMIT_AUTH_PER_MIN", 20))
    RATE_LIMIT_HEAVY_PER_MIN: int = field(default_factory=lambda: _int("RATE_LIMIT_HEAVY_PER_MIN", 30))
    RATE_LIMIT_DEFAULT_PER_MIN: int = field(default_factory=lambda: _int("RATE_LIMIT_DEFAULT_PER_MIN", 240))
    MAX_BODY_BYTES: int = field(default_factory=lambda: _int("MAX_BODY_BYTES", 15 * 1024 * 1024))
    CORS_ORIGINS: list[str] = field(default_factory=lambda: _list(
        "CORS_ORIGINS",
        "http://localhost,https://localhost,capacitor://localhost,http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:8000,http://127.0.0.1:8000",
    ))
    TRUST_PROXY_HEADERS: bool = field(default_factory=lambda: _bool("TRUST_PROXY_HEADERS", False))

    # --- marketplace ---
    MAX_LISTINGS_PER_USER: int = field(default_factory=lambda: _int("MAX_LISTINGS_PER_USER", 50))
    MAX_PHOTOS_PER_LISTING: int = field(default_factory=lambda: _int("MAX_PHOTOS_PER_LISTING", 8))

    # --- ML: CNN ---
    CNN_WEIGHTS_PATH: Path = field(default_factory=lambda: Path(os.getenv(
        "CNN_WEIGHTS_PATH", str(BACKEND_DIR / "data" / "models" / "best_resnet50_coffee.pth"))))
    CONFIDENCE_THRESHOLD_CNN: float = field(default_factory=lambda: _float("CONFIDENCE_THRESHOLD_CNN", 75.0))
    CONFIDENCE_THRESHOLD_RAG: float = field(default_factory=lambda: _float("CONFIDENCE_THRESHOLD_RAG", 0.60))
    ML_DEVICE: str = field(default_factory=lambda: os.getenv("ML_DEVICE", "auto").lower())
    FAKE_ML: bool = field(default_factory=lambda: _bool("PLANTIQ_FAKE_ML", False))

    # --- ML: RAG ---
    RAG_PROFILE: str = field(default_factory=lambda: os.getenv("RAG_PROFILE", "auto").lower())
    RAG_DOCS_DIR: Path = field(default_factory=lambda: Path(os.getenv(
        "RAG_DOCS_DIR", str(BACKEND_DIR / "data" / "knowledge_base"))))
    RAG_INDEX_DIR: Path = field(default_factory=lambda: Path(os.getenv(
        "RAG_INDEX_DIR", str(BACKEND_DIR / "data" / "index"))))
    RAG_AUTO_BUILD: bool = field(default_factory=lambda: _bool("RAG_AUTO_BUILD", True))

    # --- LLM providers ---
    GEMINI_API_KEY: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    GEMINI_MODEL: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    GROQ_API_KEY: str = field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    GROQ_MODEL: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"))
    LLM_TIMEOUT_S: float = field(default_factory=lambda: _float("LLM_TIMEOUT_S", 45.0))
    HF_TOKEN: str = field(default_factory=lambda: os.getenv("HF_TOKEN", ""))

    # --- speech to text ---
    ENABLE_LOCAL_STT: bool = field(default_factory=lambda: _bool("ENABLE_LOCAL_STT", _bool("USE_LOCAL_STT", True)))
    ENABLE_LOCAL_KANNADA_STT: bool = field(default_factory=lambda: _bool("ENABLE_LOCAL_KANNADA_STT", True))
    ENABLE_LOCAL_ENGLISH_STT: bool = field(default_factory=lambda: _bool("ENABLE_LOCAL_ENGLISH_STT", True))
    INDIC_CONFORMER_MODEL_ID: str = field(default_factory=lambda: os.getenv(
        "INDIC_CONFORMER_MODEL_ID", "ai4bharat/indic-conformer-600m-multilingual"))
    INDIC_CONFORMER_DECODER: str = field(default_factory=lambda: os.getenv("INDIC_CONFORMER_DECODER", "ctc"))
    ENGLISH_STT_MODEL_ID: str = field(default_factory=lambda: os.getenv(
        "ENGLISH_STT_MODEL_ID", "bryandts/whisper-base-en-india-accent-svarah"))

    # --- weather ---
    OPEN_METEO_URL: str = field(default_factory=lambda: os.getenv(
        "OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast"))
    WEATHER_TIMEOUT_S: float = field(default_factory=lambda: _float("WEATHER_TIMEOUT_S", 6.0))

    API_PREFIX: str = "/api/v1"

    def __post_init__(self) -> None:
        self.DATABASE_URL = self._resolve_database_url()
        if self.SECRET_KEY in ("", _DEFAULT_SECRET_SENTINEL) or len(self.SECRET_KEY) < 32:
            if self.is_production:
                raise RuntimeError("SECRET_KEY must be set to a random value of at least 32 characters in production.")
            # Development: a per-process random key (tokens die on restart, which is safe).
            self.SECRET_KEY = os.getenv("PLANTIQ_DEV_SECRET") or secrets.token_urlsafe(48)
        if self.is_production and "*" in self.CORS_ORIGINS:
            raise RuntimeError("CORS_ORIGINS='*' is not allowed in production.")

    @property
    def is_production(self) -> bool:
        return self.ENV in ("production", "prod")

    @property
    def is_local_kannada_stt_enabled(self) -> bool:
        return self.ENABLE_LOCAL_STT and self.ENABLE_LOCAL_KANNADA_STT

    @property
    def is_local_english_stt_enabled(self) -> bool:
        return self.ENABLE_LOCAL_STT and self.ENABLE_LOCAL_ENGLISH_STT

    @property
    def media_dir(self) -> Path:
        return self.VAR_DIR / "media"

    @property
    def sqlite_path(self) -> Path:
        return self.VAR_DIR / "plantiq.db"

    def _resolve_database_url(self) -> str:
        explicit = os.getenv("DATABASE_URL", "").strip()
        if explicit:
            return explicit
        pg_password = os.getenv("POSTGRES_PASSWORD", "")
        pg_host = os.getenv("POSTGRES_HOST", "")
        if pg_host:
            user = os.getenv("POSTGRES_USER", "postgres")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "plantiq_app")
            auth = f"{user}:{quote_plus(pg_password)}" if pg_password else user
            return f"postgresql+psycopg2://{auth}@{pg_host}:{port}/{db}"
        return f"sqlite:///{(self.VAR_DIR / 'plantiq.db').as_posix()}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

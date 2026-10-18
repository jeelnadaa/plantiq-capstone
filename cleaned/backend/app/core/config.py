import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load .env
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR.parent / "backend" / ".env")

class Settings:
    PROJECT_NAME: str = "PlantIQ Cleaned API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api"
    
    # Thresholds
    CONFIDENCE_THRESHOLD_CNN: float = float(os.getenv("CONFIDENCE_THRESHOLD_CNN", "75.0"))
    CONFIDENCE_THRESHOLD_RAG: float = float(os.getenv("CONFIDENCE_THRESHOLD_RAG", "0.60"))
    
    # Model & RAG Paths
    CNN_WEIGHTS_PATH: str = os.getenv("CNN_WEIGHTS_PATH", str(ROOT_DIR / "app" / "services" / "best_resnet50_coffee.pth"))
    RAG_INDEX_DIR: str = os.getenv("RAG_INDEX_DIR", str(ROOT_DIR / "app" / "services" / "index"))
    RAG_DOCS_DIR: str = os.getenv("RAG_DOCS_DIR", str(ROOT_DIR / "app" / "services" / "knowledge_base"))
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    # Speech-to-Text (IndicConformer for Kannada & Svarah Whisper for Indian English)
    INDIC_CONFORMER_MODEL_ID: str = os.getenv("INDIC_CONFORMER_MODEL_ID", "ai4bharat/indic-conformer-600m-multilingual")
    INDIC_CONFORMER_DEVICE: str = os.getenv("INDIC_CONFORMER_DEVICE", "auto")  # 'auto', 'cuda', 'cpu'
    INDIC_CONFORMER_DECODER: str = os.getenv("INDIC_CONFORMER_DECODER", "ctc")  # 'ctc' or 'rnnt'
    ENGLISH_STT_MODEL_ID: str = os.getenv("ENGLISH_STT_MODEL_ID", "bryandts/whisper-base-en-india-accent-svarah")
    
    # Master local STT switch (can be toggled in .env via ENABLE_LOCAL_STT=false)
    ENABLE_LOCAL_STT: bool = os.getenv("ENABLE_LOCAL_STT", os.getenv("USE_LOCAL_STT", "true")).lower() in ("true", "1", "yes", "on", "t")

    # Granular local STT switches (can be toggled separately in .env)
    ENABLE_LOCAL_KANNADA_STT: bool = os.getenv("ENABLE_LOCAL_KANNADA_STT", os.getenv("USE_LOCAL_KANNADA_STT", "true")).lower() in ("true", "1", "yes", "on", "t")
    ENABLE_LOCAL_ENGLISH_STT: bool = os.getenv("ENABLE_LOCAL_ENGLISH_STT", os.getenv("USE_LOCAL_ENGLISH_STT", "true")).lower() in ("true", "1", "yes", "on", "t")

    @property
    def is_local_kannada_stt_enabled(self) -> bool:
        """Returns True only when both master local STT and Kannada local STT are enabled."""
        return bool(self.ENABLE_LOCAL_STT and self.ENABLE_LOCAL_KANNADA_STT)

    @property
    def is_local_english_stt_enabled(self) -> bool:
        """Returns True only when both master local STT and English local STT are enabled."""
        return bool(self.ENABLE_LOCAL_STT and self.ENABLE_LOCAL_ENGLISH_STT)

    
    # Security & API Protection
    SECRET_KEY: str = os.getenv("SECRET_KEY", "plantiq-production-secret-key-change-in-env")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    CORS_ORIGINS: list = [
        o.strip() for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:8000,http://127.0.0.1:8000,http://localhost:3000,http://localhost:5173"
        ).split(",") if o.strip()
    ]
    
    # PostgreSQL Database Configuration
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "plantiq")

    def __init__(self):
        # Database URL resolution
        explicit_url = os.getenv("DATABASE_URL")
        if explicit_url:
            self.DATABASE_URL = explicit_url
        else:
            if self.POSTGRES_PASSWORD:
                encoded_pw = quote_plus(self.POSTGRES_PASSWORD)
                self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{encoded_pw}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            else:
                self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()

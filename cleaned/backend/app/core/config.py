import os
from pathlib import Path
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
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "plantiq-production-secret-key-change-in-env")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/plantiq_cleaned.db")

settings = Settings()

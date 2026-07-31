import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR.parent / "rag" / ".env")

class Settings:
    PROJECT_NAME: str = "PlantIQ API"
    VERSION: str = "1.0.0"
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Paths
    BASE_DIR: Path = ROOT_DIR
    CNN_WEIGHTS_PATH: str = os.getenv(
        "CNN_WEIGHTS_PATH", 
        str(ROOT_DIR.parent / "cnn" / "best_resnet50_coffee.pth")
    )
    PDF_FOLDER: str = os.getenv(
        "PDF_FOLDER", 
        str(ROOT_DIR / "knowledge_base" if (ROOT_DIR / "knowledge_base").exists() else ROOT_DIR.parent / "rag" / "knowledge_base")
    )
    INDEX_FOLDER: str = os.getenv(
        "INDEX_FOLDER", 
        str(ROOT_DIR / "index")
    )
    UPLOAD_DIR: Path = ROOT_DIR / "uploads"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR}/plantiq.db")
    
    # Confidence Thresholds
    CONFIDENCE_THRESHOLD_CNN: float = float(os.getenv("CONFIDENCE_THRESHOLD_CNN", "75.0"))
    CONFIDENCE_THRESHOLD_RAG: float = float(os.getenv("CONFIDENCE_THRESHOLD_RAG", "0.60"))

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path(settings.INDEX_FOLDER).mkdir(parents=True, exist_ok=True)

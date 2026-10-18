from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

db_url = settings.DATABASE_URL

# Normalize postgres:// to postgresql:// (for compatibility with hosted providers e.g. Neon, Supabase, Render)
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Configure database engine according to dialect
if db_url.startswith("sqlite"):
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False}
    )
else:
    # Production-grade PostgreSQL configuration with connection pooling and health checks
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Automatically detect and recover dropped or stale connections
        pool_size=10,        # Base pool connection size
        max_overflow=20      # Max burst connections beyond pool_size
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

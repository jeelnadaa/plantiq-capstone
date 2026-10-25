import os
import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, quote_plus
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
SQLITE_FALLBACK_FILE = ROOT_DIR / "plantiq_cleaned.db"
SQLITE_FALLBACK_URL = f"sqlite:///{SQLITE_FALLBACK_FILE}"

Base = declarative_base()

def _parse_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.fromisoformat(val)
    except Exception:
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(val, fmt)
        except Exception:
            pass
    return None

def _parse_json(val):
    if val is None:
        return None
    if isinstance(val, (dict, list)):
        return val
    if isinstance(val, str):
        try:
            return json.loads(val)
        except Exception:
            return val
    return val

def _try_create_postgres_database(pg_url: str) -> bool:
    """Connects to the default PostgreSQL maintenance database to auto-create target database."""
    try:
        parsed = urlparse(pg_url)
        target_db = parsed.path.lstrip("/") or settings.POSTGRES_DB
        host = parsed.hostname or settings.POSTGRES_HOST
        port = parsed.port or settings.POSTGRES_PORT
        user = parsed.username or settings.POSTGRES_USER
        password = parsed.password or settings.POSTGRES_PASSWORD

        pw_part = f":{quote_plus(password)}" if password else ""
        maint_url = f"postgresql://{user}{pw_part}@{host}:{port}/postgres"

        maint_engine = create_engine(maint_url, isolation_level="AUTOCOMMIT")
        with maint_engine.connect() as conn:
            check_sql = text("SELECT 1 FROM pg_database WHERE datname = :dbname")
            exists = conn.execute(check_sql, {"dbname": target_db}).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{target_db}";'))
                print(f"✨ Automatically created missing PostgreSQL database: '{target_db}'")
        maint_engine.dispose()
        return True
    except Exception as e:
        print(f"⚠️ Could not auto-create database '{settings.POSTGRES_DB}': {e}")
        return False

def _auto_migrate_sqlite_to_pg(target_engine, sqlite_path: Path):
    """Auto-seeds empty PostgreSQL database with existing data from SQLite."""
    if not sqlite_path.exists():
        return

    import app.models
    from app.models.user import User, AuthToken
    from app.models.chat import ChatThread, ChatMessage
    from app.models.cache import ImageAnalysisCache
    from app.models.marketplace import CropListing

    sq_conn = sqlite3.connect(str(sqlite_path))
    sq_conn.row_factory = sqlite3.Row
    sq_cursor = sq_conn.cursor()

    Session = sessionmaker(bind=target_engine)
    session = Session()

    try:
        # Users
        sq_cursor.execute("SELECT * FROM users")
        for r in sq_cursor.fetchall():
            if not session.query(User).filter(User.id == r["id"]).first():
                session.add(User(
                    id=r["id"], username=r["username"], email=r["email"],
                    full_name=r["full_name"], hashed_password=r["hashed_password"],
                    created_at=_parse_dt(r["created_at"]) or datetime.utcnow()
                ))
        session.commit()

        # Auth Tokens
        sq_cursor.execute("SELECT * FROM auth_tokens")
        for r in sq_cursor.fetchall():
            if not session.query(AuthToken).filter(AuthToken.id == r["id"]).first():
                session.add(AuthToken(
                    id=r["id"], user_id=r["user_id"], token=r["token"],
                    created_at=_parse_dt(r["created_at"]) or datetime.utcnow()
                ))
        session.commit()

        # Chat Threads
        sq_cursor.execute("SELECT * FROM chat_threads")
        for r in sq_cursor.fetchall():
            if not session.query(ChatThread).filter(ChatThread.id == r["id"]).first():
                session.add(ChatThread(
                    id=r["id"], user_id=r["user_id"], title=r["title"],
                    created_at=_parse_dt(r["created_at"]) or datetime.utcnow()
                ))
        session.commit()

        # Chat Messages
        sq_cursor.execute("SELECT * FROM chat_messages")
        for r in sq_cursor.fetchall():
            if not session.query(ChatMessage).filter(ChatMessage.id == r["id"]).first():
                session.add(ChatMessage(
                    id=r["id"], thread_id=r["thread_id"], role=r["role"],
                    content=r["content"], attached_image_name=r["attached_image_name"],
                    image_data_url=r["image_data_url"],
                    created_at=_parse_dt(r["created_at"]) or datetime.utcnow()
                ))
        session.commit()

        # Cache
        sq_cursor.execute("SELECT * FROM image_analysis_cache")
        for r in sq_cursor.fetchall():
            if not session.query(ImageAnalysisCache).filter(ImageAnalysisCache.id == r["id"]).first():
                session.add(ImageAnalysisCache(
                    id=r["id"], image_hash=r["image_hash"], user_id=r["user_id"],
                    filename=r["filename"], disease_class=r["disease_class"],
                    confidence=r["confidence"], distribution=_parse_json(r["distribution"]),
                    env_data=_parse_json(r["env_data"]), advisory_text=r["advisory_text"],
                    sources=_parse_json(r["sources"]), is_blended=bool(r["is_blended"]),
                    created_at=_parse_dt(r["created_at"]) or datetime.utcnow()
                ))
        session.commit()

        # Marketplace Listings
        sq_cursor.execute("SELECT * FROM crop_listings")
        for r in sq_cursor.fetchall():
            if not session.query(CropListing).filter(CropListing.id == r["id"]).first():
                session.add(CropListing(
                    id=r["id"], user_id=r["user_id"], title=r["title"],
                    variety=r["variety"], quantity_kg=r["quantity_kg"],
                    price_per_kg=r["price_per_kg"], farmer_name=r["farmer_name"],
                    phone_number=r["phone_number"], address=r["address"],
                    latitude=r["latitude"], longitude=r["longitude"],
                    photos=_parse_json(r["photos"]),
                    created_at=_parse_dt(r["created_at"]) or datetime.utcnow()
                ))
        session.commit()

        # Update serial sequence counters
        serial_tables = [
            ("users", "id"), ("auth_tokens", "id"), ("chat_messages", "id"),
            ("image_analysis_cache", "id"), ("crop_listings", "id")
        ]
        with target_engine.connect() as conn:
            for tbl, col in serial_tables:
                try:
                    conn.execute(text(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{tbl}', '{col}'),
                            COALESCE((SELECT MAX({col}) FROM {tbl}), 1)
                        );
                    """))
                    conn.commit()
                except Exception:
                    pass

        print(f"📦 Auto-migrated seed records from {sqlite_path.name} into PostgreSQL successfully.")
    except Exception as ex:
        session.rollback()
        print(f"⚠️ Auto-migration note: {ex}")
    finally:
        session.close()
        sq_conn.close()

def _create_engine_with_fallback(db_url: str):
    """Attempts PostgreSQL connection with auto-creation of missing DB and graceful SQLite fallback."""
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    if db_url.startswith("sqlite"):
        return create_engine(db_url, connect_args={"check_same_thread": False})

    # Attempt PostgreSQL connection
    try:
        pg_engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
        return pg_engine
    except Exception as exc:
        err_msg = str(exc).lower()

        # Case 1: Database does not exist -> auto-create it
        if "does not exist" in err_msg:
            print(f"⚠️ Target PostgreSQL database does not exist. Attempting auto-creation...")
            if _try_create_postgres_database(db_url):
                try:
                    pg_engine = create_engine(
                        db_url,
                        pool_pre_ping=True,
                        pool_size=10,
                        max_overflow=20
                    )
                    with pg_engine.connect() as conn:
                        conn.execute(text("SELECT 1;"))
                    print(f"✅ Successfully connected to newly created database '{settings.POSTGRES_DB}'.")
                    return pg_engine
                except Exception as retry_err:
                    print(f"⚠️ Reconnection to new database failed: {retry_err}")

        # Case 2: PostgreSQL server is completely unreachable or credentials failed -> Fallback to SQLite
        print("\n" + "=" * 65)
        print("⚠️  POSTGRESQL CONNECTION NOTICE:")
        print(f"   Could not connect to PostgreSQL ({exc}).")
        print(f"🔄 FALLBACK: Automatically routing database queries to local SQLite:")
        print(f"   {SQLITE_FALLBACK_FILE}")
        print("💡 The application will run normally without interruption.")
        print("   To switch back to PostgreSQL, check backend/.env and start PostgreSQL.")
        print("=" * 65 + "\n")
        return create_engine(SQLITE_FALLBACK_URL, connect_args={"check_same_thread": False})

# Active database engine and session factory
engine = _create_engine_with_fallback(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

_is_initialized = False

def init_database(force: bool = False):
    """Ensures database schema tables exist and auto-seeds if uninitialized."""
    global _is_initialized, engine
    if _is_initialized and not force:
        return

    import app.models  # Register all SQLAlchemy models

    # Create schema tables
    Base.metadata.create_all(bind=engine)

    # Ensure dynamic unit columns exist on crop_listings table
    try:
        with engine.connect() as conn:
            for col_name, col_type in [
                ("quantity", "FLOAT"),
                ("quantity_unit", "VARCHAR(50) DEFAULT 'kg'"),
                ("price", "FLOAT"),
                ("price_unit", "VARCHAR(80) DEFAULT 'per kg'")
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE crop_listings ADD COLUMN {col_name} {col_type};"))
                    conn.commit()
                except Exception:
                    pass
    except Exception:
        pass

    # If active database is PostgreSQL, check if empty and auto-seed from SQLite
    is_sqlite = str(engine.url).startswith("sqlite")

    if not is_sqlite:
        try:
            with engine.connect() as conn:
                user_count = conn.execute(text("SELECT COUNT(*) FROM users;")).scalar()
            if user_count == 0 and SQLITE_FALLBACK_FILE.exists():
                print(f"🌱 Empty PostgreSQL database detected. Auto-seeding from {SQLITE_FALLBACK_FILE.name}...")
                _auto_migrate_sqlite_to_pg(engine, SQLITE_FALLBACK_FILE)
            print(f"✅ PostgreSQL database verified: '{settings.POSTGRES_DB}'")
        except Exception as seed_err:
            print(f"⚠️ Verification notice: {seed_err}")
    else:
        print(f"✅ SQLite database active: {SQLITE_FALLBACK_FILE.name}")

    _is_initialized = True

def get_db():
    if not _is_initialized:
        init_database()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

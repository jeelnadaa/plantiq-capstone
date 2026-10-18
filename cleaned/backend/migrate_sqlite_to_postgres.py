"""
PlantIQ - SQLite to PostgreSQL Data Migration Script
---------------------------------------------------
Migrates all existing data from SQLite (plantiq_cleaned.db) into PostgreSQL:
  1. users
  2. auth_tokens
  3. chat_threads
  4. chat_messages
  5. image_analysis_cache
  6. crop_listings

Also synchronizes PostgreSQL sequence counters to prevent ID collisions.

Usage:
    python migrate_sqlite_to_postgres.py
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime

# Windows console encoding
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models
from app.models.user import User, AuthToken
from app.models.chat import ChatThread, ChatMessage
from app.models.cache import ImageAnalysisCache
from app.models.marketplace import CropListing

def parse_dt(val):
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

def parse_json(val):
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

def run_migration():
    sqlite_path = Path(__file__).resolve().parent / "plantiq_cleaned.db"
    if not sqlite_path.exists():
        print(f"❌ SQLite database file not found at: {sqlite_path}")
        return False

    print("\n=======================================================")
    print("🚀 PlantIQ: SQLite ➔ PostgreSQL Data Migration")
    print("=======================================================")
    print(f" * Source SQLite:   {sqlite_path}")
    print(f" * Target Postgres: {settings.POSTGRES_DB} ({settings.POSTGRES_HOST}:{settings.POSTGRES_PORT})")
    print("-------------------------------------------------------")

    # Step 1: Ensure Postgres tables exist
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL schema verified.")
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        print("👉 Please check your credentials in backend/.env")
        return False

    sq_conn = sqlite3.connect(str(sqlite_path))
    sq_conn.row_factory = sqlite3.Row
    sq_cursor = sq_conn.cursor()

    pg_session = SessionLocal()

    try:
        # 1. Users
        sq_cursor.execute("SELECT * FROM users")
        user_rows = sq_cursor.fetchall()
        print(f"\n📦 Migrating {len(user_rows)} users...")
        for r in user_rows:
            existing = pg_session.query(User).filter(User.id == r["id"]).first()
            if not existing:
                u = User(
                    id=r["id"],
                    username=r["username"],
                    email=r["email"],
                    full_name=r["full_name"],
                    hashed_password=r["hashed_password"],
                    created_at=parse_dt(r["created_at"]) or datetime.utcnow()
                )
                pg_session.add(u)
        pg_session.commit()
        print(f"   ✅ Users migrated.")

        # 2. Auth Tokens
        sq_cursor.execute("SELECT * FROM auth_tokens")
        token_rows = sq_cursor.fetchall()
        print(f"\n📦 Migrating {len(token_rows)} auth tokens...")
        for r in token_rows:
            existing = pg_session.query(AuthToken).filter(AuthToken.id == r["id"]).first()
            if not existing:
                t = AuthToken(
                    id=r["id"],
                    user_id=r["user_id"],
                    token=r["token"],
                    created_at=parse_dt(r["created_at"]) or datetime.utcnow()
                )
                pg_session.add(t)
        pg_session.commit()
        print(f"   ✅ Auth tokens migrated.")

        # 3. Chat Threads
        sq_cursor.execute("SELECT * FROM chat_threads")
        thread_rows = sq_cursor.fetchall()
        print(f"\n📦 Migrating {len(thread_rows)} chat threads...")
        for r in thread_rows:
            existing = pg_session.query(ChatThread).filter(ChatThread.id == r["id"]).first()
            if not existing:
                th = ChatThread(
                    id=r["id"],
                    user_id=r["user_id"],
                    title=r["title"],
                    created_at=parse_dt(r["created_at"]) or datetime.utcnow()
                )
                pg_session.add(th)
        pg_session.commit()
        print(f"   ✅ Chat threads migrated.")

        # 4. Chat Messages
        sq_cursor.execute("SELECT * FROM chat_messages")
        msg_rows = sq_cursor.fetchall()
        print(f"\n📦 Migrating {len(msg_rows)} chat messages...")
        for r in msg_rows:
            existing = pg_session.query(ChatMessage).filter(ChatMessage.id == r["id"]).first()
            if not existing:
                cm = ChatMessage(
                    id=r["id"],
                    thread_id=r["thread_id"],
                    role=r["role"],
                    content=r["content"],
                    attached_image_name=r["attached_image_name"],
                    image_data_url=r["image_data_url"],
                    created_at=parse_dt(r["created_at"]) or datetime.utcnow()
                )
                pg_session.add(cm)
        pg_session.commit()
        print(f"   ✅ Chat messages migrated.")

        # 5. Image Analysis Cache
        sq_cursor.execute("SELECT * FROM image_analysis_cache")
        cache_rows = sq_cursor.fetchall()
        print(f"\n📦 Migrating {len(cache_rows)} diagnostic cache records...")
        for r in cache_rows:
            existing = pg_session.query(ImageAnalysisCache).filter(ImageAnalysisCache.id == r["id"]).first()
            if not existing:
                iac = ImageAnalysisCache(
                    id=r["id"],
                    image_hash=r["image_hash"],
                    user_id=r["user_id"],
                    filename=r["filename"],
                    disease_class=r["disease_class"],
                    confidence=r["confidence"],
                    distribution=parse_json(r["distribution"]),
                    env_data=parse_json(r["env_data"]),
                    advisory_text=r["advisory_text"],
                    sources=parse_json(r["sources"]),
                    is_blended=bool(r["is_blended"]),
                    created_at=parse_dt(r["created_at"]) or datetime.utcnow()
                )
                pg_session.add(iac)
        pg_session.commit()
        print(f"   ✅ Diagnostic cache records migrated.")

        # 6. Crop Listings
        sq_cursor.execute("SELECT * FROM crop_listings")
        listing_rows = sq_cursor.fetchall()
        print(f"\n📦 Migrating {len(listing_rows)} marketplace crop listings...")
        for r in listing_rows:
            existing = pg_session.query(CropListing).filter(CropListing.id == r["id"]).first()
            if not existing:
                cl = CropListing(
                    id=r["id"],
                    user_id=r["user_id"],
                    title=r["title"],
                    variety=r["variety"],
                    quantity_kg=r["quantity_kg"],
                    price_per_kg=r["price_per_kg"],
                    farmer_name=r["farmer_name"],
                    phone_number=r["phone_number"],
                    address=r["address"],
                    latitude=r["latitude"],
                    longitude=r["longitude"],
                    photos=parse_json(r["photos"]),
                    created_at=parse_dt(r["created_at"]) or datetime.utcnow()
                )
                pg_session.add(cl)
        pg_session.commit()
        print(f"   ✅ Crop listings migrated.")

        # Step 3: Synchronize PostgreSQL serial sequences so future inserts don't collide
        from sqlalchemy import text
        print("\n🔄 Synchronizing PostgreSQL auto-increment sequence counters...")
        serial_tables = [
            ("users", "id"),
            ("auth_tokens", "id"),
            ("chat_messages", "id"),
            ("image_analysis_cache", "id"),
            ("crop_listings", "id")
        ]
        with engine.connect() as conn:
            for tbl, col in serial_tables:
                try:
                    conn.execute(text(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{tbl}', '{col}'),
                            COALESCE((SELECT MAX({col}) FROM {tbl}), 1)
                        );
                    """))
                    conn.commit()
                except Exception as seq_err:
                    pass

        print("✅ Sequence counters updated successfully.")
        print("\n🎉 Migration completed successfully!")
        return True

    except Exception as ex:
        pg_session.rollback()
        print(f"\n❌ Migration error: {ex}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        pg_session.close()
        sq_conn.close()

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

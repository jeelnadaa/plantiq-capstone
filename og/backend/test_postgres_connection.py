"""
PlantIQ - PostgreSQL Connection & Health Diagnostic
--------------------------------------------------
Tests connection to PostgreSQL using credentials configured in backend/.env.
Creates the database and tables if they do not already exist.

Usage:
    python test_postgres_connection.py
"""

import sys
import os

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.core.config import settings

def test_connection():
    print("\n=======================================================")
    print("🐘 PlantIQ PostgreSQL Diagnostic & Connection Verifier")
    print("=======================================================")
    print(f" * Target Host:     {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    print(f" * Target User:     {settings.POSTGRES_USER}")
    print(f" * Target Database: {settings.POSTGRES_DB}")
    print(f" * Password Set:    {'Yes (***)' if settings.POSTGRES_PASSWORD else 'No (Empty)'}")
    print("-------------------------------------------------------")

    # Step 1: Check if driver is available
    try:
        import psycopg2
        print("✅ psycopg2 driver detected:", psycopg2.__version__)
    except ImportError:
        print("❌ ERROR: psycopg2 is not installed! Run: pip install psycopg2-binary")
        return False

    # Step 2: Attempt connecting directly or through postgres maintenance db
    from urllib.parse import quote_plus
    pw_part = f":{quote_plus(settings.POSTGRES_PASSWORD)}" if settings.POSTGRES_PASSWORD else ""

    from sqlalchemy import create_engine, text
    import sqlalchemy.exc

    print(f"📡 Attempting connection to '{settings.POSTGRES_DB}'...")
    try:
        from app.core.database import engine, Base
        import app.models # Register all models

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).fetchone()
            print(f"✅ Connected to PostgreSQL successfully!")
            print(f"   Server Version: {result[0]}")

        print("🔨 Verifying / Creating database schema tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created/verified successfully!")

        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\n📋 PostgreSQL Tables in '{settings.POSTGRES_DB}':")
        for tbl in sorted(tables):
            with engine.connect() as conn:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            print(f"   - {tbl:<25} ({count} rows)")

        print("\n🎉 PostgreSQL database is fully ready for PlantIQ!")
        return True

    except sqlalchemy.exc.OperationalError as e:
        err_msg = str(e)
        if "does not exist" in err_msg:
            print(f"\n⚠️ Database '{settings.POSTGRES_DB}' does not exist on PostgreSQL server.")
            print(f"💡 Attempting to create database '{settings.POSTGRES_DB}' automatically...")
            
            maint_url = f"postgresql://{settings.POSTGRES_USER}{pw_part}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/postgres"
            try:
                maint_engine = create_engine(maint_url, isolation_level="AUTOCOMMIT")
                with maint_engine.connect() as maint_conn:
                    maint_conn.execute(text(f'CREATE DATABASE "{settings.POSTGRES_DB}";'))
                print(f"✅ Database '{settings.POSTGRES_DB}' created successfully!")
                maint_engine.dispose()
                return test_connection()
            except Exception as create_err:
                print(f"❌ Could not automatically create database: {create_err}")
                print(f"👉 Please create it manually in psql / pgAdmin: CREATE DATABASE {settings.POSTGRES_DB};")
                return False
        else:
            print(f"\n❌ Connection failed: {e}")
            print("\n👉 Suggestions:")
            print("   1. Verify your PostgreSQL service is running.")
            print("   2. Check POSTGRES_PASSWORD, POSTGRES_USER, POSTGRES_HOST in backend/.env")
            print("   3. If using Docker, check that the port 5432 is mapped.")
            return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

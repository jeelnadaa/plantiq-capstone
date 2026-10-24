"""Database engine/session. PostgreSQL when configured (auto-creates the database), SQLite otherwise.

If PostgreSQL is configured but unreachable and DB_FALLBACK_TO_SQLITE is on, we fall back to the local
SQLite file (the original app behaved the same way).
"""
from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

log = logging.getLogger("plantiq.db")


class Base(DeclarativeBase):
    pass


def _sqlite_engine(url: str) -> Engine:
    if url.startswith("sqlite:///") and ":memory:" not in url:
        settings.VAR_DIR.mkdir(parents=True, exist_ok=True)
    kwargs: dict = {"connect_args": {"check_same_thread": False}}
    if ":memory:" in url:
        from sqlalchemy.pool import StaticPool
        kwargs["poolclass"] = StaticPool
    engine = create_engine(url, **kwargs)

    @event.listens_for(engine, "connect")
    def _pragmas(dbapi_conn, _):  # noqa: ANN001
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        if ":memory:" not in url:
            cur.execute("PRAGMA journal_mode=WAL")
        cur.close()

    return engine


def _ensure_postgres_database(url: str) -> None:
    """Create the target database if the server is up but the DB does not exist yet."""
    parsed = make_url(url)
    admin = create_engine(parsed.set(database="postgres"), isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with admin.connect() as conn:
            exists = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :n"), {"n": parsed.database}).scalar()
            if not exists:
                conn.execute(text(f'CREATE DATABASE "{parsed.database}"'))
                log.info("Created PostgreSQL database %s", parsed.database)
    finally:
        admin.dispose()


def build_engine(url: str | None = None) -> Engine:
    url = url or settings.DATABASE_URL
    if url.startswith("sqlite"):
        return _sqlite_engine(url)
    try:
        _ensure_postgres_database(url)
        engine = create_engine(url, pool_pre_ping=True, pool_size=10, max_overflow=20)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        log.info("Using PostgreSQL at %s", make_url(url).render_as_string(hide_password=True))
        return engine
    except Exception as exc:  # pragma: no cover - depends on local services
        if not settings.DB_FALLBACK_TO_SQLITE:
            raise
        log.warning("PostgreSQL unavailable (%s). Falling back to SQLite at %s", exc.__class__.__name__, settings.sqlite_path)
        return _sqlite_engine(f"sqlite:///{settings.sqlite_path.as_posix()}")


engine: Engine = build_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(bind: Engine | None = None) -> None:
    """Create tables and apply additive column migrations (safe to run on every start)."""
    import app.models  # noqa: F401  (register models)

    target = bind or engine
    Base.metadata.create_all(target)
    _additive_migrations(target)


def _additive_migrations(target: Engine) -> None:
    """Add any model columns that are missing from existing tables (no destructive changes)."""
    insp = inspect(target)
    with target.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if not insp.has_table(table.name):
                continue
            existing = {c["name"] for c in insp.get_columns(table.name)}
            for col in table.columns:
                if col.name in existing:
                    continue
                ddl_type = col.type.compile(dialect=target.dialect)
                conn.execute(text(f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {ddl_type}'))
                log.info("Added column %s.%s", table.name, col.name)


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_backend_name() -> str:
    return engine.dialect.name

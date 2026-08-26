"""
Alembic env.py — Async-compatible migration environment for Stream2Vec.

Uses SQLAlchemy's async engine (asyncpg) for the online path.
Supports offline SQL generation without a live database.

DATABASE_URL env var overrides the URL in alembic.ini.
The app model imports are deferred so the env.py can be loaded
even when the full application config (SECRET_KEY, etc.) is absent.
"""

import asyncio
import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import MetaData, pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# ── Make sure `backend/` is on sys.path ──────────────────────────────────────
# Alembic is invoked from within backend/, but make this robust either way.
_backend_dir = Path(__file__).resolve().parent.parent
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# ── Override sqlalchemy.url from env if present ──────────────────────────────
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    config.set_main_option("sqlalchemy.url", _db_url)

# ── Logging ──────────────────────────────────────────────────────────────────
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Lazy model import ─────────────────────────────────────────────────────────
# Set minimal env vars so pydantic-settings doesn't reject startup before we
# can load models.  These are never used for actual DB connections here.
_sentinel = "__alembic_dummy__"
for _var in ("SECRET_KEY", "DATABASE_URL", "MINIO_ENDPOINT", "MINIO_ACCESS_KEY",
             "MINIO_SECRET_KEY", "KAFKA_BOOTSTRAP_SERVERS"):
    os.environ.setdefault(_var, _sentinel)

import app.models  # noqa: F401 — registers all ORM models on Base.metadata
from app.database.base import Base  # noqa: E402

target_metadata = Base.metadata


# ── Offline mode ─────────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Emit SQL to stdout — no live DB connection required."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Online mode (async) ───────────────────────────────────────────────────────
def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

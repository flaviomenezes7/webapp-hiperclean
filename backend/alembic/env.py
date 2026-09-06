"""Alembic environment configuration.

Loads the DATABASE_URL from the app settings and imports all SQLModel models
so Alembic can detect schema changes for autogeneration.
"""

from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# --- Import app config and all models ---
from app.config import get_settings
from sqlmodel import SQLModel

# This import triggers model registration on SQLModel.metadata
import app.models  # noqa: F401

# Alembic Config object
config = context.config

# Get DB URL directly (bypass configparser to avoid % interpolation issues)
db_url = get_settings().DATABASE_URL

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=db_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(db_url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

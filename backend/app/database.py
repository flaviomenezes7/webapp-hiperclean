from sqlmodel import Session, create_engine, SQLModel
from typing import Generator
from app.config import get_settings

settings = get_settings()
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

connect_args = {}
engine_kwargs = {"echo": False}

if is_sqlite:
    # SQLite needs check_same_thread=False for FastAPI (multi-threaded)
    connect_args["check_same_thread"] = False
else:
    # Postgres-specific pool settings
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs,
)


def create_db_and_tables():
    """Create all tables — used for SQLite local dev. For Postgres, use Alembic."""
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session

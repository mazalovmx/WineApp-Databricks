"""Database connection and session for FastAPI."""
import os
from collections.abc import Generator
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

try:
    from .config import settings
    _database_url = settings.database_url
except Exception:
    _database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/winefinder")

engine = create_engine(
    _database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI - yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session():
    """Context manager for sync session (used by non-async routes and pipeline)."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

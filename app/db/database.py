"""
Database connection/session setup. Uses SQLAlchemy so switching from
SQLite to PostgreSQL is just a DATABASE_URL change.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Create all tables. Call once at app startup."""
    from app.db import models  # noqa: F401  (ensures models are registered)
    Base.metadata.create_all(bind=engine)


def get_session():
    """Yield a DB session, closing it afterward (FastAPI/Streamlit-friendly)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

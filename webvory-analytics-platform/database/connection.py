"""
Database connection setup using SQLAlchemy.
Configure your PostgreSQL credentials via environment variables or defaults below.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ──────────────────────────────────────────────
# Connection config
# ──────────────────────────────────────────────

DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "webvory_db")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ──────────────────────────────────────────────
# Engine + Session
# ──────────────────────────────────────────────

engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # keep 10 connections ready
    max_overflow=20,       # allow up to 20 extra under load
    pool_pre_ping=True,    # check connection is alive before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes - yields a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
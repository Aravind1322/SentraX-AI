"""
SentraX AI Backend — database/session.py
Database session maker and context manager helpers.
"""

from sqlalchemy.orm import sessionmaker
from database.connection import engine
from contextlib import contextmanager

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_session():
    """Yield a database session context manager."""
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

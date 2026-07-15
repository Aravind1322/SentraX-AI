"""
SentraX AI Backend — database/connection.py
Central connection and engine config abstraction supporting SQLite and PostgreSQL.
"""

import os
from sqlalchemy import create_engine
from config import DATABASE_PATH

# Default to SQLite local database aligned with legacy DATABASE_PATH
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_PATH}")

# Create engine with appropriate pooling options based on dialect
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
else:
    # SQLite fallback
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

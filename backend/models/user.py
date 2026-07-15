"""
SentraX AI Backend — models/user.py
SQLAlchemy User model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)

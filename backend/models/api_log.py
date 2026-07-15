"""
SentraX AI Backend — models/api_log.py
SQLAlchemy API request logger model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class APIRequestLog(Base):
    __tablename__ = "api_request_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    endpoint = Column(String, nullable=False)
    scan_type = Column(String)
    result = Column(String)
    created_at = Column(DateTime, default=func.now())

"""
SentraX AI Backend — models/ioc.py
SQLAlchemy IOCRecord model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class IOCRecord(Base):
    __tablename__ = "ioc_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ioc_type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    source = Column(String)
    severity = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

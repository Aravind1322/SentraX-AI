"""
SentraX AI Backend — models/alert.py
SQLAlchemy Alert model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    severity = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Unacknowledged")
    score = Column(Integer)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    timestamp = Column(DateTime, default=func.now())

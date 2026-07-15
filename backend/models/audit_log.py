"""
SentraX AI Backend — models/audit_log.py
SQLAlchemy AuditLog model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(String, nullable=False)
    details = Column(String)
    timestamp = Column(DateTime, default=func.now())
    user_id = Column(Integer)
    ip_address = Column(String)

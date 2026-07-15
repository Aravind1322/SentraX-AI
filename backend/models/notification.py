"""
SentraX AI Backend — models/notification.py
SQLAlchemy Notification model.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    is_read = Column(Integer, default=0)
    timestamp = Column(DateTime, default=func.now())

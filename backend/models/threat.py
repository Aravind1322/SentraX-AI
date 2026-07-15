"""
SentraX AI Backend — models/threat.py
SQLAlchemy ThreatFeed and FeedSyncStatus models.
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from database.base import Base


class ThreatFeed(Base):
    __tablename__ = "threat_feeds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feed_type = Column(String, nullable=False)
    value = Column(String, nullable=False)
    source = Column(String)
    confidence_score = Column(Integer, default=80)
    created_at = Column(DateTime, default=func.now())


class FeedSyncStatus(Base):
    __tablename__ = "feed_sync_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feed_name = Column(String, nullable=False, unique=True)
    last_synced = Column(DateTime, default=func.now())
    status = Column(String)

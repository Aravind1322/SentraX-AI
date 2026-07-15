"""
SentraX AI Backend — models/scan.py
SQLAlchemy scan storage models (normalized + summary history).
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from database.base import Base


class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_type = Column(String, nullable=False)
    input_data = Column(String, nullable=False)
    score = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    threat_level = Column(String, nullable=False)
    confidence = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now())


class ScanDetail(Base):
    __tablename__ = "scan_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scan_history.id", ondelete="CASCADE"), nullable=False)
    scan_type = Column(String, nullable=False)
    target = Column(String)
    score = Column(Integer, nullable=False)
    label = Column(String, nullable=False)
    confidence = Column(Integer)
    threat_level = Column(String, nullable=False)
    scanner_version = Column(String)
    created_at = Column(DateTime, default=func.now())


class ScanReason(Base):
    __tablename__ = "scan_reasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_detail_id = Column(Integer, ForeignKey("scan_details.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String, nullable=False)


class TechnicalMetric(Base):
    __tablename__ = "technical_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_detail_id = Column(Integer, ForeignKey("scan_details.id", ondelete="CASCADE"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(String, nullable=False)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_detail_id = Column(Integer, ForeignKey("scan_details.id", ondelete="CASCADE"), nullable=False)
    recommendation = Column(String, nullable=False)


class ScanMetadata(Base):
    __tablename__ = "scan_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_detail_id = Column(Integer, ForeignKey("scan_details.id", ondelete="CASCADE"), nullable=False)
    execution_time_ms = Column(Integer)
    backend_version = Column(String)
    api_version = Column(String)
    engine_name = Column(String)
    engine_version = Column(String)

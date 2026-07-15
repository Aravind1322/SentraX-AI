"""
SentraX AI Backend — models/case.py
SQLAlchemy Case Management models.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from database.base import Base


class SOCCase(Base):
    __tablename__ = "soc_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    priority = Column(String, nullable=False)
    status = Column(String, nullable=False)
    assigned_analyst = Column(String)
    evidence_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CaseEvidence(Base):
    __tablename__ = "case_evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("soc_cases.id", ondelete="CASCADE"), nullable=False)
    evidence_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_metadata = Column(String)
    added_at = Column(DateTime, default=func.now())


class CaseTimeline(Base):
    __tablename__ = "case_timeline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(Integer, ForeignKey("soc_cases.id", ondelete="CASCADE"), nullable=False)
    event_title = Column(String, nullable=False)
    event_description = Column(String)
    event_time = Column(DateTime, default=func.now())

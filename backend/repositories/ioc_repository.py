"""
SentraX AI Backend — repositories/ioc_repository.py
Repository class abstraction for IOCs using SQLAlchemy.
"""

from sqlalchemy.orm import Session
from models.ioc import IOCRecord
from typing import List, Optional


class IOCRepository:
    """
    Handles all queries and writes targeting Indicators of Compromise signatures.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[IOCRecord]:
        """Fetch all watchlist signatures sorted by creation date, newest first."""
        return self.db.query(IOCRecord).order_by(IOCRecord.created_at.desc()).all()

    def create(self, ioc_type: str, value: str, source: str, severity: str) -> IOCRecord:
        """Create and persist a new Indicator of Compromise signature."""
        ioc = IOCRecord(
            ioc_type=ioc_type,
            value=value,
            source=source,
            severity=severity
        )
        self.db.add(ioc)
        self.db.commit()
        return ioc

    def delete(self, ioc_id: int) -> bool:
        """Removes a signature record from watchlist."""
        ioc = self.db.query(IOCRecord).filter(IOCRecord.id == ioc_id).first()
        if ioc:
            self.db.delete(ioc)
            self.db.commit()
            return True
        return False

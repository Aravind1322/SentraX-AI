"""
SentraX AI Backend — repositories/alert_repository.py
Repository class abstraction for alerts using SQLAlchemy.
"""

from sqlalchemy.orm import Session
from models.alert import Alert
from typing import List, Optional
from datetime import datetime


class AlertRepository:
    """
    Handles all queries and writes targeting SOC real-time alerts.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, status: Optional[str] = None) -> List[Alert]:
        """Fetch all alert records, optionally filtered by status, newest first."""
        query = self.db.query(Alert)
        if status:
            query = query.filter(Alert.status == status)
        return query.order_by(Alert.timestamp.desc()).all()

    def create(self, title: str, description: str, severity: str, score: int) -> Alert:
        """Create and persist a new real-time threat alert."""
        alert = Alert(
            title=title,
            description=description,
            severity=severity,
            score=score
        )
        self.db.add(alert)
        self.db.commit()
        return alert

    def acknowledge(self, alert_id: int, analyst: str) -> bool:
        """Marks alert status as acknowledged by a specified analyst."""
        alert = self.db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.status = "Acknowledged"
            alert.acknowledged_by = analyst
            alert.acknowledged_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

"""
SentraX AI Backend — utils/database_writer.py
Helper module for populating and normalising the SOC database tables using repositories.
"""

from typing import Dict, Any, List, Optional
from database.session import SessionLocal
from repositories.history_repository import HistoryRepository
from database import create_notification


def save_scan(
    scan_type: str,
    input_data: str,
    score: int,
    label: str,
    threat_level: str,
    confidence: int,
    reasons: Optional[List[str]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    recommendations: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    scanner_version: str = "v5.0"
) -> int:
    """
    Persist scan summaries and details using HistoryRepository.
    """
    scan_id = -1
    session = SessionLocal()
    try:
        repo = HistoryRepository(session)
        history = repo.save_scan(
            scan_type=scan_type,
            input_data=input_data,
            score=score,
            label=label,
            threat_level=threat_level,
            confidence=confidence,
            reasons=reasons,
            metrics=metrics,
            recommendations=recommendations,
            metadata=metadata,
            scanner_version=scanner_version
        )
        scan_id = history.id
    except Exception as e:
        print(f"Database error in database_writer.save_scan: {e}")
    finally:
        session.close()

    # Notification checks & Alerts
    if score >= 90:
        create_notification(
            title="CRITICAL: Critical Anomaly Detected",
            message=f"A risk score of {score} was flagged for a {scan_type} scan.",
            severity="CRITICAL"
        )
    elif threat_level == "HIGH":
        create_notification(
            title="WARNING: High Threat Classified",
            message=f"High risk threat level flagged for a {scan_type} scan.",
            severity="WARNING"
        )

    try:
        from services.alert_engine import AlertEngine
        AlertEngine.trigger_scan_alert(scan_type, input_data, score)
    except Exception as ae_err:
        print(f"Error triggering alert engine in writer: {ae_err}")

    return scan_id

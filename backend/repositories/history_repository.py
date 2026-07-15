"""
SentraX AI Backend — repositories/history_repository.py
Repository class abstraction for scan histories and normalized tables using SQLAlchemy.
"""

from sqlalchemy.orm import Session
from models.scan import ScanHistory, ScanDetail, ScanReason, TechnicalMetric, Recommendation, ScanMetadata
from typing import Dict, Any, List, Optional
from datetime import datetime


class HistoryRepository:
    """
    Handles all queries and writes targeting the scan_history and normalized scan tables.
    """

    def __init__(self, db: Session):
        self.db = db

    def save_scan(
        self,
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
    ) -> ScanHistory:
        """
        Persists a full normalized threat scan to database inside a single transactional unit.
        """
        # 1. Summary Scan History
        history = ScanHistory(
            scan_type=scan_type,
            input_data=input_data,
            score=score,
            label=label,
            threat_level=threat_level,
            confidence=confidence
        )
        self.db.add(history)
        self.db.flush()

        # 2. Detailed Scan properties
        detail = ScanDetail(
            scan_id=history.id,
            scan_type=scan_type,
            target=input_data,
            score=score,
            label=label,
            confidence=confidence,
            threat_level=threat_level,
            scanner_version=scanner_version
        )
        self.db.add(detail)
        self.db.flush()

        # 3. Threat reasons list
        if reasons:
            for r in reasons:
                self.db.add(ScanReason(scan_detail_id=detail.id, reason=r))

        # 4. Technical Metrics dict
        if metrics:
            for name, val in metrics.items():
                self.db.add(TechnicalMetric(
                    scan_detail_id=detail.id,
                    metric_name=str(name),
                    metric_value=str(val)
                ))

        # 5. Recommendations list
        if recommendations:
            for rec in recommendations:
                self.db.add(Recommendation(scan_detail_id=detail.id, recommendation=rec))

        # 6. Metadata attributes
        meta = metadata or {}
        exec_time = meta.get("execution_time_ms", 10)
        backend_v = meta.get("backend_version", "v1.0.0")
        api_v = meta.get("api_version", "v1")
        engine_n = meta.get("engine_name", "SentraX AI Engine")
        engine_v = meta.get("engine_version", "v1.0")

        self.db.add(ScanMetadata(
            scan_detail_id=detail.id,
            execution_time_ms=exec_time,
            backend_version=backend_v,
            api_version=api_v,
            engine_name=engine_n,
            engine_version=engine_v
        ))

        self.db.commit()
        return history

    def get_by_id(self, scan_id: int) -> Optional[ScanHistory]:
        """Fetch summary record by database primary key."""
        return self.db.query(ScanHistory).filter(ScanHistory.id == scan_id).first()

    def get_detail_by_scan_id(self, scan_id: int) -> Optional[ScanDetail]:
        """Fetch detailed record linked to summary scan ID."""
        return self.db.query(ScanDetail).filter(ScanDetail.scan_id == scan_id).first()

    def get_reasons_by_detail_id(self, detail_id: int) -> List[ScanReason]:
        """Retrieve reasons collection linked to scan detail."""
        return self.db.query(ScanReason).filter(ScanReason.scan_detail_id == detail_id).all()

    def get_metrics_by_detail_id(self, detail_id: int) -> List[TechnicalMetric]:
        """Retrieve key-value technical metrics linked to scan detail."""
        return self.db.query(TechnicalMetric).filter(TechnicalMetric.scan_detail_id == detail_id).all()

    def get_recommendations_by_detail_id(self, detail_id: int) -> List[Recommendation]:
        """Retrieve security recommendations linked to scan detail."""
        return self.db.query(Recommendation).filter(Recommendation.scan_detail_id == detail_id).all()

    def get_metadata_by_detail_id(self, detail_id: int) -> Optional[ScanMetadata]:
        """Retrieve engine details metadata linked to scan detail."""
        return self.db.query(ScanMetadata).filter(ScanMetadata.scan_detail_id == detail_id).first()

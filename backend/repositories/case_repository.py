"""
SentraX AI Backend — repositories/case_repository.py
Repository class abstraction for cases using SQLAlchemy.
"""

from sqlalchemy.orm import Session
from models.case import SOCCase, CaseEvidence, CaseTimeline
from typing import List, Optional, Dict, Any
import json


class CaseRepository:
    """
    Handles all queries and writes targeting SOC investigation cases,
    evidence vault uploads, and case timeline chronological events.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str, description: str, priority: str, assigned_analyst: Optional[str] = None) -> SOCCase:
        """Create and persist a new SOC case file, appending the initial event to its timeline."""
        case = SOCCase(
            title=title,
            description=description,
            priority=priority,
            status="Open",
            assigned_analyst=assigned_analyst
        )
        self.db.add(case)
        self.db.flush()

        # Add initial timeline log
        timeline = CaseTimeline(
            case_id=case.id,
            event_title="Case Opened",
            event_description=f"Investigation case initialized by {assigned_analyst or 'System'}"
        )
        self.db.add(timeline)
        self.db.commit()
        return case

    def get_all(self) -> List[SOCCase]:
        """Fetch all case files ordered by update times, newest first."""
        return self.db.query(SOCCase).order_by(SOCCase.updated_at.desc()).all()

    def get_by_id(self, case_id: int) -> Optional[SOCCase]:
        """Fetch case summary record by primary key."""
        return self.db.query(SOCCase).filter(SOCCase.id == case_id).first()

    def get_timeline(self, case_id: int) -> List[CaseTimeline]:
        """Retrieve chronological timeline items linked to case."""
        return self.db.query(CaseTimeline).filter(CaseTimeline.case_id == case_id).order_by(CaseTimeline.event_time.asc()).all()

    def get_evidence(self, case_id: int) -> List[CaseEvidence]:
        """Retrieve evidence log files linked to case."""
        return self.db.query(CaseEvidence).filter(CaseEvidence.case_id == case_id).all()

    def update(self, case_id: int, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None, assigned_analyst: Optional[str] = None) -> bool:
        """Update case detail properties, generating a timeline change entry."""
        case = self.get_by_id(case_id)
        if not case:
            return False

        timeline_desc = []
        if title is not None:
            case.title = title
            timeline_desc.append(f"Title updated to '{title}'")
        if description is not None:
            case.description = description
            timeline_desc.append("Description modified")
        if priority is not None:
            case.priority = priority
            timeline_desc.append(f"Priority changed to {priority}")
        if status is not None:
            case.status = status
            timeline_desc.append(f"Status changed to {status}")
        if assigned_analyst is not None:
            case.assigned_analyst = assigned_analyst
            timeline_desc.append(f"Assigned analyst set to {assigned_analyst}")

        if timeline_desc:
            timeline = CaseTimeline(
                case_id=case_id,
                event_title="Case Details Modified",
                event_description=", ".join(timeline_desc)
            )
            self.db.add(timeline)
            self.db.commit()
            return True
        return False

    def delete(self, case_id: int) -> bool:
        """Delete case and cascade-delete all timelines and evidences linked to it."""
        case = self.get_by_id(case_id)
        if case:
            self.db.delete(case)
            self.db.commit()
            return True
        return False

    def add_evidence(self, case_id: int, evidence_type: str, file_name: str, file_metadata: Optional[Dict[str, Any]] = None) -> CaseEvidence:
        """Upload evidence file logs, linking to case and creating a timeline item."""
        meta_str = json.dumps(file_metadata) if file_metadata else None
        evidence = CaseEvidence(
            case_id=case_id,
            evidence_type=evidence_type,
            file_name=file_name,
            file_metadata=meta_str
        )
        self.db.add(evidence)
        
        # Increment counter
        case = self.get_by_id(case_id)
        if case:
            case.evidence_count += 1
            
        # Log timeline event
        timeline = CaseTimeline(
            case_id=case_id,
            event_title="Evidence Uploaded",
            event_description=f"Added {evidence_type} file: '{file_name}' to evidence vault."
        )
        self.db.add(timeline)
        
        self.db.commit()
        return evidence

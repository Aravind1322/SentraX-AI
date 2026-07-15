"""
SentraX AI Backend — services/case_management_service.py
Case Management, Evidence Repository, and Chronological Timeline Service layer.
"""

from typing import Dict, Any, List, Optional
import json
from database import get_connection


class CaseManagementService:
    """
    Service class managing SOC investigations, timeline events,
    and associated case evidence logs.
    """

    @staticmethod
    def create_case(title: str, description: str, priority: str = "MEDIUM", assigned_analyst: Optional[str] = None) -> Dict[str, Any]:
        """Creates a new SOC investigation case and builds the initial timeline entry."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO soc_cases (title, description, priority, status, assigned_analyst)
                    VALUES (?, ?, ?, 'Open', ?)
                    """,
                    (title, description, priority, assigned_analyst)
                )
                conn.commit()
                case_id = cursor.lastrowid
                
                # Create initial timeline entry
                cursor.execute(
                    """
                    INSERT INTO case_timeline (case_id, event_title, event_description)
                    VALUES (?, 'Case Opened', ?)
                    """,
                    (case_id, f"Investigation case initialized by {assigned_analyst or 'System'}")
                )
                conn.commit()

                return {
                    "id": case_id,
                    "title": title,
                    "description": description,
                    "priority": priority,
                    "status": "Open",
                    "assigned_analyst": assigned_analyst,
                    "evidence_count": 0
                }
        except Exception as e:
            print(f"Error creating case: {e}")
            return {"error": str(e)}

    @staticmethod
    def get_all_cases() -> List[Dict[str, Any]]:
        """Fetch all SOC cases from database."""
        cases = []
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, title, description, priority, status, assigned_analyst, evidence_count, created_at, updated_at FROM soc_cases ORDER BY updated_at DESC")
                for row in cursor.fetchall():
                    cases.append(dict(row))
        except Exception as e:
            print(f"Error fetching cases: {e}")
        return cases

    @staticmethod
    def get_case(case_id: int) -> Optional[Dict[str, Any]]:
        """Fetch details, evidence files list, and timeline events of a specific case."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, title, description, priority, status, assigned_analyst, evidence_count, created_at, updated_at FROM soc_cases WHERE id = ?", (case_id,))
                case_row = cursor.fetchone()
                if not case_row:
                    return None

                case_data = dict(case_row)
                
                # Fetch Timeline
                cursor.execute("SELECT id, event_title, event_description, event_time FROM case_timeline WHERE case_id = ? ORDER BY event_time ASC", (case_id,))
                case_data["timeline"] = [dict(r) for r in cursor.fetchall()]

                # Fetch Evidence
                cursor.execute("SELECT id, evidence_type, file_name, file_metadata, added_at FROM case_evidence WHERE case_id = ?", (case_id,))
                case_data["evidence"] = []
                for r in cursor.fetchall():
                    evidence_item = dict(r)
                    if evidence_item["file_metadata"]:
                        try:
                            evidence_item["file_metadata"] = json.loads(evidence_item["file_metadata"])
                        except:
                            pass
                    case_data["evidence"].append(evidence_item)

                return case_data
        except Exception as e:
            print(f"Error fetching case {case_id}: {e}")
            return None

    @staticmethod
    def update_case(case_id: int, title: Optional[str] = None, description: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None, assigned_analyst: Optional[str] = None) -> bool:
        """Update case details and append a change event to the timeline."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Build update query
                fields = []
                params = []
                timeline_desc = []
                
                if title is not None:
                    fields.append("title = ?")
                    params.append(title)
                    timeline_desc.append(f"Title updated to '{title}'")
                if description is not None:
                    fields.append("description = ?")
                    params.append(description)
                    timeline_desc.append("Description modified")
                if priority is not None:
                    fields.append("priority = ?")
                    params.append(priority)
                    timeline_desc.append(f"Priority changed to {priority}")
                if status is not None:
                    fields.append("status = ?")
                    params.append(status)
                    timeline_desc.append(f"Status changed to {status}")
                if assigned_analyst is not None:
                    fields.append("assigned_analyst = ?")
                    params.append(assigned_analyst)
                    timeline_desc.append(f"Assigned analyst set to {assigned_analyst}")

                if not fields:
                    return False

                fields.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE soc_cases SET {', '.join(fields)} WHERE id = ?"
                params.append(case_id)
                
                cursor.execute(query, params)
                updated = cursor.rowcount > 0
                
                if updated:
                    # Log event on timeline
                    cursor.execute(
                        """
                        INSERT INTO case_timeline (case_id, event_title, event_description)
                        VALUES (?, 'Case Details Modified', ?)
                        """,
                        (case_id, ", ".join(timeline_desc))
                    )
                    conn.commit()
                return updated
        except Exception as e:
            print(f"Error updating case {case_id}: {e}")
            return False

    @staticmethod
    def delete_case(case_id: int) -> bool:
        """Delete case and all related timeline + evidence entries."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM soc_cases WHERE id = ?", (case_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting case {case_id}: {e}")
            return False

    @staticmethod
    def add_evidence(case_id: int, evidence_type: str, file_name: str, file_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Upload evidence metadata, link to case, increment evidence count, and update timeline."""
        try:
            meta_str = json.dumps(file_metadata) if file_metadata else None
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO case_evidence (case_id, evidence_type, file_name, file_metadata)
                    VALUES (?, ?, ?, ?)
                    """,
                    (case_id, evidence_type, file_name, meta_str)
                )
                
                # Increment count
                cursor.execute("UPDATE soc_cases SET evidence_count = evidence_count + 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (case_id,))
                
                # Timeline log
                cursor.execute(
                    """
                    INSERT INTO case_timeline (case_id, event_title, event_description)
                    VALUES (?, 'Evidence Uploaded', ?)
                    """,
                    (case_id, f"Added {evidence_type} file: '{file_name}' to evidence vault.")
                )
                conn.commit()
                return {"message": "Evidence added successfully", "file_name": file_name}
        except Exception as e:
            print(f"Error adding evidence to case {case_id}: {e}")
            return {"error": str(e)}

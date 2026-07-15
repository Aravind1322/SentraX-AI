"""
SentraX AI Backend — services/ioc_service.py
IOC service layer handling CRUD operations, database schema features, imports/exports, and metrics.
"""

from typing import Dict, Any, List
from database import get_connection


class IOCService:
    """
    Service class managing SQLite storage of indicators (domains, URLs, IPs, wallets, file hashes).
    """

    @staticmethod
    def create_ioc(
        ioc_type: str,
        value: str,
        source: str = "Manual Entry",
        severity: str = "MEDIUM",
        confidence: int = 80,
        description: str = "Threat intelligence watchlist item",
        status: str = "Active"
    ) -> Dict[str, Any]:
        """Insert a new IOC record to database."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO ioc_records (ioc_type, value, source, severity, confidence, description, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (ioc_type, value, source, severity, confidence, description, status)
                )
                conn.commit()
                ioc_id = cursor.lastrowid
                return {
                    "id": ioc_id,
                    "ioc_type": ioc_type,
                    "value": value,
                    "source": source,
                    "severity": severity,
                    "confidence": confidence,
                    "description": description,
                    "status": status,
                    "created_at": "Just now"
                }
        except Exception as e:
            print(f"Error creating IOC: {e}")
            return {"error": str(e)}

    @staticmethod
    def update_ioc(
        ioc_id: int,
        ioc_type: str,
        value: str,
        source: str,
        severity: str,
        confidence: int,
        description: str,
        status: str
    ) -> bool:
        """Update an existing IOC signature by ID."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE ioc_records 
                    SET ioc_type = ?, value = ?, source = ?, severity = ?, confidence = ?, description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (ioc_type, value, source, severity, confidence, description, status, ioc_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating IOC {ioc_id}: {e}")
            return False

    @staticmethod
    def get_all_iocs() -> List[Dict[str, Any]]:
        """Fetch all IOC signatures from SQLite."""
        iocs = []
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, ioc_type, value, source, severity, confidence, description, status, created_at, updated_at 
                    FROM ioc_records 
                    ORDER BY created_at DESC
                    """
                )
                for row in cursor.fetchall():
                    iocs.append(dict(row))
        except Exception as e:
            print(f"Error fetching IOCs: {e}")
        return iocs

    @staticmethod
    def delete_ioc(ioc_id: int) -> bool:
        """Delete an IOC signature by ID."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM ioc_records WHERE id = ?", (ioc_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting IOC {ioc_id}: {e}")
            return False

    @staticmethod
    def get_recent_triggers(limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch threat history triggers from the database."""
        triggers = []
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, timestamp, user_email, scanner, ioc_value, severity, action 
                    FROM ioc_triggers 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                    """,
                    (limit,)
                )
                for row in cursor.fetchall():
                    triggers.append(dict(row))
        except Exception as e:
            print(f"Error fetching recent triggers: {e}")
        return triggers

    @staticmethod
    def get_kpis() -> Dict[str, Any]:
        """Fetch threat intelligence statistics from SQLite."""
        stats = {
            "total_threats": 0,
            "critical_iocs": 0,
            "high_risk_iocs": 0,
            "recently_added": 0
        }
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM ioc_records")
                stats["total_threats"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM ioc_records WHERE severity = 'CRITICAL'")
                stats["critical_iocs"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM ioc_records WHERE severity = 'HIGH'")
                stats["high_risk_iocs"] = cursor.fetchone()[0] or 0

                cursor.execute("SELECT COUNT(*) FROM ioc_records WHERE datetime(created_at) >= datetime('now', '-7 days')")
                stats["recently_added"] = cursor.fetchone()[0] or 0
        except Exception as e:
            print(f"Error fetching IOC KPIs: {e}")
        return stats

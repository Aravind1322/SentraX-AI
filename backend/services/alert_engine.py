"""
SentraX AI Backend — services/alert_engine.py
Realtime Alert Engine, Threat Correlation, and Incident Severity Calculator.
"""

from typing import Dict, Any, List, Optional
from database import get_connection
from datetime import datetime


class AlertEngine:
    """
    Service class managing SOC real-time alert logs, threat correlation matching,
    and automatic incident severity evaluations.
    """

    @staticmethod
    def get_all_alerts(status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch SOC alerts from database, optionally filtered by status."""
        alerts = []
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                query = "SELECT id, title, description, severity, status, score, acknowledged_by, acknowledged_at, timestamp FROM alerts"
                params = []
                if status:
                    query += " WHERE status = ?"
                    params.append(status)
                query += " ORDER BY timestamp DESC"
                
                cursor.execute(query, params)
                for row in cursor.fetchall():
                    alerts.append(dict(row))
        except Exception as e:
            print(f"Error fetching alerts: {e}")
        return alerts

    @staticmethod
    def acknowledge_alert(alert_id: int, analyst: str = "Admin") -> bool:
        """Acknowledge a security alert in SOC logs."""
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE alerts 
                    SET status = 'Acknowledged', acknowledged_by = ?, acknowledged_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                    """,
                    (analyst, alert_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error acknowledging alert {alert_id}: {e}")
            return False

    @staticmethod
    def correlate_threat(input_data: str) -> Dict[str, Any]:
        """
        Threat Correlation Engine: Calculates correlation scores by detecting
        repeated URLs, IPs, domains, or phone numbers in scan history.
        """
        correlation_score = 0
        incident_count = 0
        reasons = []

        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                # Count matches in scan history
                cursor.execute(
                    "SELECT COUNT(*), AVG(score) FROM scan_history WHERE input_data LIKE ?",
                    (f"%{input_data}%",)
                )
                row = cursor.fetchone()
                if row:
                    incident_count = row[0] or 0

            if incident_count > 1:
                reasons.append(f"Threat indicator matched in {incident_count} historical scans")
                correlation_score = min(100, incident_count * 20)
            else:
                correlation_score = 0

        except Exception as e:
            print(f"Correlation check error: {e}")

        return {
            "correlation_score": correlation_score,
            "incident_count": incident_count,
            "reasons": reasons
        }

    @staticmethod
    def calculate_severity(score: int, correlation_score: int) -> str:
        """
        Incident Severity Calculator: Evaluates threat level as LOW, MEDIUM, HIGH, or CRITICAL.
        Based on risk scores and correlation indicators.
        """
        # Base logic on risk score
        if score >= 90 or (score >= 70 and correlation_score > 50):
            return "CRITICAL"
        elif score >= 70 or (score >= 50 and correlation_score > 30):
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        else:
            return "LOW"

    @classmethod
    def trigger_scan_alert(cls, scan_type: str, input_data: str, score: int) -> None:
        """
        Assess scan risk, run correlation + severity calculations, and write
        to SOC alerts table if threat matches critical thresholds.
        """
        correlation = cls.correlate_threat(input_data)
        severity = cls.calculate_severity(score, correlation["correlation_score"])

        # We trigger SOC alerts for MEDIUM, HIGH, and CRITICAL indicators
        if severity != "LOW":
            title = f"SOC Alert: {severity} Risk {scan_type} Threat"
            desc = (
                f"Indicator '{input_data}' was scanned with a risk score of {score}. "
                f"Correlation engine score: {correlation['correlation_score']}%."
            )
            import re
            title = re.sub(r'<[^>]+>', '', str(title))
            desc = re.sub(r'<[^>]+>', '', str(desc))
            
            import logging
            alerts_logger = logging.getLogger("alerts")
            alerts_logger.info(f"Generated SOC Alert: {title} | Severity: {severity} | Score: {score} | Description: {desc}")

            try:
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO alerts (title, description, severity, score)
                        VALUES (?, ?, ?, ?)
                        """,
                        (title, desc, severity, score)
                    )
                    conn.commit()

                # Broadcast newly created HIGH or CRITICAL alerts immediately
                if severity in ["HIGH", "CRITICAL"]:
                    try:
                        import asyncio
                        from utils.connection_manager import manager
                        alert_payload = {
                            "event": "new_alert",
                            "title": title,
                            "description": desc,
                            "severity": severity,
                            "score": score,
                            "timestamp": datetime.now().isoformat()
                        }
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                loop.create_task(manager.broadcast(alert_payload, channel="alerts"))
                            else:
                                loop.run_until_complete(manager.broadcast(alert_payload, channel="alerts"))
                        except RuntimeError:
                            asyncio.run(manager.broadcast(alert_payload, channel="alerts"))
                    except Exception as ws_err:
                        err_logger = logging.getLogger("errors")
                        err_logger.error(f"Failed broadcasting WebSocket alert: {ws_err}")

            except Exception as e:
                err_logger = logging.getLogger("errors")
                err_logger.error(f"Error persisting SOC alert: {e}")

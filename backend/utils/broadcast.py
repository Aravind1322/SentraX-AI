"""
SentraX AI Backend — utils/broadcast.py
Thin async helper that pushes post-scan events to WebSocket channels.

Called from scan route handlers after every successful analysis.
Never raises — failures are logged silently so they never interrupt a scan response.
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from database import get_connection

_log = logging.getLogger("backend")


async def broadcast_scan_event(
    scan_type: str,
    target: str,
    score: int,
    label: str,
    threat_level: str,
    user_email: str = "anonymous@sentrax.ai",
):
    """
    After a successful scan, broadcast two events:
      1. "new_scan"      → channel "scans"     (recent-scan feed)
      2. "dashboard_update" → channel "dashboard" (live KPI metrics)
    """
    try:
        from utils.connection_manager import manager

        ts = datetime.utcnow().isoformat()

        # ── 1. new_scan event ─────────────────────────────────────────────────
        scan_payload: Dict[str, Any] = {
            "event":        "new_scan",
            "scan_type":    scan_type,
            "target":       target,
            "score":        score,
            "label":        label,
            "threat_level": threat_level,
            "analyst":      user_email,
            "timestamp":    ts,
        }
        await manager.broadcast(scan_payload, channel="scans")

        # ── 2. dashboard_update event ─────────────────────────────────────────
        # Pull fresh aggregated stats from SQLite to keep numbers authoritative
        stats = _get_dashboard_stats()
        dash_payload: Dict[str, Any] = {
            "event":     "dashboard_update",
            "timestamp": ts,
            **stats,
        }
        await manager.broadcast(dash_payload, channel="dashboard")

    except Exception as e:
        _log.warning(f"broadcast_scan_event failed silently: {e}")


def _get_dashboard_stats() -> Dict[str, Any]:
    """Compute live KPI metrics from scan_history for the dashboard channel."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*)                                      AS total_scans,
                    SUM(CASE WHEN threat_level='HIGH' THEN 1 ELSE 0 END) AS high_risk,
                    SUM(CASE WHEN threat_level='MEDIUM' THEN 1 ELSE 0 END) AS medium_risk,
                    SUM(CASE WHEN threat_level='LOW' THEN 1 ELSE 0 END) AS low_risk,
                    AVG(score)                                    AS avg_score,
                    MAX(score)                                    AS max_score
                FROM scan_history
            """)
            row = cursor.fetchone()
            if row:
                return {
                    "total_scans":  int(row["total_scans"] or 0),
                    "high_risk":    int(row["high_risk"] or 0),
                    "medium_risk":  int(row["medium_risk"] or 0),
                    "low_risk":     int(row["low_risk"] or 0),
                    "avg_score":    round(float(row["avg_score"] or 0), 1),
                    "max_score":    int(row["max_score"] or 0),
                }
    except Exception as e:
        _log.warning(f"_get_dashboard_stats failed: {e}")
    return {"total_scans": 0, "high_risk": 0, "medium_risk": 0,
            "low_risk": 0, "avg_score": 0.0, "max_score": 0}

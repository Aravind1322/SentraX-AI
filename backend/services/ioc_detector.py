"""
SentraX AI Backend — services/ioc_detector.py
Realtime Threat Detection Engine for matching scan values against watchlisted IOC signatures.
Now fully asynchronous to prevent deadlocks and connection blocking.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from database import get_connection, log_audit

_logger = logging.getLogger("backend")


async def check_and_trigger_ioc_alert(scan_type: str, scanned_value: str, current_user_email: str = "anonymous@sentrax.ai"):
    """
    Look up scanned_value in ioc_records.
    If match found:
      - Log "IOC Triggered" audit event.
      - Record the match in `ioc_triggers` history table.
      - Insert a new security alert into `alerts` if a duplicate Unacknowledged alert doesn't already exist.
      - Broadcast alert over WS channel `alerts`.
      - Broadcast update over WS channel `dashboard`.
    """
    try:
        match = None
        # 1. Match against active IOCs inside a short-lived connection
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, ioc_type, value, severity, source, confidence, description 
                FROM ioc_records 
                WHERE status = 'Active'
                """
            )
            iocs = cursor.fetchall()
            
            scanned_lower = str(scanned_value).lower()
            for ioc in iocs:
                ioc_val_lower = str(ioc["value"]).lower()
                ioc_type = str(ioc["ioc_type"]).lower()
                
                # Check match criteria:
                # - Exact match
                # - Domain suffix match for URL scans
                # - Substring containment for message body scans
                if ioc_val_lower == scanned_lower:
                    match = dict(ioc)
                    break
                elif ioc_type in ["domain", "tld"] and scan_type == "URL" and ioc_val_lower in scanned_lower:
                    match = dict(ioc)
                    break
                elif ioc_type == "keyword" and scan_type in ["SMS", "Fraud"] and ioc_val_lower in scanned_lower:
                    match = dict(ioc)
                    break
                elif ioc_type == "url" and ioc_val_lower in scanned_lower:
                    match = dict(ioc)
                    break
                    
        if not match:
            return
            
        # Found matching IOC!
        ioc_id = match["id"]
        ioc_value = match["value"]
        severity = match["severity"].upper()
        source = match["source"]
        description = match["description"]
        
        # Log audit immediately (handles opening and closing connection itself)
        log_audit(
            "ioc_triggered",
            f"IOC signature '{ioc_value}' (ID: {ioc_id}) triggered by {scan_type} scan: {scanned_value}"
        )
        
        dup_count = 0
        with get_connection() as conn:
            cursor = conn.cursor()
            # Record in ioc_triggers table
            cursor.execute(
                """
                INSERT INTO ioc_triggers (user_email, scanner, ioc_value, severity, action)
                VALUES (?, ?, ?, ?, ?)
                """,
                (current_user_email, scan_type, ioc_value, severity, "Alert Triggered")
            )
            
            # Check for duplicate Unacknowledged alerts for this value
            cursor.execute(
                "SELECT COUNT(*) FROM alerts WHERE description LIKE ? AND status = 'Unacknowledged'",
                (f"%'{ioc_value}'%",)
            )
            dup_count = cursor.fetchone()[0]
            conn.commit()
            
        if dup_count == 0:
            # Create a security alert
            title = f"🚨 {severity} THREAT DETECTED"
            desc = (
                f"Known malicious {match['ioc_type']} detected: '{ioc_value}'.\n"
                f"Severity: {severity}\n"
                f"Source: {source} (Threat Intelligence Database)\n"
                f"Description: {description}"
            )
            import re
            title = re.sub(r'<[^>]+>', '', str(title))
            desc = re.sub(r'<[^>]+>', '', str(desc))
            
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO alerts (title, description, severity, score)
                    VALUES (?, ?, ?, ?)
                    """,
                    (title, desc, severity, 95 if severity == "CRITICAL" else (85 if severity == "HIGH" else (60 if severity == "MEDIUM" else 30)))
                )
                conn.commit()
                
            # Broadcast over WS channel "alerts"
            from utils.connection_manager import manager
            alert_payload = {
                "event": "new_alert",
                "title": title,
                "description": desc,
                "severity": severity,
                "score": 95 if severity == "CRITICAL" else 85,
                "timestamp": datetime.now().isoformat()
            }
            await manager.broadcast(alert_payload, channel="alerts")
            
        # Broadcast dashboard update
        from utils.broadcast import _get_dashboard_stats
        stats = _get_dashboard_stats()
        dash_payload = {
            "event": "dashboard_update",
            "timestamp": datetime.now().isoformat(),
            **stats
        }
        from utils.connection_manager import manager
        await manager.broadcast(dash_payload, channel="dashboard")
        
    except Exception as e:
        _logger.warning(f"Error in check_and_trigger_ioc_alert: {e}")

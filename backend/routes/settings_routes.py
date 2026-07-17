"""
SentraX AI Backend — routes/settings_routes.py
Endpoints for managing tenant settings (thresholds, alert configs) and notification streams.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
from database import get_connection
from utils.security import get_current_user, RoleChecker

router = APIRouter()

# Schema definitions
class ThresholdsModel(BaseModel):
    high: int
    medium: int

class AlertsModel(BaseModel):
    email: bool
    slack: bool
    critical_only: bool

class SettingsUpdateModel(BaseModel):
    risk_thresholds: Optional[ThresholdsModel] = None
    alert_preferences: Optional[AlertsModel] = None
    export_settings: Optional[Dict[str, Any]] = None
    retention_period: Optional[str] = None


@router.get("/settings", summary="Get global security parameters and settings")
async def get_settings(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Retrieve security parameters, thresholds, and alert preferences.
    """
    settings = {}
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            for row in cursor.fetchall():
                key = row["key"]
                val = row["value"]
                if key in ["risk_thresholds", "alert_preferences", "export_settings"]:
                    try:
                        settings[key] = json.loads(val)
                    except:
                        settings[key] = val
                else:
                    settings[key] = val
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings: {str(e)}"
        )
    return settings


@router.put("/settings", summary="Update global settings (Admin only)")
async def update_settings(
    settings_update: SettingsUpdateModel,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Administrator"]))
):
    """
    Saves new risk thresholds, alert options, or data retention configurations.
    Enforced strictly for system Administrators.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            if settings_update.risk_thresholds is not None:
                val = json.dumps(settings_update.risk_thresholds.dict())
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('risk_thresholds', ?)", (val,))
                
            if settings_update.alert_preferences is not None:
                val = json.dumps(settings_update.alert_preferences.dict())
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('alert_preferences', ?)", (val,))
                
            if settings_update.export_settings is not None:
                val = json.dumps(settings_update.export_settings)
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('export_settings', ?)", (val,))
                
            if settings_update.retention_period is not None:
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('retention_period', ?)", (settings_update.retention_period,))
                
            conn.commit()
            return {"message": "Settings updated successfully"}
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )


@router.get("/notifications", summary="Retrieve recent threat notification alerts")
async def get_notifications(
    unread_only: bool = False,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve real-time generated security warnings and fraud indicators.
    """
    notifications = []
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, title, message, severity, is_read, timestamp FROM notifications"
            if unread_only:
                query += " WHERE is_read = 0"
            query += " ORDER BY timestamp DESC LIMIT 50"
            
            cursor.execute(query)
            for row in cursor.fetchall():
                notifications.append({
                    "id": row["id"],
                    "title": row["title"],
                    "message": row["message"],
                    "severity": row["severity"],
                    "is_read": bool(row["is_read"]),
                    "timestamp": row["timestamp"]
                })
    except Exception as e:
         raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notifications: {str(e)}"
        )
    return notifications


@router.put("/notifications/{notif_id}/read", summary="Mark notification alert as read")
async def read_notification(
    notif_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Updates a notification state to mark it as read.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
            conn.commit()
            return {"message": f"Notification {notif_id} marked as read"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database update failed: {str(e)}"
        )

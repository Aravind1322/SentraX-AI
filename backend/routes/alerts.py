"""
SentraX AI Backend — routes/alerts.py
Endpoints for querying and acknowledging real-time SOC security alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from services.alert_engine import AlertEngine
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any, Optional

router = APIRouter()


class AcknowledgeRequest(BaseModel):
    alert_id: int


@router.get("", summary="List SOC security alert logs")
async def list_alerts(
    status_filter: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve all SOC real-time security alerts."""
    return AlertEngine.get_all_alerts(status_filter)


@router.post("/acknowledge", summary="Acknowledge a SOC alert")
async def acknowledge_alert(
    request: AcknowledgeRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Marks a threat alert status as Acknowledged by an analyst."""
    analyst_name = current_user.get("full_name", "Security Analyst")
    ok = AlertEngine.acknowledge_alert(request.alert_id, analyst_name)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert log with ID {request.alert_id} not found"
        )
    return {"message": f"Alert {request.alert_id} acknowledged by {analyst_name}"}

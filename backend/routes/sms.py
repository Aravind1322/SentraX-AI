"""
SentraX AI Backend — routes/sms.py
SMS Shield endpoints.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from schemas import SMSScanRequest, SMSScanResponse
from services.sms_service import scan_sms
from utils.security import get_current_user, RoleChecker
from utils.broadcast import broadcast_scan_event
from typing import Dict, Any

router = APIRouter()


@router.get("/", summary="SMS API status")
async def sms_status():
    """Confirm the SMS Shield API is reachable."""
    return {
        "endpoint": "/api/sms",
        "status": "ready",
        "description": "SMS scam and fraud message detection.",
    }


@router.post("/scan", response_model=SMSScanResponse, summary="Analyse an SMS message")
async def scan_sms_endpoint(
    request: SMSScanRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Anonymous Analyst", "Security Analyst", "Administrator"]))
):
    """
    Submit an SMS message for scam analysis.

    Returns a classification label, risk score, detected keywords,
    confidence, and recommended actions.
    """
    result = scan_sms(request.message)
    from services.ioc_detector import check_and_trigger_ioc_alert
    background_tasks.add_task(
        broadcast_scan_event,
        "SMS", request.message[:80],
        result.get("score", 0), result.get("label", "Legitimate"),
        result.get("threat_level", "LOW"),
        current_user.get("email", "anonymous@sentrax.ai"),
    )
    background_tasks.add_task(
        check_and_trigger_ioc_alert,
        "SMS", request.message,
        current_user.get("email", "anonymous@sentrax.ai")
    )
    return SMSScanResponse(**result)

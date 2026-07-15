"""
SentraX AI Backend — routes/url.py
URL Intelligence endpoints.
Placeholder responses — business logic wired in a future sprint.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from schemas import URLScanRequest, URLScanResponse
from services.url_service import scan_url
from utils.security import get_current_user, RoleChecker
from utils.broadcast import broadcast_scan_event
from typing import Dict, Any

router = APIRouter()


@router.get("/", summary="URL API status")
async def url_status():
    """Confirm the URL Intelligence API is reachable."""
    return {
        "endpoint": "/api/url",
        "status": "ready",
        "description": "URL phishing and threat intelligence scanner.",
    }


@router.post("/scan", response_model=URLScanResponse, summary="Scan a URL")
async def scan_url_endpoint(
    request: URLScanRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Anonymous Analyst", "Security Analyst", "Administrator"]))
):
    """
    Submit a URL for threat analysis.

    Returns a classification label, threat score, reasons, confidence,
    and recommended actions.
    """
    result = await scan_url(request.url)
    from services.ioc_detector import check_and_trigger_ioc_alert
    background_tasks.add_task(
        broadcast_scan_event,
        "URL", request.url,
        result.get("score", 0), result.get("label", "Safe"),
        result.get("threat_level", "LOW"),
        current_user.get("email", "anonymous@sentrax.ai"),
    )
    background_tasks.add_task(
        check_and_trigger_ioc_alert,
        "URL", request.url,
        current_user.get("email", "anonymous@sentrax.ai")
    )
    return URLScanResponse(**result)

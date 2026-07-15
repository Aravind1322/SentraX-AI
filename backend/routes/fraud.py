"""
SentraX AI Backend — routes/fraud.py
Fraud Detection endpoints.
"""

from fastapi import APIRouter, Depends, BackgroundTasks
from schemas import FraudScanRequest, FraudScanResponse
from services.fraud_service import scan_fraud
from utils.security import get_current_user, RoleChecker
from utils.broadcast import broadcast_scan_event
from typing import Dict, Any

router = APIRouter()


@router.get("/", summary="Fraud API status")
async def fraud_status():
    """Confirm the Fraud Detection API is reachable."""
    return {
        "endpoint": "/api/fraud",
        "status": "ready",
        "description": "Transaction fraud and anomaly detection.",
    }


@router.post("/scan", response_model=FraudScanResponse, summary="Analyse a transaction")
async def scan_fraud_endpoint(
    request: FraudScanRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """
    Submit a transaction for fraud risk analysis.

    Returns a risk score, HIGH/MEDIUM/LOW classification,
    reasons for the score, confidence, and recommended actions.
    """
    result = scan_fraud(
        amount=request.amount,
        location=request.location,
        device=request.device,
        customer_id=request.customer_id,
    )
    background_tasks.add_task(
        broadcast_scan_event,
        "Fraud", f"${request.amount} @ {request.location}",
        result.get("risk_score", 0), result.get("status", "LOW RISK"),
        "HIGH" if result.get("risk_score", 0) >= 70 else ("MEDIUM" if result.get("risk_score", 0) >= 40 else "LOW"),
        current_user.get("email", "anonymous@sentrax.ai"),
    )
    from services.ioc_detector import check_and_trigger_ioc_alert
    background_tasks.add_task(
        check_and_trigger_ioc_alert,
        "Fraud", f"${request.amount} @ {request.location}",
        current_user.get("email", "anonymous@sentrax.ai")
    )
    return FraudScanResponse(**result)

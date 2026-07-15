"""
SentraX AI Backend — routes/employee.py
Employee Monitoring endpoints.
Placeholder responses — business logic wired in a future sprint.
"""

from fastapi import APIRouter, Depends
from schemas import EmployeeScanRequest, EmployeeScanResponse
from services.employee_service import scan_employee
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any

router = APIRouter()


@router.get("/", summary="Employee API status")
async def employee_status():
    """Confirm the Employee Monitoring API is reachable."""
    return {
        "endpoint": "/api/employee",
        "status": "ready",
        "description": "Insider threat and anomalous login detection.",
    }


@router.post("/scan", response_model=EmployeeScanResponse, summary="Analyse an employee login")
async def scan_employee_endpoint(
    request: EmployeeScanRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """
    Submit an employee login record for risk analysis.

    Returns a risk level, after-hours detection, confidence,
    and recommended actions.
    """
    result = scan_employee(
        employee=request.employee,
        login_time=request.login_time,
        department=request.department,
    )
    return EmployeeScanResponse(**result)

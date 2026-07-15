"""
SentraX AI Backend — services/employee_service.py
Employee Monitoring service layer.
"""

from typing import Dict, Any, Optional
from utils.helpers import parse_login_hour


def scan_employee(
    employee: str,
    login_time: str,
    department: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyse an employee login record for after-hours and anomaly indicators.
    """
    hour = parse_login_hour(login_time)
    
    if hour is not None and hour < 6:
        risk_level = "SUSPICIOUS"
        threat_level = "MEDIUM"
        reasons = [f"Login at {login_time} is outside business hours (after-hours access)"]
        recommendations = [
            "Verify login authenticity with the employee.",
            "Flag account for active session auditing.",
            "Review access logs for secondary anomalies.",
        ]
        confidence = 85
    else:
        risk_level = "NORMAL"
        threat_level = "LOW"
        reasons = []
        recommendations = [
            "Login falls within expected business hours.",
            "Continue routine employee activity monitoring.",
        ]
        confidence = 90

    from database import save_scan
    score = 75 if risk_level == "SUSPICIOUS" else 15
    input_data = f"Employee: {employee}, Login Time: {login_time}"
    if department:
        input_data += f", Department: {department}"
        
    save_scan(
        scan_type="Employee",
        input_data=input_data,
        score=score,
        label=risk_level,
        threat_level=threat_level,
        confidence=confidence,
        reasons=reasons,
        metrics={
            "employee": employee,
            "login_time": login_time,
            "department": department or "N/A"
        },
        recommendations=recommendations,
        metadata={
            "execution_time_ms": 8,
            "backend_version": "v1.0.0",
            "api_version": "v1",
            "engine_name": "Employee Monitoring Engine",
            "engine_version": "v1.0"
        }
    )

    return {
        "employee": employee,
        "login_time": login_time,
        "risk_level": risk_level,
        "reasons": reasons,
        "confidence": confidence,
        "threat_level": threat_level,
        "recommendations": recommendations,
    }

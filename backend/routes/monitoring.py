"""
SentraX AI Backend — routes/monitoring.py
Endpoint for monitoring backend health, database connectivity, and uptime.
"""

from fastapi import APIRouter
from config import APP_VERSION, ENABLE_URL_SCAN, ENABLE_SMS_SCAN, ENABLE_FRAUD_SCAN, ENABLE_EMPLOYEE_SCAN
from database import get_connection
from datetime import datetime

router = APIRouter()

# Keep track of service initialization time
START_TIME = datetime.now()


@router.get("/health", summary="Detailed health and monitoring probe")
async def check_health():
    """
    Returns comprehensive system health parameters: uptime, version,
    active services, API status, and SQLite database connectivity status.
    """
    # 1. Database status check
    db_status = "unhealthy"
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            row = cursor.fetchone()
            if row and row[0] == 1:
                db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # 2. Compute uptime
    uptime_delta = datetime.now() - START_TIME
    uptime_str = str(uptime_delta).split(".")[0]  # Remove microsecond part

    # 3. Compile active features
    active_services = []
    if ENABLE_URL_SCAN:
        active_services.append("URL Intelligence")
    if ENABLE_SMS_SCAN:
        active_services.append("SMS Shield")
    if ENABLE_FRAUD_SCAN:
        active_services.append("Fraud Detection")
    if ENABLE_EMPLOYEE_SCAN:
        active_services.append("Employee Monitoring")

    return {
        "status": "healthy",
        "api_status": "operational",
        "database_status": db_status,
        "version": APP_VERSION,
        "active_services": active_services,
        "uptime": uptime_str,
        "timestamp": datetime.now().isoformat()
    }

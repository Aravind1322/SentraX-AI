"""
SentraX AI Backend — routes/reports.py
Endpoints for generating and downloading comprehensive SOC Executive Reports (PDF, CSV, JSON).
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from services.enterprise_reporting_service import EnterpriseReportingService
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any

router = APIRouter()


@router.get("/json", summary="Get executive reports dataset in JSON format")
async def get_report_json(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve full SOC activity metrics in structured JSON format."""
    return EnterpriseReportingService.get_reporting_data()


@router.get("/csv", summary="Download executive reports summary in CSV format")
async def get_report_csv(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Generate and download a CSV file of SOC KPI indicators and top threats."""
    csv_data = EnterpriseReportingService.generate_csv_report()
    return StreamingResponse(
        io_bytes_from_str(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sentrax_soc_executive_report.csv"}
    )


@router.get("/pdf", summary="Download formatted Executive SOC Report in PDF format")
async def get_report_pdf(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Generate and download a formatted PDF threat intelligence executive status summary."""
    pdf_buffer = EnterpriseReportingService.generate_pdf_report()
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=sentrax_soc_executive_report.pdf"}
    )


def io_bytes_from_str(data_str: str):
    import io
    return io.BytesIO(data_str.encode("utf-8"))

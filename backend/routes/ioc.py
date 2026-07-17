"""
SentraX AI Backend — routes/ioc.py
Endpoints for managing Indicators of Compromise (IOC) signatures, metrics, and triggers.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from services.ioc_service import IOCService
from utils.security import get_current_user, RoleChecker

router = APIRouter()


class IOCRequest(BaseModel):
    ioc_type: str = Field(..., example="domain", description="domain, url, ip, email, phone, file_hash")
    value: str = Field(..., example="badactor-login.info")
    source: str = Field("Manual Entry", example="OTX API Feed")
    severity: str = Field("MEDIUM", example="HIGH")
    confidence: int = Field(80, ge=0, le=100, example=85)
    description: str = Field("Threat intelligence watchlist item", example="Phishing site domain")
    status: str = Field("Active", example="Active")


@router.post("", summary="Create an IOC signature record (Admin only)")
async def add_ioc(
    request: IOCRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Administrator"]))
):
    """Adds a new Indicator of Compromise signature."""
    res = IOCService.create_ioc(
        ioc_type=request.ioc_type,
        value=request.value,
        source=request.source,
        severity=request.severity,
        confidence=request.confidence,
        description=request.description,
        status=request.status
    )
    return res


@router.put("/{ioc_id}", summary="Update an IOC signature record (Admin only)")
async def update_ioc(
    ioc_id: int,
    request: IOCRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Administrator"]))
):
    """Updates an existing Indicator of Compromise signature."""
    success = IOCService.update_ioc(
        ioc_id=ioc_id,
        ioc_type=request.ioc_type,
        value=request.value,
        source=request.source,
        severity=request.severity,
        confidence=request.confidence,
        description=request.description,
        status=request.status
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IOC signature with ID {ioc_id} not found"
        )
    return {"message": "IOC signature updated successfully"}


@router.get("", summary="List all active IOC records")
async def list_iocs(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve the full list of Indicator of Compromise records."""
    return IOCService.get_all_iocs()


@router.delete("/{ioc_id}", summary="Delete an IOC record (Admin only)")
async def remove_ioc(
    ioc_id: int,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Administrator"]))
):
    """Removes an active Indicator of Compromise signature from watchlist."""
    deleted = IOCService.delete_ioc(ioc_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"IOC signature with ID {ioc_id} not found"
        )
    return {"message": f"IOC signature {ioc_id} deleted successfully"}


@router.post("/import", summary="Import a batch list of IOCs (Admin only)")
async def import_iocs(
    request: List[IOCRequest],
    current_user: Dict[str, Any] = Depends(RoleChecker(["Administrator"]))
):
    """Imports multiple IOC signatures."""
    imported_count = 0
    for ioc in request:
        res = IOCService.create_ioc(
            ioc_type=ioc.ioc_type,
            value=ioc.value,
            source=ioc.source,
            severity=ioc.severity,
            confidence=ioc.confidence,
            description=ioc.description,
            status=ioc.status
        )
        if "error" not in res:
            imported_count += 1
    return {"message": f"Successfully imported {imported_count} IOC signatures"}


@router.get("/export", summary="Export IOC signature records")
async def export_iocs(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Exports all IOC signature records as a downloadable payload."""
    records = IOCService.get_all_iocs()
    return records


@router.get("/triggers", summary="Get recent triggered matching events")
async def list_triggers(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Get chronological matches of threats against watchlist."""
    return IOCService.get_recent_triggers()


@router.get("/kpis", summary="Get stats summary for Threat Intel Dashboard")
async def get_kpis(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieves statistical counts for active threat intelligence records."""
    return IOCService.get_kpis()

"""
SentraX AI Backend — routes/cases.py
Endpoints for case management, timeline chronological updates, and evidence repositories.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from services.case_management_service import CaseManagementService
from utils.security import get_current_user, RoleChecker
from typing import Dict, Any, Optional

router = APIRouter()


class CaseCreateRequest(BaseModel):
    title: str = Field(..., example="Anomalous Login Investigation")
    description: str = Field(..., example="Investigating login from unknown geolocation at 3 AM")
    priority: str = Field("MEDIUM", example="HIGH")


class CaseUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


class EvidenceAddRequest(BaseModel):
    evidence_type: str = Field(..., example="JSON", description="PDF, CSV, TXT, JSON, Image")
    file_name: str = Field(..., example="login_logs.json")
    file_metadata: Optional[Dict[str, Any]] = None


@router.post("", summary="Create a new SOC case")
async def create_new_case(
    request: CaseCreateRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Initializes a new SOC case file and logs it to SQLite."""
    analyst_name = current_user.get("full_name", "System")
    return CaseManagementService.create_case(
        title=request.title,
        description=request.description,
        priority=request.priority,
        assigned_analyst=analyst_name
    )


@router.get("", summary="List all SOC cases")
async def list_cases(
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve the full list of SOC case files."""
    return CaseManagementService.get_all_cases()


@router.get("/{case_id}", summary="Get case details, evidence, and timeline")
async def get_case_details(
    case_id: int,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Viewer", "Security Analyst", "Administrator"]))
):
    """Retrieve detailed investigation files, timelines, and evidence links of a specific case."""
    case_data = CaseManagementService.get_case(case_id)
    if not case_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case file with ID {case_id} not found"
        )
    return case_data


@router.put("/{case_id}", summary="Update case details")
async def modify_case(
    case_id: int,
    request: CaseUpdateRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Updates status, priorities, or assignees of a case file."""
    analyst_name = current_user.get("full_name", "System")
    updated = CaseManagementService.update_case(
        case_id=case_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        status=request.status,
        assigned_analyst=analyst_name
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case file with ID {case_id} not found"
        )
    return {"message": f"Case file {case_id} updated successfully"}


@router.delete("/{case_id}", summary="Delete a case file")
async def remove_case(
    case_id: int,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Removes a case file and its related histories from database."""
    deleted = CaseManagementService.delete_case(case_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case file with ID {case_id} not found"
        )
    return {"message": f"Case file {case_id} deleted successfully"}


@router.post("/{case_id}/evidence", summary="Add evidence file metadata to case")
async def upload_evidence(
    case_id: int,
    request: EvidenceAddRequest,
    current_user: Dict[str, Any] = Depends(RoleChecker(["Security Analyst", "Administrator"]))
):
    """Links file hashes and metadata logs to a case's evidence repository."""
    return CaseManagementService.add_evidence(
        case_id=case_id,
        evidence_type=request.evidence_type,
        file_name=request.file_name,
        file_metadata=request.file_metadata
    )
